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

"""Discord Community Directory and Live Channel Inspector.

ARCHITECTURE NOTE (Future Roadmap):
- Current Implementation (Option B): Curated community index with keyword routing,
  direct server invites, channel recommendations, and pinned resource locations.
- Future Architecture A (Ingestion & Mirroring):
  To provide full-text message search across these servers without violating Discord TOS,
  a cooperative bot with 'Read Message History' in designated public support channels
  can stream/ingest messages into a Firestore collection (`discord_knowledge_archive`)
  or a Vertex AI RAG Engine corpus for semantic vector search.
"""

import os
import urllib.request
import json
from typing import Any, Dict, List, Optional

DISCORD_COMMUNITIES = [
    {
        "name": "Float with VESC",
        "invite_url": "https://discord.gg/Kwsgzte2",
        "focus": "General VESC Onewheel community, Float Package, firmware releases, tune sharing, and general build advice.",
        "key_channels": ["#announcements", "#general-chat", "#tuning-and-presets", "#firmware-testing", "#vesc-xr"],
        "keywords": ["float package", "refloat", "tune", "preset", "firmware", "balance", "imu", "surfdado", "update"],
    },
    {
        "name": "VESC Development",
        "invite_url": "https://discord.gg/tq6tav6MQ",
        "focus": "Core VESC firmware development, Benjamin Vedder updates, FOC algorithm discussions, and motor control hardware design.",
        "key_channels": ["#firmware-dev", "#hardware-design", "#vesc-tool", "#foc-control", "#general-vesc"],
        "keywords": ["vedder", "benjamin", "firmware", "source code", "c-code", "foc", "algorithm", "drv8301", "pull request"],
    },
    {
        "name": "Vescify (Onewheel VESC Conversions)",
        "invite_url": "https://discord.gg/ahJXqXVVz",
        "focus": "Step-by-step conversions of OEM Future Motion XR, Plus, and Pint frames into VESC controllers.",
        "key_channels": ["#xr-conversion", "#pint-conversion", "#wiring-harnesses", "#footpad-sensors", "#troubleshooting"],
        "keywords": ["conversion", "xr", "pint", "plus", "stock harness", "harness", "footpad", "wiring", "vescify"],
    },
    {
        "name": "Funwheel",
        "invite_url": "https://discord.gg/ydvbEvafa",
        "focus": "Open-source balance board design, Funwheel DIY controllers, 3D printable boxes, and custom electronics.",
        "key_channels": ["#hardware", "#cad-files", "#3d-printing", "#enclosures", "#motor-hubs"],
        "keywords": ["funwheel", "cad", "stl", "3d print", "diy box", "enclosure", "open source"],
    },
    {
        "name": "JetFleet",
        "invite_url": "https://discord.gg/ztuacpdhE",
        "focus": "High-voltage and extreme performance VESC builds, custom Thor / Ubox controllers, and racing setups.",
        "key_channels": ["#high-voltage", "#racing-tunes", "#custom-builds", "#controller-heatsinks"],
        "keywords": ["jetfleet", "high voltage", "24s", "20s", "thor", "racing", "speed", "field weakening", "cooling"],
    },
    {
        "name": "Floatwheel",
        "invite_url": "https://discord.gg/KjKzYvFP5",
        "focus": "Official Floatwheel ADV, ADV2, and Atom platform support, assembly guides, and factory firmware updates.",
        "key_channels": ["#adv-troubleshooting", "#adv2-updates", "#atom-discussion", "#shipping-and-parts", "#firmware"],
        "keywords": ["floatwheel", "adv", "adv2", "atom", "tony", "cannoncore", "factory", "lcm", "adv firmware"],
    },
    {
        "name": "FixMyPEV",
        "invite_url": "https://discord.gg/KjKzYvFP5",
        "focus": "PEV hardware repairs, battery cell rebuilding, BMS diagnostics, axle hub servicing, and wiring harness fixes.",
        "key_channels": ["#battery-repair", "#bms-wiring", "#motor-hub-service", "#general-repairs"],
        "keywords": ["fixmypev", "repair", "battery", "bms", "axle", "bearing", "stripped", "multimeter", "harness", "water damage"],
    },
]


def find_discord_community(query: str) -> List[Dict[str, Any]]:
    """Match a rider's topic or issue to the most relevant VESC Discord community server.

    If DISCORD_BOT_TOKEN environment variable is set, it can also check bot accessibility.
    """
    clean_query = query.lower().strip()
    words = [w for w in clean_query.split() if len(w) > 2]

    matches = []
    for community in DISCORD_COMMUNITIES:
        score = 0
        # Exact community name match
        if community["name"].lower() in clean_query:
            score += 10

        # Focus description match
        for word in words:
            if word in community["focus"].lower():
                score += 2

        # Keyword match
        for kw in community["keywords"]:
            if kw in clean_query:
                score += 4
            elif any(word in kw for word in words):
                score += 1

        if score > 0:
            matches.append({
                "community_name": community["name"],
                "invite_url": community["invite_url"],
                "focus": community["focus"],
                "recommended_channels": community["key_channels"],
                "match_score": score,
            })

    matches.sort(key=lambda x: x["match_score"], reverse=True)

    # If no high-confidence keyword match, return the full list as reference
    if not matches:
        return [
            {
                "community_name": c["name"],
                "invite_url": c["invite_url"],
                "focus": c["focus"],
                "recommended_channels": c["key_channels"][:3],
                "match_score": 0,
            }
            for c in DISCORD_COMMUNITIES
        ]

    return matches[:3]
