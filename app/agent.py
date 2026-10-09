# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback

from app.firestore_service import (
    list_hardware_components,
    get_hardware_component,
    save_hardware_component,
    list_tune_presets,
    save_tune_preset,
)
from app.diagnostics import diagnose_fault
from app.youtube_service import search_creator_videos
from app.pev_service import search_pev_forum
from app.discord_service import find_discord_community
from app.image_service import generate_and_upload_image

MODEL = "gemini-3.8-flash"


async def generate_vesc_diagram(
    prompt: str,
    item_title: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generate a technical diagram, schematic, or visual illustration for a VESC hardware item or build setup.

    Uses the gemini-3.1-flash-lite-image model in the global region.
    The generated image is saved to the Playground Artifacts panel and published to Cloud Storage.

    Args:
        prompt: Detailed prompt describing the schematic, wiring pinout, controller layout, or battery configuration.
        item_title: Short title or component name for the artifact (e.g. 'Little_FOCer_Pinout', '18s2p_Battery_Pack', 'Pint_BMS_Bypass').
        tool_context: The ADK tool execution context injected by the runtime.

    Returns:
        dict containing the public Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>),
        the artifact filename, and image metadata.
    """
    result = generate_and_upload_image(prompt=prompt, item_title=item_title)

    # 1. Save with tool_context.save_artifact so it shows up in the Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(
        data=result["bytes"],
        mime_type=result["mime_type"],
    )
    await tool_context.save_artifact(
        filename=result["filename"],
        artifact=artifact_part,
    )

    # 2. Return public Cloud Storage URL and details (do not write to local file or return local path)
    return {
        "status": "success",
        "item_title": item_title,
        "filename": result["filename"],
        "public_url": result["public_url"],
        "description": result["description"],
    }


def find_discord_resources(topic_or_issue: str) -> List[Dict[str, Any]]:
    """Find the best VESC community Discord servers, channels, and invite links for a specific topic or issue.

    Covers trusted community servers: Float with VESC, VESC Development, Vescify (Onewheel conversions),
    Funwheel, JetFleet, Floatwheel, and FixMyPEV. Use this when users need live community help,
    specific channel advice, or server invites.

    Args:
        topic_or_issue: The problem, model, or build question (e.g. 'XR conversion wiring', 'Floatwheel ADV firmware', 'high voltage racing').

    Returns:
        List of matching Discord servers with invite links, descriptions, and recommended channels.
    """
    return find_discord_community(query=topic_or_issue)


def search_pev_knowledge(query: str) -> List[Dict[str, Any]]:
    """Search community discussion threads, build guides, and troubleshooting posts on pev.dev.

    Use this tool whenever riders ask questions about custom VESC hardware builds, firmware tips,
    IMU calibration, Float Package or Refloat setup, battery builds, or need community-tested solutions.

    Args:
        query: Search keywords (e.g. 'Little FOCer IMU calibration', 'Thor 300 setup', 'DRV fault fix', 'Refloat tune').

    Returns:
        List of matching discussion threads from pev.dev with title, link URL, reply counts, and excerpt.
    """
    return search_pev_forum(query=query)


def search_vesc_youtube_guides(query: str, creator: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search tutorial videos and teardowns from top VESC community YouTube creators.

    Covers trusted channels: @surfdado, @jayisdoingstuff, @BenjaminsRobotics,
    @fixmypev, and @JetFleet-Fajdiga. Use this to suggest specific video guides,
    teardowns, firmware tutorials, or tuning walk-throughs to the user.

    Args:
        query: Keywords to search (e.g. 'Floatwheel', 'VESC Tool setup', 'BMS wiring', 'Float Control').
        creator: Optional creator filter ('surfdado', 'jayisdoingstuff', 'BenjaminsRobotics', 'fixmypev', 'JetFleet').

    Returns:
        A list of matching video guides with title, author, watch URL, date, and description snippet.
    """
    return search_creator_videos(query=query, creator_filter=creator)


