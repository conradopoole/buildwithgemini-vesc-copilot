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

"""VESC Fault Diagnostic Knowledge Base & Triage Engine."""

from typing import Any, Dict, List, Optional

VESC_FAULT_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "FAULT_CODE_DRV": {
        "fault_name": "FAULT_CODE_DRV",
        "aliases": ["drv", "drv8301", "drv fault", "gate driver fault", "3 blinks"],
        "severity": "CRITICAL",
        "description": "Gate driver IC reported a hardware fault condition (over-temperature, charge pump undervoltage, or short-circuit protection triggered).",
        "primary_causes": [
            "Damaged MOSFET phase transistor (gate-to-source or drain-to-source short)",
            "Motor phase wire pinched or shorted to motor stator/axle",
            "Severe inductive voltage spike during aggressive braking at full battery charge",
            "Failed DRV8301/gate driver IC power supply capacitor",
        ],
        "immediate_action": "🛑 STOP immediately. Disconnect the battery pack. Do NOT attempt to bench spin the motor or ride, as this can cause a runaway short circuit or fire.",
        "triage_steps": [
            "1. Multimeter Phase Resistance: Set DMM to Ohms (Ω). Measure resistance across each pair of motor phase wires (Phase A-B, B-C, A-C). All three should match within ~0.05Ω.",
            "2. MOSFET Diode Test: Switch multimeter to Diode mode. With battery disconnected, probe from Battery Negative to each Phase terminal (Red to B-, Black to Phase), then from Phase to Battery Positive (Red to Phase, Black to B+). Typical reading is ~0.45V - 0.55V. If any phase shows 0.00V, that MOSFET bank is blown.",
            "3. Inspect Phase Harness: Check the motor exit point at the axle for chafing against the axle core or aluminum footpad carriers.",
            "4. Check Terminal in VESC Tool: Connect via USB/BLE (do not spin motor). Run 'faults' command in the Terminal tab to inspect register fault codes (e.g. GVDD_OV, FAULT, OCP).",
        ],
        "safe_to_clear": False,
    },
    "FAULT_CODE_ABS_OVER_CURRENT": {
        "fault_name": "FAULT_CODE_ABS_OVER_CURRENT",
        "aliases": ["abs over current", "over current", "overcurrent", "abs_over_current"],
        "severity": "HIGH",
        "description": "Instantaneous current exceeded the controller's absolute peak hardware threshold (usually set 30-50A above Motor Current Max).",
        "primary_causes": [
            "Sudden loss of traction (free-spin) followed by instant curb landing or high-traction bite",
            "FOC motor observer losing sync (low inductance tracking error or bad motor detection parameters)",
            "Intermittent motor phase cable connection or loose bullet connector",
            "Aggressive field weakening transition or too high current ramp rate",
        ],
        "immediate_action": "Inspect motor cables and connectors for melting or loose crimps. Re-run FOC Motor Detection in VESC Tool.",
        "triage_steps": [
            "1. Inspect high-current phase bullets/connectors for signs of arcing, heat discoloration, or backing out.",
            "2. In VESC Tool -> Motor Settings -> FOC -> General: Check 'Absolute Maximum Current'. Ensure it is set at least 25A above 'Motor Current Max' (e.g., if Motor Max is 100A, ABS Max should be 130A-140A).",
            "3. Re-run complete FOC Detection Wizard (Resistance R, Inductance L, and Flux Linkage λ). An incorrect motor inductance estimate triggers current observer desync.",
            "4. Check 'Current KP' and 'Current KI' gains; excessively high KP can cause current ringing and spike into ABS cutoff.",
        ],
        "safe_to_clear": True,
    },
    "FAULT_CODE_OVER_VOLTAGE": {
        "fault_name": "FAULT_CODE_OVER_VOLTAGE",
        "aliases": ["over voltage", "overvoltage", "regen overvoltage", "high voltage fault"],
        "severity": "HIGH",
        "description": "Bus voltage exceeded the maximum safety limit configured in VESC Tool (often triggered during regenerative braking on a 100% full battery).",
        "primary_causes": [
            "Regenerative braking with a freshly charged 100% battery pack (nowhere for regen current to go)",
            "Battery BMS high-voltage disconnect opened during braking, causing voltage flyback",
            "Incorrect 'Maximum Input Voltage' setting for your battery cell series count (e.g., 18S or 20S configured with 15S limits)",
        ],
        "immediate_action": "Do not ride downhill immediately after 100% charge. Drain the battery slightly by free-spinning or riding on flat ground.",
        "triage_steps": [
            "1. Verify battery voltage: Check total pack voltage with DMM or in VESC Tool Realtime Data.",
            "2. Check Cutoff Limits in VESC Tool -> Motor Settings -> General: For 18S, Max Input Voltage should be ~78V; for 20S, ~86V.",
            "3. Ensure BMS is wired as Charge-Only if it lacks high-current regenerative discharge protection, or configure smart CAN BMS to communicate throttle limits.",
        ],
        "safe_to_clear": True,
    },
    "FAULT_CODE_UNDER_VOLTAGE": {
        "fault_name": "FAULT_CODE_UNDER_VOLTAGE",
        "aliases": ["under voltage", "undervoltage", "low voltage", "battery sag cutoff"],
        "severity": "MEDIUM",
        "description": "Bus voltage dropped below the minimum operational voltage threshold.",
        "primary_causes": [
            "Severely depleted battery pack",
            "Severe cell voltage sag under load due to an aging or high internal resistance (IR) battery pack",
            "Loose main XT60/XT90 power connector or broken nickel strip in the battery pack",
        ],
        "immediate_action": "Discontinue riding. Measure individual cell group voltages to inspect for out-of-balance or dead P-groups.",
        "triage_steps": [
            "1. Connect charger and check charging current and balance status.",
            "2. If voltage drops abruptly under mild throttle, check each cell group voltage via balance connector or smart BMS app. Look for groups differing by >0.1V.",
            "3. Verify 'Battery Voltage Cutoff Start' and 'End' are properly calibrated (e.g. 3.1V/cell end cutoff).",
        ],
        "safe_to_clear": True,
    },
    "FAULT_CODE_ENCODER": {
        "fault_name": "FAULT_CODE_ENCODER / FAULT_CODE_HALL",
        "aliases": ["encoder", "hall sensor", "hall fault", "motor jitter", "cogging"],
        "severity": "MEDIUM",
        "description": "Motor rotor position sensor or Hall sensor communication failed or reported invalid state transitions.",
        "primary_causes": [
            "Motor Hall sensor cable disconnected or damaged at the axle exit",
            "Miswired Hall sensor pinout (5V, GND, Temp, Hall 1, Hall 2, Hall 3)",
            "Defective Hall sensor IC inside the motor stator",
            "Moisture or water ingress inside the motor hall sensor PCB",
        ],
        "immediate_action": "Avoid riding until Hall detection passes. A failing Hall sensor causes harsh cogging, shuddering at launch, or unexpected nosedive.",
        "triage_steps": [
            "1. Inspect the 5-pin or 6-pin JST Hall connector between the motor and controller.",
            "2. Open VESC Tool -> Motor Settings -> FOC -> Hall Sensors: Run 'Detect Hall Sensors' and slowly spin the wheel by hand as prompted.",
            "3. Observe Hall table results: If any Hall sensor returns 255 or transitions fail, test 5V power and ground leads on the motor harness with a multimeter.",
        ],
        "safe_to_clear": True,
    },
    "FAULT_CODE_OVER_TEMP_FET": {
        "fault_name": "FAULT_CODE_OVER_TEMP_FET",
        "aliases": ["over temp fet", "overtemp", "controller overheating", "mosfet temperature"],
        "severity": "MEDIUM",
        "description": "MOSFET temperature sensor exceeded the configured thermal cutoff threshold (typically 85°C - 100°C).",
        "primary_causes": [
            "Poor thermal interface between controller MOSFETs and metal rail heatsink (dry or missing thermal pad/paste)",
            "Sustained steep hill climbs with high motor current and low airflow",
            "Air gap inside sealed plastic enclosure without aluminum rail heat transfer",
        ],
        "immediate_action": "Allow the controller to cool down. Check thermal coupling between the controller heatsink and aluminum chassis rails.",
        "triage_steps": [
            "1. Inspect thermal paste / thermal silicone pad on the controller backplate.",
            "2. Ensure mounting screws torque the heatsink firmly against aluminum rails.",
            "3. In VESC Tool, review 'Temperature Cutoff Start' (typically 80°C) and 'Temperature Cutoff End' (typically 95°C).",
        ],
        "safe_to_clear": True,
    },
}


