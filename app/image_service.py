# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Service for generating VESC diagrams and images and publishing to GCS."""

import re
import time
import uuid
from typing import Dict, Any, Optional

import google.genai as genai
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-04-5c449e223ad5"
PUBLIC_BUCKET_NAME = "bwg3-qwiklabs-gcp-04-5c449e223ad5"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"

# Initialize clients once
_genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
_storage_client = storage.Client(project=PROJECT_ID)


def generate_and_upload_image(prompt: str, item_title: str) -> Dict[str, Any]:
    """Generates an image/diagram using gemini-3.1-flash-lite-image and uploads to GCS.

    Args:
        prompt: Detailed visual prompt describing the hardware diagram, wiring, or board component.
        item_title: Short title or identifier for naming the artifact and storage object.

    Returns:
        dict with:
            - 'bytes': raw image bytes
            - 'mime_type': image mime type (e.g. image/jpeg)
            - 'filename': unique artifact filename
            - 'public_url': public HTTPS URL on Cloud Storage
            - 'description': description of the generated image
    """
    # 1. Generate image using gemini-3.1-flash-lite-image
    response = _genai_client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    image_bytes = None
    mime_type = "image/jpeg"

    for candidate in response.candidates:
        if not candidate.content or not candidate.content.parts:
            continue
        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break
        if image_bytes:
            break

    if not image_bytes:
        raise RuntimeError("No image data returned from gemini-3.1-flash-lite-image")

    # Determine extension
    ext = "jpg"
    if "png" in mime_type:
        ext = "png"
    elif "webp" in mime_type:
        ext = "webp"

    safe_title = re.sub(r"[^a-zA-Z0-9_\-]", "_", item_title.lower()).strip("_")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{safe_title}_{unique_id}.{ext}"

    # 2. Upload image bytes directly to GCS bucket
    bucket = _storage_client.bucket(PUBLIC_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{PUBLIC_BUCKET_NAME}/{filename}"

    return {
        "bytes": image_bytes,
        "mime_type": mime_type,
        "filename": filename,
        "public_url": public_url,
        "description": f"Generated diagram/image for: {item_title}",
    }
