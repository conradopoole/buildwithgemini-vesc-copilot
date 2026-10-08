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

"""Service to search community knowledge, guides, and troubleshooting threads on pev.dev."""

import json
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List


def search_pev_forum(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search pev.dev discussions, build guides, and troubleshooting posts.

    Discourse search on pev.dev works best with single keywords or core terms
    (e.g., 'focer', 'imu', 'refloat', 'motor', 'bms', 'voltage', 'hall').

    Args:
        query: The search term or issue (e.g. 'Little FOCer IMU calibration', 'DRV fault', 'Refloat tune').
        max_results: Max number of discussion threads to return (default 5).

    Returns:
        List of matching threads with title, URL, reply count, and excerpt snippet.
    """
    clean_query = query.strip()
    if not clean_query:
        return []

    # Clean query into high-signal keywords for Discourse search
    # Filter out common stop words
    stop_words = {"the", "a", "an", "and", "or", "for", "with", "how", "what", "is", "my", "to", "on", "in", "code"}
    words = [re.sub(r"[^\w]", "", w) for w in clean_query.split()]
    keywords = [w for w in words if w.lower() not in stop_words and len(w) > 2]

    # Try full query first, then fall back to primary keywords
    search_attempts = []
    if keywords:
        search_attempts.append(" ".join(keywords[:3]))
        for kw in keywords[:2]:
            if kw not in search_attempts:
                search_attempts.append(kw)
    else:
        search_attempts.append(clean_query)

    for attempt in search_attempts:
        encoded_query = urllib.parse.quote(attempt)
        url = f"https://pev.dev/search.json?q={encoded_query}"

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (VESC-CoPilot; DIY Onewheel Knowledge Assistant)",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                if response.status != 200:
                    continue
                data = json.loads(response.read().decode("utf-8"))

            topics_map = {t.get("id"): t for t in data.get("topics", [])}
            posts = data.get("posts", [])

            results = []
            seen_topics = set()

            for post in posts:
                topic_id = post.get("topic_id")
                if topic_id in seen_topics:
                    continue
                seen_topics.add(topic_id)

                topic = topics_map.get(topic_id, {})
                title = topic.get("title") or "pev.dev Discussion"
                slug = topic.get("slug") or f"topic-{topic_id}"
                thread_url = f"https://pev.dev/t/{slug}/{topic_id}"
                blurb = post.get("blurb", "") or topic.get("excerpt", "")

                results.append({
                    "title": title,
                    "url": thread_url,
                    "posts_count": topic.get("posts_count", 1),
                    "views": topic.get("views", 0),
                    "excerpt": blurb[:280] if len(blurb) > 280 else blurb,
                })

                if len(results) >= max_results:
                    break

            if results:
                return results

        except Exception:
            continue

    return []