def diagnose_fault(fault_query: str) -> Dict[str, Any]:
    """Diagnose a VESC fault code, describe root causes, and generate a step-by-step triage guide.

    Args:
        fault_query: The fault code or error description (e.g. 'FAULT_CODE_DRV', 'drv',
                     'abs over current', 'over voltage', 'hall sensor', 'blinking 3 times').

    Returns:
        Structured diagnostic report with severity, causes, safety actions, and multimeter triage steps.
    """
    clean_query = fault_query.lower().strip()

    # Exact key match
    for key, data in VESC_FAULT_KNOWLEDGE_BASE.items():
        if clean_query == key.lower():
            return {"status": "found", "diagnostic": data}

    # Alias / substring match
    for key, data in VESC_FAULT_KNOWLEDGE_BASE.items():
        for alias in data.get("aliases", []):
            if alias in clean_query or clean_query in alias:
                return {"status": "found", "diagnostic": data}

    # Return guidance if not recognized
    return {
        "status": "unknown_fault",
        "query": fault_query,
        "message": (
            f"Fault '{fault_query}' was not recognized in the immediate VESC knowledge base. "
            "Common VESC faults include: FAULT_CODE_DRV (gate driver), FAULT_CODE_ABS_OVER_CURRENT, "
            "FAULT_CODE_OVER_VOLTAGE, FAULT_CODE_UNDER_VOLTAGE, FAULT_CODE_ENCODER (Hall sensor), "
            "and FAULT_CODE_OVER_TEMP_FET."
        ),
        "available_fault_codes": list(VESC_FAULT_KNOWLEDGE_BASE.keys()),
    }