def diagnose_vesc_fault(fault_code: str) -> Dict[str, Any]:
    """Diagnose a VESC fault code, describe root causes, safety steps, and multimeter triage procedures.

    Use this tool whenever a rider mentions an error code, blinking LED pattern, or fault like:
    FAULT_CODE_DRV, DRV8301, ABS over-current, Overvoltage, Undervoltage, Hall sensor / encoder faults,
    or MOSFET over-temperature.

    Args:
        fault_code: The VESC error name or symptom (e.g. 'FAULT_CODE_DRV', 'drv', 'abs over current', 'hall sensor error').

    Returns:
        Diagnostic report with severity level, primary failure causes, immediate safety actions, and multimeter triage steps.
    """
    return diagnose_fault(fault_query=fault_code)


def lookup_hardware_components(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query verified Onewheel VESC hardware components from Firestore database.

    Args:
        category: Optional component category to filter by ('controller', 'motor', 'bms', 'footpad').

    Returns:
        A list of verified hardware components with specs, voltage ratings, and common issues.
    """
    return list_hardware_components(category=category)


def get_hardware_details(component_id: str) -> Dict[str, Any]:
    """Retrieve detailed specifications and troubleshooting notes for a specific hardware component.

    Args:
        component_id: Unique identifier of the component (e.g. 'little-focer-v4', 'thor300', 'hypercore-stock').

    Returns:
        Detailed component data including voltage ranges, current limits, and known issues.
    """
    return get_hardware_component(component_id=component_id)


def add_hardware_component(
    component_id: str,
    name: str,
    category: str,
    voltage_range: str,
    max_motor_current_a: float,
    supported_firmware: str,
    features: List[str],
    common_issues: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add or update a verified VESC hardware component in the Firestore database.

    Args:
        component_id: Unique slug identifier (e.g. 'spintend-ubox-100v').
        name: Full product name.
        category: Category ('controller', 'motor', 'bms', 'footpad').
        voltage_range: Voltage range string (e.g. '36V - 84V').
        max_motor_current_a: Max continuous or burst motor current in Amps.
        supported_firmware: Supported firmware string (e.g. 'VESC 6.02+').
        features: List of notable features.
        common_issues: Optional list of known quirks or troubleshooting notes.

    Returns:
        Confirmation dictionary with saved component details.
    """
    return save_hardware_component(
        component_id=component_id,
        name=name,
        category=category,
        voltage_range=voltage_range,
        max_motor_current_a=max_motor_current_a,
        supported_firmware=supported_firmware,
        features=features,
        common_issues=common_issues,
    )


def lookup_tune_presets(target_terrain: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search community-tested VESC tune presets from Firestore database.

    Args:
        target_terrain: Optional terrain filter (e.g. 'street', 'trail', 'park').

    Returns:
        List of matching tune presets containing PID gains, tiltback thresholds, and field weakening settings.
    """
    return list_tune_presets(target_terrain=target_terrain)


def add_tune_preset(
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
    """Save a community or custom VESC tune preset to the Firestore database.

    Args:
        preset_id: Slug identifier for preset (e.g. 'buttery-street-v1').
        name: Display name for preset.
        target_terrain: Target riding style or terrain.
        kp: Proportional balance gain.
        ki: Integral balance gain.
        kd: Derivative balance gain.
        tiltback_duty_cycle: Duty cycle threshold for tiltback (e.g. 0.80 for 80%).
        tiltback_angle_deg: Tiltback angle in degrees.
        field_weakening_current_a: Field weakening current in Amps.
        description: Description of feel, recommendations, and setup notes.

    Returns:
        Confirmation dictionary with saved preset details.
    """
    return save_tune_preset(
        preset_id=preset_id,
        name=name,
        target_terrain=target_terrain,
        kp=kp,
        ki=ki,
        kd=kd,
        tiltback_duty_cycle=tiltback_duty_cycle,
        tiltback_angle_deg=tiltback_angle_deg,
        field_weakening_current_a=field_weakening_current_a,
        description=description,
    )


async def generate_memories_callback(callback_context: CallbackContext):
    """Save salient facts and rider preferences across sessions to Memory Bank."""
    await callback_context.add_session_to_memory()
    return None


# Build A2UI System Prompt using A2uiSchemaManager (version 0.8) and BasicCatalog
_schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

_role_description = (
    "You are the VESC Onewheel Tuning & Troubleshooting Co-Pilot. "
    "You help DIY balance board riders configure, tune, and troubleshoot their VESC boards. "
    "You remember the rider's stated hardware specs, board model, riding preferences, and past issues "
    "across conversations to personalize and streamline your advice."
)

_workflow_description = (
    "Key Operational Behaviors:\n"
    "1. Build & Hardware Memory Retention: DIY riders frequently return to ask questions about past builds. "
    "Pay special attention to and actively acknowledge whenever the user mentions controllers used "
    "(Fungineers Thor400, Thor301, Zeus400; Floatwheel ADV500, ADV200, GTV Kit, PintV Kit; JetFleet F6, G18 GaN; "
    "ENNOID MK8, MK8 Pro, MK9 Pro; or legacy Little FOCer and Thor 300), battery configurations (18s2p, 20s2p, 32s, Samsung 50S, P42A, P45B), "
    "motors (CannonCore, Superflux, Hypercore, MTE), frame conversions, and troubleshooting resolutions that worked.\n"
    "2. Troubleshooting & Diagnostics: Whenever a user reports a fault code (FAULT_CODE_DRV, ABS over-current, "
    "hall sensor issues) or hardware problem, call `diagnose_vesc_fault`. Proactively search community knowledge "
    "on `search_pev_knowledge` and video guides on `search_vesc_youtube_guides`.\n"
    "3. Configuration & Tuning: When a user asks how to set up or tune their VESC, look up presets and hardware "
    "components, and check pev.dev and YouTube guides for relevant walkthroughs.\n"
    "4. Community & Real-Time Support: When a user asks about Discord communities, call `find_discord_resources`.\n"
    "5. Diagram & Image Generation: When a user asks for a diagram, schematic, wiring layout, or visual representation "
    "of a component, call `generate_vesc_diagram` with a detailed prompt and item title. In your A2UI response, "
    "include an Image component pointing to the returned public HTTPS URL.\n"
    "6. Firestore Storage: Use `get_hardware_details`, `add_hardware_component`, or `add_tune_preset` when managing database records.\n"
    "7. MANDATORY SOURCES & REFERENCES: At the end of EVERY response, you MUST include one or more Text components listing "
    "the sources, references, and documentation links used to formulate your answer. Cite direct URLs from tools (e.g. pev.dev threads, "
    "YouTube guide URLs, Discord community invite links, or Firestore records). If no external search tool was called, cite the canonical "
    "community links: 'pev.dev (https://pev.dev)' and the relevant community Discord (e.g. 'Float with VESC: https://discord.gg/Kwsgzte2' or 'VESC Development: https://discord.gg/tq6tav6MQ')."
)

_ui_description = (
    "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
    "Never nest a Card inside a Card. "
    "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
    "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
    "nothing in adk web). "
    "You may include one Image component, but only when you have a public https "
    "URL for the image (for example the URL an image tool returns after uploading "
    "to a public bucket). Set the Image url to that exact https link, for example "
    "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
    "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
    "not have a public URL, add a short Text line noting the image instead. "
    "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
    "headings and emphasis. "
    "ALWAYS end the column with a 'Sources & References' Text component (usageHint='caption') "
    "containing the full URLs of the referenced documentation, forum threads, videos, or communities. "
    "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
    "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
)

instruction = _schema_manager.generate_system_prompt(
    role_description=_role_description,
    workflow_description=_workflow_description,
    ui_description=_ui_description,
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        generate_vesc_diagram,
        find_discord_resources,
        search_pev_knowledge,
        search_vesc_youtube_guides,
        diagnose_vesc_fault,
        lookup_hardware_components,
        get_hardware_details,
        add_hardware_component,
        lookup_tune_presets,
        add_tune_preset,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

