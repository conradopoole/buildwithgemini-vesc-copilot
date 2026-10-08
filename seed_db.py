#!/usr/bin/env python3
"""Seed script for VESC Onewheel Tuning & Troubleshooting Co-Pilot Firestore database.

IMPORTANT: The GCP Project ID is intentionally hardcoded as a string.
Do not read it from google.auth.default() or GOOGLE_CLOUD_PROJECT, because on
Agent Platform those can return the project number rather than the project ID.
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-5c449e223ad5"

HARDWARE_COMPONENTS = [
    {
        "id": "little-focer-v4",
        "name": "Little FOCer v4",
        "category": "controller",
        "voltage_range": "36V - 84V (10S - 20S)",
        "max_motor_current_a": 150,
        "supported_firmware": "VESC 6.02+",
        "features": ["IMU onboard (BMI270)", "Built-in Bluetooth", "Compact aluminum heatsink"],
        "common_issues": ["Thermal throttling under heavy climbs if heatsink contact is dry"],
    },
    {
        "id": "thor300",
        "name": "Thor 300 VESC",
        "category": "controller",
        "voltage_range": "36V - 100V (up to 24S)",
        "max_motor_current_a": 250,
        "supported_firmware": "VESC 6.02+",
        "features": ["Extreme high power", "CNC enclosure", "Heavy duty dual shunts"],
        "common_issues": ["Requires custom mounting / space constraints in stock XR rails"],
    },
    {
        "id": "hypercore-stock",
        "name": "Future Motion Hypercore 1148",
        "category": "motor",
        "voltage_range": "48V - 84V (15S - 20S)",
        "max_motor_current_a": 95,
        "supported_firmware": "N/A",
        "features": ["Standard XR motor", "Hall sensors", "Proven reliability"],
        "common_issues": ["Hall sensor plug wiring pinout reversal when pairing with non-FM VESC controllers"],
    },
    {
        "id": "cannoncore",
        "name": "CannonCore Motor",
        "category": "motor",
        "voltage_range": "60V - 100V (18S - 24S)",
        "max_motor_current_a": 130,
        "supported_firmware": "N/A",
        "features": ["High torque stator", "Thicker axle", "Heavy-duty phase leads"],
        "common_issues": ["Requires stator lube and heat dissipation monitoring on continuous hill climbs"],
    },
    {
        "id": "ennoid-xlite-v4",
        "name": "ENNOID-BMS XLITE-v4",
        "category": "bms",
        "voltage_range": "15S - 24S",
        "max_motor_current_a": 0,
        "supported_firmware": "VESC Tool CAN-bus integration",
        "features": ["Charge-only or discharge capable", "CAN bus reporting to VESC", "Individual cell balancing"],
        "common_issues": ["CAN termination resistor switch must be verified before enclosure seal"],
    },
]

TUNE_PRESETS = [
    {
        "id": "street-carver",
        "name": "Street Carver",
        "target_terrain": "Asphalt, pavement, smooth concrete",
        "kp": 28.0,
        "ki": 0.05,
        "kd": 0.32,
        "tiltback_duty_cycle": 0.82,
        "tiltback_angle_deg": 10.0,
        "field_weakening_current_a": 15.0,
        "description": "Smooth, flowing response with gentle pushback and extra top-end speed via mild field weakening.",
    },
    {
        "id": "trail-muncher",
        "name": "Trail Muncher",
        "target_terrain": "Dirt, roots, chunky rock, technical trails",
        "kp": 36.5,
        "ki": 0.08,
        "kd": 0.45,
        "tiltback_duty_cycle": 0.78,
        "tiltback_angle_deg": 12.0,
        "field_weakening_current_a": 0.0,
        "description": "Stiff and snappy pitch response to keep the nose up over roots and abrupt bumps. Zero field weakening for max low-end torque.",
    },
    {
        "id": "trick-park",
        "name": "Trick & Park Setup",
        "target_terrain": "Skateparks, curbs, nudges, drops",
        "kp": 32.0,
        "ki": 0.06,
        "kd": 0.38,
        "tiltback_duty_cycle": 0.85,
        "tiltback_angle_deg": 8.0,
        "field_weakening_current_a": 5.0,
        "description": "Balanced responsiveness for tail taps, bonks, and switch riding with rapid fault recovery.",
    },
]


def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    # 1. Seed hardware components
    comp_col = db.collection("hardware_components")
    print(f"Seeding {len(HARDWARE_COMPONENTS)} hardware components...")
    for comp in HARDWARE_COMPONENTS:
        doc_id = comp["id"]
        comp_col.document(doc_id).set(comp)
        print(f"  ✓ Seeded hardware component: {comp['name']} ({doc_id})")

    # 2. Seed tune presets
    tune_col = db.collection("tune_presets")
    print(f"Seeding {len(TUNE_PRESETS)} tune presets...")
    for tune in TUNE_PRESETS:
        doc_id = tune["id"]
        tune_col.document(doc_id).set(tune)
        print(f"  ✓ Seeded tune preset: {tune['name']} ({doc_id})")

    print("\nDatabase seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
