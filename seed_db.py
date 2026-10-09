#!/usr/bin/env python3
"""Seed script for VESC Onewheel Tuning & Troubleshooting Co-Pilot Firestore database.

Includes modern flagship VESC controllers from Fungineers, Floatwheel, JetFleet, and ENNOID,
alongside legacy controllers, motors, and BMS options.

IMPORTANT: The GCP Project ID is intentionally hardcoded as a string.
Do not read it from google.auth.default() or GOOGLE_CLOUD_PROJECT, because on
Agent Platform those can return the project number rather than the project ID.
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-5c449e223ad5"

HARDWARE_COMPONENTS = [
    # Modern Fungineers Flagship Controllers
    {
        "id": "thor400",
        "name": "Fungineers Thor400",
        "category": "controller",
        "manufacturer": "Fungineers",
        "website": "https://fungineers.us/",
        "voltage_range": "60V - 134V (18S - 32S Li-ion)",
        "max_motor_current_a": 400,
        "recommended_motor_current_a": 300,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "500A OnSemi Dual Cool (TDFNW8) FETs",
            "Onboard ESP32 with Wi-Fi & Bluetooth",
            "134V max operating voltage (32S capable)",
            "Integrated buzzer & 12V LED light outputs (5A buck)",
            "Compact 2-PCB footprint (80 x 60 x 25 mm)",
        ],
        "common_issues": [
            "Exposed MOSFET power PCB requires careful mounting with thermal grease/gap pad to prevent enclosure shorting",
            "Requires motors with phase inductance >= 10µH",
        ],
    },
    {
        "id": "thor301",
        "name": "Fungineers Thor301",
        "category": "controller",
        "manufacturer": "Fungineers",
        "website": "https://fungineers.us/",
        "voltage_range": "36V - 84V (10S - 20S)",
        "max_motor_current_a": 300,
        "recommended_motor_current_a": 250,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "IMS (Insulated Metal Substrate) aluminum power PCB",
            "Direct FET cooling without fragile thermal pads",
            "Onboard ESP32 with Wi-Fi & Bluetooth",
            "Direct replacement for Thor300 with quieter DC-DC and upgraded layout",
            "Integrated buzzer, 12V light outputs, and CAN bus",
        ],
        "common_issues": [
            "Tight fit in non-Fungineers controller boxes without 3D-printed riser lid",
        ],
    },
    {
        "id": "zeus400",
        "name": "Fungineers Zeus400",
        "category": "controller",
        "manufacturer": "Fungineers",
        "website": "https://fungineers.us/",
        "voltage_range": "60V - 134V (18S - 32S)",
        "max_motor_current_a": 400,
        "recommended_motor_current_a": 320,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "Ultra high-voltage high-torque balance platform",
            "Dual Cool MOSFET power stage",
            "Onboard ESP32, CAN bus, and 12V aux buck",
        ],
        "common_issues": [
            "Thermal dissipation requires direct chassis rail heatsinking on sustained 32S hill climbs",
        ],
    },

    # Modern Floatwheel Drop-In Kits & Flagship Controllers
    {
        "id": "floatwheel-gtv-kit",
        "name": "Floatwheel GTV Kit",
        "category": "controller",
        "manufacturer": "Floatwheel",
        "website": "https://floatwheel.co/",
        "voltage_range": "60V - 75.6V (18S Onewheel GT battery)",
        "max_motor_current_a": 220,
        "recommended_motor_current_a": 160,
        "supported_firmware": "VESC 6.02+ (Refloat / Float Package)",
        "features": [
            "Drop-in VESC conversion kit for Onewheel GT / XR Classic",
            "Boosts stock GT from 2,800W up to 4,200W+ (up to 5,200W with MTE hub)",
            "Direct plug-and-play with stock GT footpad, motor, and battery harness",
            "Unlocks right-to-repair and full VESC Tool / Refloat tuning",
        ],
        "common_issues": [
            "Ensure CAN bus wiring to stock BMS is properly terminated or running in bypass mode",
            "Must calibrate IMU orientation after installing inside GT front box",
        ],
    },
    {
        "id": "floatwheel-pintv-kit",
        "name": "Floatwheel PintV Kit",
        "category": "controller",
        "manufacturer": "Floatwheel",
        "website": "https://floatwheel.co/",
        "voltage_range": "48V - 63V (15S Pint / Pint X battery)",
        "max_motor_current_a": 160,
        "recommended_motor_current_a": 120,
        "supported_firmware": "VESC 6.02+ (Refloat / Float Package)",
        "features": [
            "Drop-in VESC conversion kit for Onewheel Pint and Pint X",
            "Eliminates the stock 15 mph pushback wall with safe tiltback profiles",
            "Plug-and-play connectors for stock Pint harness and footpad",
            "Full VESC Tool telemetry, Bluetooth tuning, and Refloat support",
        ],
        "common_issues": [
            "Pint battery capacity is smaller, monitor battery current limit (e.g. 30A-35A max)",
        ],
    },
    {
        "id": "floatwheel-adv500",
        "name": "Floatwheel ADV500 Controller",
        "category": "controller",
        "manufacturer": "Floatwheel",
        "website": "https://floatwheel.co/",
        "voltage_range": "60V - 84V (18S - 20S2P Samsung 50S)",
        "max_motor_current_a": 500,
        "recommended_motor_current_a": 250,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "Flagship ESC for Floatwheel ADV2 balance boards",
            "Over-engineered heatsink keeps ESC at ~41C during heavy 80C motor loads",
            "VESC Express integration with micro-SD card logging and high-speed BLE",
            "Native CAN Smart BMS telemetry with per-cell monitoring & pushback safety",
        ],
        "common_issues": [
            "Proprietary form factor designed specifically for Floatwheel ADV/ADV2 chassis",
        ],
    },
    {
        "id": "floatwheel-adv200",
        "name": "Floatwheel ADV200 Controller",
        "category": "controller",
        "manufacturer": "Floatwheel",
        "website": "https://floatwheel.co/",
        "voltage_range": "60V - 84V (18S - 20S)",
        "max_motor_current_a": 200,
        "recommended_motor_current_a": 150,
        "supported_firmware": "VESC 6.02+",
        "features": [
            "High-reliability mid-power ESC for Floatwheel ADV gen 1 boards",
            "Full CAN Smart BMS integration",
            "Robust balance algorithms with Refloat preset support",
        ],
        "common_issues": [
            "Earlier gen firmware required manual motor hall calibration on initial setup",
        ],
    },

    # Modern JetFleet High-Voltage & GaN Controllers
    {
        "id": "jetfleet-f6",
        "name": "JetFleet F6",
        "category": "controller",
        "manufacturer": "JetFleet",
        "website": "https://jetfleetstore.com/",
        "voltage_range": "24V - 140V (up to 32S Li-ion)",
        "max_motor_current_a": 180,
        "recommended_motor_current_a": 140,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "Roll-to-start instant power-on technology (no physical power button needed)",
            "Vampire Sleep Mode (~12µA ultra-low standby drain)",
            "Compact aluminum package (80.5 x 60 x 27 mm, 180g)",
            "High-speed 832Hz IMU (LSM6DS3TR-C) and dual USB-C ports",
            "3 addressable RGB LED channels, locking JST-GH connectors",
        ],
        "common_issues": [
            "Always verify locking JST-GH latches are fully engaged before sealing controller box",
        ],
    },
    {
        "id": "jetfleet-g18",
        "name": "JetFleet G18",
        "category": "controller",
        "manufacturer": "JetFleet",
        "website": "https://jetfleetstore.com/",
        "voltage_range": "40V - 168V (Ultra High Voltage)",
        "max_motor_current_a": 250,
        "recommended_motor_current_a": 200,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "Cutting-edge Gallium Nitride (eGaN) power stages",
            "Ultra-high switching frequencies with near-zero switching losses",
            "168V maximum operating ceiling for extreme custom multi-series builds",
            "Ultra-smooth FOC motor control and high thermal efficiency",
        ],
        "common_issues": [
            "Requires GaN-compatible deadtime configurations in VESC Tool",
            "High voltage (100V+) demands strict wiring insulation and anti-spark protection",
        ],
    },

    # Modern ENNOID High-Voltage ESC Series
    {
        "id": "ennoid-mk8",
        "name": "ENNOID ESC MK8",
        "category": "controller",
        "manufacturer": "ENNOID",
        "website": "https://www.ennoid.me/",
        "voltage_range": "36V - 150V (up to 36S)",
        "max_motor_current_a": 200,
        "recommended_motor_current_a": 150,
        "supported_firmware": "VESC 6.02+",
        "features": [
            "150V heavy-duty VESC architecture",
            "Seamless CAN bus integration with ENNOID-BMS XLITE series",
            "Precision phase current shunts with low temperature drift",
        ],
        "common_issues": [
            "Requires adequate heat sinking to chassis when driven above 120A continuous",
        ],
    },
    {
        "id": "ennoid-mk8-pro",
        "name": "ENNOID ESC MK8 Pro",
        "category": "controller",
        "manufacturer": "ENNOID",
        "website": "https://www.ennoid.me/",
        "voltage_range": "36V - 150V (up to 36S)",
        "max_motor_current_a": 280,
        "recommended_motor_current_a": 200,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "150V Pro high-current power stage with upgraded MOSFET array",
            "Expanded peripheral connectivity and lighting module support",
            "Advanced telemetry and external sensor inputs",
        ],
        "common_issues": [
            "Ensure CAN termination switch is properly configured when chaining with ENNOID BMS",
        ],
    },
    {
        "id": "ennoid-mk9-pro",
        "name": "ENNOID ESC MK9 Pro",
        "category": "controller",
        "manufacturer": "ENNOID",
        "website": "https://www.ennoid.me/",
        "voltage_range": "48V - 200V (Extreme High Voltage)",
        "max_motor_current_a": 300,
        "recommended_motor_current_a": 220,
        "supported_firmware": "VESC 6.02+ / VESC Express",
        "features": [
            "200V max operating rating for extreme cell count and micro-EV platforms",
            "Heavy CNC heatsink casing with high-current copper busbars",
            "Integrated high-voltage DC-DC aux outputs",
            "Full VESC Tool FOC precision control",
        ],
        "common_issues": [
            "Extreme high-voltage safety precautions mandatory during assembly and charging",
        ],
    },

    # Classic / Proven Controllers
    {
        "id": "little-focer-v4",
        "name": "Little FOCer v4",
        "category": "controller",
        "manufacturer": "Shaman Systems",
        "website": "https://pev.dev",
        "voltage_range": "36V - 84V (10S - 20S)",
        "max_motor_current_a": 150,
        "recommended_motor_current_a": 85,
        "supported_firmware": "VESC 6.02+",
        "features": ["IMU onboard (BMI270)", "Built-in Bluetooth", "Compact aluminum heatsink"],
        "common_issues": ["Thermal throttling under heavy climbs if heatsink contact is dry"],
    },
    {
        "id": "thor300",
        "name": "Thor 300 VESC",
        "category": "controller",
        "manufacturer": "Fungineers",
        "website": "https://fungineers.us/",
        "voltage_range": "36V - 100V (up to 24S)",
        "max_motor_current_a": 250,
        "recommended_motor_current_a": 180,
        "supported_firmware": "VESC 6.02+",
        "features": ["Predecessor to Thor301", "CNC enclosure", "Heavy duty dual shunts"],
        "common_issues": ["Replaced by Thor301 with quieter DC-DC and improved aluminum base"],
    },

    # Verified Motors
    {
        "id": "hypercore-stock",
        "name": "Future Motion Hypercore 1148",
        "category": "motor",
        "manufacturer": "Future Motion",
        "website": "https://pev.dev",
        "voltage_range": "48V - 84V (15S - 20S)",
        "max_motor_current_a": 95,
        "recommended_motor_current_a": 80,
        "supported_firmware": "N/A",
        "features": ["Standard XR motor", "Hall sensors", "Proven reliability"],
        "common_issues": ["Hall sensor plug wiring pinout reversal when pairing with non-FM VESC controllers"],
    },
    {
        "id": "cannoncore",
        "name": "Fungineers Superflux / CannonCore Motor",
        "category": "motor",
        "manufacturer": "Fungineers",
        "website": "https://fungineers.us/",
        "voltage_range": "60V - 120V (18S - 28S)",
        "max_motor_current_a": 160,
        "recommended_motor_current_a": 120,
        "supported_firmware": "N/A",
        "features": ["Curved N52SH magnets", "Thick stator laminations", "High torque per amp", "Cooling fins"],
        "common_issues": ["Heavier motor hub requires sturdy footpad mounting and drop brackets"],
    },

    # Smart BMS Solutions
    {
        "id": "ennoid-xlite-v4",
        "name": "ENNOID-BMS XLITE-v4",
        "category": "bms",
        "manufacturer": "ENNOID",
        "website": "https://www.ennoid.me/",
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
