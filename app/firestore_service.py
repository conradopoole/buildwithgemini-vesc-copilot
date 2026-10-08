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

"""Firestore database client and CRUD functions for VESC Co-Pilot.

IMPORTANT: PROJECT_ID is hardcoded as a string because on Agent Platform,
reading from environment or auth tokens can resolve to the GCP Project Number,
which breaks Firestore API client calls.
"""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-5c449e223ad5"

_db: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    """Lazily initialize and return the Firestore client with hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def list_hardware_components(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List hardware components from Firestore, optionally filtered by category.

    Args:
        category: Optional category filter, e.g. 'controller', 'motor', 'bms', 'footpad'.

    Returns:
        A list of matching hardware component records.
    """
    db = get_db()
    col = db.collection("hardware_components")
    if category:
        query = col.where("category", "==", category.lower().strip())
        docs = query.stream()
    else:
        docs = col.stream()

    components = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        components.append(data)
    return components


def get_hardware_component(component_id: str) -> Dict[str, Any]:
    """Fetch details of a single hardware component by ID.

    Args:
        component_id: Unique ID of the component (e.g. 'little-focer-v4', 'thor300').

    Returns:
        The component details dictionary or error info if not found.
    """
    db = get_db()
    doc_ref = db.collection("hardware_components").document(component_id.strip())
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Hardware component '{component_id}' not found in database."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_hardware_component(
    component_id: str,
    name: str,
    category: str,
    voltage_range: str,
    max_motor_current_a: float,
    supported_firmware: str,
    features: List[str],
    common_issues: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add or update a verified hardware component in Firestore.

    Args:
        component_id: Unique slug identifier for the component (e.g. 'spintend-ubox-100v').
        name: Full product display name.
        category: Component category ('controller', 'motor', 'bms', 'footpad', etc.).
        voltage_range: Supported voltage range (e.g. '48V - 84V (12S - 20S)').
        max_motor_current_a: Maximum continuous or burst motor current in Amps.
        supported_firmware: Target firmware compatibility (e.g. 'VESC 6.02+').
        features: Key features or specs.
        common_issues: Known troubleshooting quirks or thermal considerations.

    Returns:
        Status message with the saved component details.
    """
    db = get_db()
    data = {
        "id": component_id.strip(),
        "name": name.strip(),
        "category": category.strip().lower(),
        "voltage_range": voltage_range.strip(),
        "max_motor_current_a": float(max_motor_current_a),
        "supported_firmware": supported_firmware.strip(),
        "features": features,
        "common_issues": common_issues or [],
    }
    db.collection("hardware_components").document(component_id.strip()).set(data)
    return {"status": "success", "message": f"Hardware component '{name}' saved successfully.", "component": data}


def list_tune_presets(target_terrain: Optional[str] = None) -> List[Dict[str, Any]]:
    """List tune presets from Firestore.

    Args:
        target_terrain: Optional keyword to filter presets by riding terrain.

    Returns:
        List of matching tune preset dictionaries.
    """
    db = get_db()
    docs = db.collection("tune_presets").stream()
    presets = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if target_terrain:
            terrain_kw = target_terrain.lower()
            if terrain_kw not in data.get("target_terrain", "").lower() and terrain_kw not in data.get("name", "").lower():
                continue
        presets.append(data)
    return presets


def save_tune_preset(
    preset_id: str,
    name: str,
    target_terrain: str,
    kp: float,
    ki: float,
    kd: float,
    tiltback_duty_cycle: float,
    tiltback_angle_deg: float,
    field_weakening_current_a: float,
    description: str,
) -> Dict[str, Any]:
    """Save or update a custom tune preset in Firestore.

    Args:
        preset_id: Unique slug for the tune preset (e.g. 'aggressive-trail-v2').
        name: Name of the preset (e.g. 'Aggressive Trail 2.0').
        target_terrain: Ideal terrain type (e.g. 'Technical mountain trails').
        kp: Proportional PID balance gain.
        ki: Integral PID balance gain.
        kd: Derivative PID balance gain.
        tiltback_duty_cycle: Duty cycle threshold where pushback engages (e.g. 0.80 for 80%).
        tiltback_angle_deg: Pushback elevation angle in degrees.
        field_weakening_current_a: Field weakening current in Amps.
        description: Guidance on rider weight and handling characteristics.

    Returns:
        Status message with saved preset data.
    """
    db = get_db()
    data = {
        "id": preset_id.strip(),
        "name": name.strip(),
        "target_terrain": target_terrain.strip(),
        "kp": float(kp),
        "ki": float(ki),
        "kd": float(kd),
        "tiltback_duty_cycle": float(tiltback_duty_cycle),
        "tiltback_angle_deg": float(tiltback_angle_deg),
        "field_weakening_current_a": float(field_weakening_current_a),
        "description": description.strip(),
    }
    db.collection("tune_presets").document(preset_id.strip()).set(data)
    return {"status": "success", "message": f"Tune preset '{name}' saved successfully.", "preset": data}
