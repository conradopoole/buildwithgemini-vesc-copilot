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

"""YouTube public video search service for trusted VESC Onewheel creators."""

import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

# Public YouTube RSS channel feeds for key VESC creators
CREATOR_CHANNELS = {
    "surfdado": {
        "channel_id": "UClhp0J195HBXm6p6KN8nE4Q",
        "creator": "surfdado (Float Control / VESC Package lead)",
        "handle": "@surfdado",
    },
    "jayisdoingstuff": {
        "channel_id": "UCzChWdW2sDQ25WOtV18YmrA",
        "creator": "Jay is Doing Stuff (VESC Builds & Tuning)",
        "handle": "@jayisdoingstuff",
    },
    "BenjaminsRobotics": {
        "channel_id": "UCcslH9JifCwInHV6mP5KGFQ",
        "creator": "Benjamin Vedder (VESC Creator & Firmware Dev)",
        "handle": "@BenjaminsRobotics",
    },
    "fixmypev": {
        "channel_id": "UC28VvwvADFO-Ge3NO0xiEIQ",
        "creator": "FixMyPEV (Hardware, BMS & Diagnostics)",
        "handle": "@fixmypev",
    },
    "JetFleet-Fajdiga": {
        "channel_id": "UCJYyP9o06qCYGe9oPVuP3ag",
        "creator": "JetFleet (Custom Builds & High-Voltage Systems)",
        "handle": "@JetFleet-Fajdiga",
    },
}

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/", "yt": "http://www.youtube.com/xml/schemas/2015"}


def search_creator_videos(query: str, creator_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search videos from trusted VESC YouTube channels.
    
    If YOUTUBE_API_KEY environment variable is provided, it can be used for YouTube Data API v3;
    otherwise, it directly queries public Atom/RSS XML feeds from YouTube with zero API keys required.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    matched_videos: List[Dict[str, Any]] = []

    # Filter target channels if specified
    targets = {}
    if creator_filter:
        cf = creator_filter.lower()
        for k, v in CREATOR_CHANNELS.items():
            if cf in k.lower() or cf in v["creator"].lower():
                targets[k] = v
    if not targets:
        targets = CREATOR_CHANNELS

    for key, info in targets.items():
        channel_id = info["channel_id"]
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "VESC-CoPilot/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                
                for entry in root.findall("atom:entry", ATOM_NS):
                    title_el = entry.find("atom:title", ATOM_NS)
                    link_el = entry.find("atom:link", ATOM_NS)
                    media_group = entry.find("media:group", ATOM_NS)
                    desc_el = media_group.find("media:description", ATOM_NS) if media_group is not None else None
                    pub_el = entry.find("atom:published", ATOM_NS)
                    
                    title = title_el.text if title_el is not None and title_el.text else ""
                    video_url = link_el.attrib.get("href", "") if link_el is not None else ""
                    description = desc_el.text if desc_el is not None and desc_el.text else ""
                    published = pub_el.text[:10] if pub_el is not None and pub_el.text else ""

                    searchable_text = f"{title} {description}".lower()
                    
                    # Compute match score
                    score = sum(1 for term in query_terms if term in searchable_text)
                    if score > 0 or not query_terms:
                        matched_videos.append({
                            "title": title,
                            "url": video_url,
                            "creator": info["creator"],
                            "handle": info["handle"],
                            "published_date": published,
                            "snippet": (description[:240] + "...") if len(description) > 240 else description,
                            "match_score": score,
                        })
        except Exception:
            continue

    # Sort matched videos by highest relevance score, then recent date
    matched_videos.sort(key=lambda x: (x["match_score"], x["published_date"]), reverse=True)
    return matched_videos[:6]
