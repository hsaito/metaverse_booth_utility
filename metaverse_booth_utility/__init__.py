# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


import json
import math
import os

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, PointerProperty, StringProperty
from bpy.types import Menu, Operator, Panel, PropertyGroup
from mathutils import Vector


UI_TRANSLATIONS = {
    "booth_presets": {
        "en": "Booth presets",
        "ja": "ブースプリセット",
        "es": "Preajustes de booth",
    },
    "event": {
        "en": "Event",
        "ja": "イベント",
        "es": "Evento",
    },
    "variant": {
        "en": "Variant",
        "ja": "バリエーション",
        "es": "Variante",
    },
    "type": {
        "en": "Type",
        "ja": "タイプ",
        "es": "Tipo",
    },
    "legacy_badge": {
        "en": "Legacy",
        "ja": "レガシー",
        "es": "Legado",
    },
    "show_legacy": {
        "en": "Show legacy",
        "ja": "レガシーを表示",
        "es": "Mostrar legado",
    },
    "select_event": {
        "en": "Select Event",
        "ja": "イベントを選択",
        "es": "Seleccionar evento",
    },
    "select_variant": {
        "en": "Select Variant",
        "ja": "バリエーションを選択",
        "es": "Seleccionar variante",
    },
    "select_type": {
        "en": "Select Type",
        "ja": "タイプを選択",
        "es": "Seleccionar tipo",
    },
    "advanced": {
        "en": "Advanced",
        "ja": "詳細設定",
        "es": "Avanzado",
    },
    "generate": {
        "en": "Generate",
        "ja": "生成",
        "es": "Generar",
    },
    "reset": {
        "en": "Reset",
        "ja": "リセット",
        "es": "Restablecer",
    },
    "remove_generated": {
        "en": "Remove Generated",
        "ja": "生成物を削除",
        "es": "Eliminar generados",
    },
    "show_frame": {
        "en": "Show Frame",
        "ja": "フレームを表示",
        "es": "Mostrar marco",
    },
    "hide_frame": {
        "en": "Hide Frame",
        "ja": "フレームを非表示",
        "es": "Ocultar marco",
    },
    "show_arrow": {
        "en": "Show Arrow",
        "ja": "矢印を表示",
        "es": "Mostrar flecha",
    },
    "hide_arrow": {
        "en": "Hide Arrow",
        "ja": "矢印を非表示",
        "es": "Ocultar flecha",
    },
    "toggle_target_missing": {
        "en": "No generated {target} object found",
        "ja": "生成済みの{target}オブジェクトが見つかりません",
        "es": "No se encontro un objeto generado de {target}",
    },
    "frame": {
        "en": "frame",
        "ja": "フレーム",
        "es": "marco",
    },
    "arrow": {
        "en": "arrow",
        "ja": "矢印",
        "es": "flecha",
    },
    "invalid_preset_json": {
        "en": "Invalid preset JSON",
        "ja": "プリセットJSONが不正です",
        "es": "JSON de preajustes invalido",
    },
    "select_preset_preview": {
        "en": "Select a preset to preview",
        "ja": "プレビューするプリセットを選択してください",
        "es": "Selecciona un preajuste para ver la vista previa",
    },
    "size": {
        "en": "Size",
        "ja": "サイズ",
        "es": "Tamano",
    },
    "front_axis": {
        "en": "Front axis",
        "ja": "前方向軸",
        "es": "Eje frontal",
    },
    "width_m": {
        "en": "Width (m)",
        "ja": "幅 (m)",
        "es": "Ancho (m)",
    },
    "depth_m": {
        "en": "Depth (m)",
        "ja": "奥行き (m)",
        "es": "Profundidad (m)",
    },
    "height_m": {
        "en": "Height (m)",
        "ja": "高さ (m)",
        "es": "Altura (m)",
    },
    "unable_to_load_preset_json": {
        "en": "Unable to load preset JSON",
        "ja": "プリセットJSONを読み込めません",
        "es": "No se pudo cargar el JSON de preajustes",
    },
    "generated_message": {
        "en": "Generated {event}/{variant}/{type_name} ({width}x{depth} m)",
        "ja": "{event}/{variant}/{type_name} を生成しました ({width}x{depth} m)",
        "es": "Generado {event}/{variant}/{type_name} ({width}x{depth} m)",
    },
    "reset_selection": {
        "en": "Reset booth preset selection",
        "ja": "ブースプリセット選択をリセットしました",
        "es": "Se restablecio la seleccion de preajuste de booth",
    },
    "removed_generated": {
        "en": "Removed {count} generated object(s)",
        "ja": "生成オブジェクトを {count} 個削除しました",
        "es": "Se eliminaron {count} objeto(s) generados",
    },
    "manual": {
        "en": "Manual",
        "ja": "手動",
        "es": "Manual",
    },
    "custom": {
        "en": "Custom",
        "ja": "カスタム",
        "es": "Personalizado",
    },
}


def get_effective_ui_locale():
    locale_code = ""
    try:
        locale_code = getattr(bpy.context.preferences.view, "language", "")
    except (AttributeError, RuntimeError):
        locale_code = ""

    if not locale_code or locale_code == "DEFAULT":
        locale_code = getattr(bpy.app.translations, "locale", "")

    return str(locale_code or "en_US")


def get_locale_codes(locale_code=None):
    locale_code = str(locale_code or get_effective_ui_locale()).strip()
    if not locale_code:
        return []

    normalized = locale_code.replace("-", "_")
    parts = normalized.split("_", 1)
    language = parts[0].lower()
    region = parts[1] if len(parts) > 1 else ""

    candidates = []

    def append_unique(value):
        if value and value not in candidates:
            candidates.append(value)

    append_unique(normalized)
    append_unique(normalized.replace("_", "-"))
    append_unique(normalized.replace("_", ""))
    if language and region:
        append_unique(f"{language}_{region.upper()}")
        append_unique(f"{language}_{region.lower()}")
        append_unique(f"{language}-{region.upper()}")
        append_unique(f"{language}-{region.lower()}")
        append_unique(f"{language}{region.upper()}")
        append_unique(f"{language}{region.lower()}")
    append_unique(language)
    return candidates


def normalize_locale_key(value):
    value = str(value or "").strip()
    if not value:
        return ""
    value = value.replace("_", "-")
    parts = value.split("-")
    if not parts:
        return ""
    language = parts[0].lower()
    if len(parts) == 1:
        return language
    tail = []
    for segment in parts[1:]:
        if len(segment) <= 3:
            tail.append(segment.upper())
        else:
            tail.append(segment)
    return "-".join([language] + tail)


def get_i18n_value(i18n_map, locale_code=None):
    if not isinstance(i18n_map, dict):
        return ""

    normalized_map = {}
    for key, value in i18n_map.items():
        normalized_key = normalize_locale_key(key)
        if normalized_key and isinstance(value, str) and value.strip() and normalized_key not in normalized_map:
            normalized_map[normalized_key] = value

    for candidate in get_locale_codes(locale_code):
        normalized_candidate = normalize_locale_key(candidate)
        value = normalized_map.get(normalized_candidate)
        if isinstance(value, str) and value.strip():
            return value

    return ""


def get_localized_name(item, locale_code=None):
    if not isinstance(item, dict):
        return ""

    i18n_map = item.get("name_i18n")
    i18n_value = get_i18n_value(i18n_map, locale_code)
    if i18n_value:
        return i18n_value

    # Backward compatibility with legacy keys like name_jaJP/name_ja/name_es.
    for suffix in get_locale_codes(locale_code):
        key = f"name_{suffix}"
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value

    fallback = item.get("name")
    if isinstance(fallback, str):
        return fallback
    return ""


def tr(key):
    language = get_effective_ui_locale().split("_", 1)[0].lower()
    labels = UI_TRANSLATIONS.get(key, {})
    return labels.get(language, labels.get("en", key))


def get_addon_preferences():
    try:
        addons = bpy.context.preferences.addons
    except (AttributeError, RuntimeError):
        return None

    addon = addons.get(__name__)
    if addon:
        return addon.preferences
    return None


def get_default_show_legacy_value():
    prefs = get_addon_preferences()
    if prefs is not None:
        return bool(getattr(prefs, "default_show_legacy", False))
    return False


def apply_default_show_legacy_to_all_scenes(value):
    try:
        scenes = bpy.data.scenes
    except AttributeError:
        return

    show_legacy = bool(value)
    for scene in scenes:
        props = getattr(scene, "booth_config", None)
        if props is None:
            continue
        if props.show_legacy == show_legacy:
            continue
        props.show_legacy = show_legacy


def update_default_show_legacy_preference(pref, context):
    del context  # Unused.
    apply_default_show_legacy_to_all_scenes(pref.default_show_legacy)


def get_item_name(item):
    if not isinstance(item, dict):
        return ""
    name = item.get("name")
    if isinstance(name, str):
        return name
    return ""


def get_frame_object():
    return bpy.data.objects.get("Booth Frame Reference")


def get_arrow_object():
    return bpy.data.objects.get("Booth Front Arrow")


def get_generated_collection(context=None):
    if context and getattr(context, "scene", None):
        scene_collection = context.scene.collection
        for child in scene_collection.children:
            if child.name == GENERATED_COLLECTION_NAME:
                return child

    return bpy.data.collections.get(GENERATED_COLLECTION_NAME)


def ensure_generated_collection(context):
    generated_collection = get_generated_collection(context)
    if generated_collection:
        return generated_collection

    generated_collection = bpy.data.collections.new(GENERATED_COLLECTION_NAME)

    scene = getattr(context, "scene", None)
    if scene:
        scene_collection = scene.collection
        if scene_collection.children.get(generated_collection.name) is None:
            scene_collection.children.link(generated_collection)

    return generated_collection


def move_object_to_collection(obj, target_collection):
    if not obj or not target_collection:
        return

    if target_collection not in obj.users_collection:
        target_collection.objects.link(obj)

    for collection in list(obj.users_collection):
        if collection != target_collection:
            collection.objects.unlink(obj)


def is_object_visible(obj):
    return bool(obj) and not obj.hide_viewport


def find_event(config_data, event_name):
    for event in config_data.get("events", []):
        if get_item_name(event) == event_name:
            return event
    return None


def find_variant(event_data, variant_name):
    if not isinstance(event_data, dict):
        return None
    for variant in event_data.get("variants", []):
        if get_item_name(variant) == variant_name:
            return variant
    return None


def find_type(variant_data, type_name):
    if not isinstance(variant_data, dict):
        return None
    for preset in variant_data.get("types", []):
        if get_item_name(preset) == type_name:
            return preset
    return None


def is_legacy_variant(variant_data):
    if not isinstance(variant_data, dict):
        return False

    legacy_value = variant_data.get("legacy")
    if isinstance(legacy_value, bool):
        return legacy_value

    # Backward compatibility for preset files that use a dedicated "Legacy" variant.
    return get_item_name(variant_data).strip().lower() == "legacy"


def is_legacy_type(preset_data, variant_data=None):
    if not isinstance(preset_data, dict):
        return False

    legacy_value = preset_data.get("legacy")
    if isinstance(legacy_value, bool):
        return legacy_value

    return is_legacy_variant(variant_data)


def get_selectable_types(variant_data, show_legacy):
    if not isinstance(variant_data, dict):
        return []

    selectable = []
    for preset in variant_data.get("types", []):
        if is_legacy_type(preset, variant_data) and not show_legacy:
            continue
        if not get_item_name(preset):
            continue
        selectable.append(preset)
    return selectable


def get_selectable_variants(event_data, show_legacy):
    if not isinstance(event_data, dict):
        return []

    selectable = []
    for variant in event_data.get("variants", []):
        if is_legacy_variant(variant) and not show_legacy:
            continue
        if not get_item_name(variant):
            continue
        if not get_selectable_types(variant, show_legacy):
            continue
        selectable.append(variant)
    return selectable


def get_selectable_events(config_data, show_legacy):
    selectable = []
    for event in config_data.get("events", []):
        if not get_item_name(event):
            continue
        if not get_selectable_variants(event, show_legacy):
            continue
        selectable.append(event)
    return selectable


def apply_preset_to_properties(props, preset, variant=None):
    if not isinstance(preset, dict):
        return

    props.width_m = float(preset.get("width_m", props.width_m))
    props.depth_m = float(preset.get("depth_m", props.depth_m))
    props.height_m = float(preset.get("height_m", props.height_m))
    props.front_axis = normalize_front_axis(preset.get("front_axis", props.front_axis))
    props.selected_type_is_legacy = is_legacy_type(preset, variant)


def reset_preset_selection_state(props):
    props.event_name = ""
    props.variant_name = ""
    props.type_name = ""
    props.selected_type_is_legacy = False
    props.width_m = 1.0
    props.depth_m = 1.0
    props.height_m = 1.0
    props.front_axis = "y-"


def normalize_selection_to_first_valid(props, config_data=None):
    props.selected_type_is_legacy = False

    if config_data is None:
        try:
            config_data = get_config_data(props)
        except ValueError:
            return

    selectable_events = get_selectable_events(config_data, props.show_legacy)
    if not selectable_events:
        props.event_name = ""
        props.variant_name = ""
        props.type_name = ""
        return

    event_names = [get_item_name(event) for event in selectable_events]
    if props.event_name not in event_names:
        props.event_name = event_names[0]

    event = find_event(config_data, props.event_name)
    if not event:
        props.event_name = event_names[0]
        event = find_event(config_data, props.event_name)
    if not event:
        props.variant_name = ""
        props.type_name = ""
        return

    selectable_variants = get_selectable_variants(event, props.show_legacy)
    if not selectable_variants:
        props.variant_name = ""
        props.type_name = ""
        return

    variant_names = [get_item_name(variant) for variant in selectable_variants]
    if props.variant_name not in variant_names:
        props.variant_name = variant_names[0]

    variant = find_variant(event, props.variant_name)
    if not variant:
        props.variant_name = variant_names[0]
        variant = find_variant(event, props.variant_name)
    if not variant:
        props.type_name = ""
        return

    selectable_types = get_selectable_types(variant, props.show_legacy)
    if not selectable_types:
        props.type_name = ""
        return

    type_names = [get_item_name(preset) for preset in selectable_types]
    if props.type_name not in type_names:
        props.type_name = type_names[0]

    preset = find_type(variant, props.type_name)
    if not preset:
        props.type_name = type_names[0]
        preset = find_type(variant, props.type_name)

    if preset:
        apply_preset_to_properties(props, preset, variant)


def sync_selected_legacy_flag(props, config_data=None):
    props.selected_type_is_legacy = False

    if config_data is None:
        try:
            config_data = get_config_data(props)
        except ValueError:
            return

    event = find_event(config_data, props.event_name)
    if not event:
        return

    variant = find_variant(event, props.variant_name)
    if not variant:
        return

    preset = find_type(variant, props.type_name)
    if not preset:
        return

    props.selected_type_is_legacy = is_legacy_type(preset, variant)


def update_show_legacy(props, context):
    del context  # Unused.

    if props.suppress_show_legacy_update:
        return

    # Changing visibility mode should reset selection/preview to initial state.
    reset_preset_selection_state(props)


def get_selected_display_names(props, config_data=None):
    event_display = props.event_name
    variant_display = props.variant_name
    type_display = props.type_name

    if config_data is None:
        try:
            config_data = get_config_data(props)
        except ValueError:
            return event_display, variant_display, type_display

    event = find_event(config_data, props.event_name)
    if event:
        event_display = get_localized_name(event)
        variant = find_variant(event, props.variant_name)
        if variant:
            variant_display = get_localized_name(variant)
            preset = find_type(variant, props.type_name)
            if preset:
                type_display = get_localized_name(preset)

    return event_display, variant_display, type_display


def get_event_menu_items(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []

    items = []
    for event in get_selectable_events(data, props.show_legacy):
        name = get_item_name(event)
        items.append((name, get_localized_name(event)))
    return items


def get_variant_menu_items(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []

    event = find_event(data, props.event_name)
    if not event:
        return []

    items = []
    for variant in get_selectable_variants(event, props.show_legacy):
        name = get_item_name(variant)
        items.append((name, get_localized_name(variant)))
    return items


def get_type_menu_items(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []

    event = find_event(data, props.event_name)
    if not event:
        return []

    variant = find_variant(event, props.variant_name)
    if not variant:
        return []

    items = []
    for preset in get_selectable_types(variant, props.show_legacy):
        name = get_item_name(preset)
        items.append((name, get_localized_name(preset)))
    return items


def get_event_names(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []
    return [get_item_name(item) for item in get_selectable_events(data, props.show_legacy)]


def get_variant_names(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []
    if not props.event_name:
        return []
    event = find_event(data, props.event_name)
    if event:
        return [get_item_name(item) for item in get_selectable_variants(event, props.show_legacy)]
    return []


def get_type_names(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []
    if not props.event_name or not props.variant_name:
        return []
    event = find_event(data, props.event_name)
    if not event:
        return []

    variant = find_variant(event, props.variant_name)
    if variant:
        return [get_item_name(item) for item in get_selectable_types(variant, props.show_legacy)]
    return []

bl_info = {
    "name": "Metaverse Booth Utility",
    "blender": (3, 6, 0),
    "category": "Object",
    "version": (1, 1, 4),
    "author": "Hideki Saito",
    "description": "Generate booth reference frames and front-direction arrows from configurable event presets.",
}

ADDON_DIR = os.path.dirname(__file__)
DEFAULT_CONFIG_PATH = os.path.join(ADDON_DIR, "defaults.json")
DEFAULT_CONFIG_TEXT = ""
GENERATED_OBJECT_NAMES = (
    "Booth Frame Reference",
    "Booth Front Arrow",
    "Booth Arrow Shaft",
    "Booth Arrow Tip",
)
GENERATED_COLLECTION_NAME = "Metaverse Booth Utility Generated"
FRONT_AXIS_ITEMS = (
    ("x+", "x+", "Front points to +X"),
    ("x-", "x-", "Front points to -X"),
    ("y+", "y+", "Front points to +Y"),
    ("y-", "y-", "Front points to -Y"),
    ("z+", "z+", "Front points to +Z"),
    ("z-", "z-", "Front points to -Z"),
)


def load_default_config_text():
    global DEFAULT_CONFIG_TEXT
    if not DEFAULT_CONFIG_TEXT:
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as handle:
            DEFAULT_CONFIG_TEXT = handle.read()
    return DEFAULT_CONFIG_TEXT


def parse_config_text(text):
    text = (text or "").strip()
    if not text:
        text = load_default_config_text()
    return json.loads(text)


def get_config_data(props):
    text = props.config_json or load_default_config_text()
    try:
        return parse_config_text(text)
    except json.JSONDecodeError as exc:
        raise ValueError(str(exc)) from exc
    except FileNotFoundError as exc:
        raise ValueError(str(exc)) from exc


def validate_config_text(props):
    if not props.config_json:
        return True
    try:
        parse_config_text(props.config_json)
    except (json.JSONDecodeError, FileNotFoundError, ValueError):
        return False
    return True


def normalize_front_axis(value):
    value = str(value or "").strip().lower()
    legacy_aliases = {
        "x": "x+",
        "+x": "x+",
        "-x": "x-",
        "y": "y+",
        "+y": "y+",
        "-y": "y-",
        "z": "z+",
        "+z": "z+",
        "-z": "z-",
    }
    value = legacy_aliases.get(value, value)
    valid_axes = {item[0] for item in FRONT_AXIS_ITEMS}
    if value in valid_axes:
        return value
    return "y-"


def show_invalid_json_popup(context, message):
    def draw_menu(self, context):
        self.layout.label(text=message, icon="ERROR")

    try:
        context.window_manager.popup_menu(draw_menu, title="Invalid Preset JSON", icon="ERROR")
    except AttributeError:
        pass


def get_first_event(config_data):
    events = config_data.get("events", [])
    if events:
        return events[0]
    return {}


def get_first_variant(event_data):
    variants = event_data.get("variants", [])
    if variants:
        return variants[0]
    return {}


def get_first_type(variant_data):
    types = variant_data.get("types", [])
    if types:
        return types[0]
    return {}


class MetaverseBoothUtilityPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    default_show_legacy: BoolProperty(
        name="Default Show Legacy",
        description="Enable Show legacy by default for newly initialized scenes and reset; applies to open scenes immediately",
        default=False,
        update=update_default_show_legacy_preference,
    )

    def draw(self, context):
        del context  # Unused.
        layout = self.layout
        layout.prop(self, "default_show_legacy")


class BoothConfigProperties(PropertyGroup):
    config_json: StringProperty(
        name="Preset JSON",
        description="JSON document describing booth presets",
        default=load_default_config_text(),
    )
    config_error: StringProperty(name="Config Error", default="")
    event_name: StringProperty(name="Event", default="")
    variant_name: StringProperty(name="Variant", default="")
    type_name: StringProperty(name="Type", default="")
    suppress_show_legacy_update: BoolProperty(name="Suppress Show Legacy Update", default=False, options={"HIDDEN"})
    show_legacy: BoolProperty(name="Show Legacy", default=False, update=update_show_legacy)
    selected_type_is_legacy: BoolProperty(name="Selected Type Is Legacy", default=False)
    width_m: FloatProperty(name="Width (m)", default=1.0, min=0.1)
    depth_m: FloatProperty(name="Depth (m)", default=1.0, min=0.1)
    height_m: FloatProperty(name="Height (m)", default=1.0, min=0.01)
    front_axis: EnumProperty(name="Front Axis", items=FRONT_AXIS_ITEMS, default="y-")
    advanced_open: BoolProperty(name="Advanced", default=False)

    def get_config_data(self):
        return get_config_data(self)


class BOOTH_OT_generate_frame(Operator):
    bl_idname = "booth.generate_frame"
    bl_label = "Generate"
    bl_description = "Generate a booth reference frame and front arrow"

    def execute(self, context):
        props = context.scene.booth_config
        try:
            config_data = get_config_data(props)
        except ValueError:
            self.report({"ERROR"}, props.config_error or tr("unable_to_load_preset_json"))
            return {"CANCELLED"}

        selected = self._get_selected_spec(config_data, props)
        selected_is_legacy = False
        if selected:
            event, variant, preset = selected
            event_name = get_item_name(event) or tr("manual")
            variant_name = get_item_name(variant) or tr("custom")
            preset_name = get_item_name(preset) or tr("custom")
            event_display = get_localized_name(event)
            variant_display = get_localized_name(variant)
            preset_display = get_localized_name(preset)
            selected_is_legacy = is_legacy_type(preset, variant)
        else:
            event_name = props.event_name or tr("manual")
            variant_name = props.variant_name or tr("custom")
            preset_name = props.type_name or tr("custom")
            event_display = event_name
            variant_display = variant_name
            preset_display = preset_name

        props.selected_type_is_legacy = selected_is_legacy

        width = float(props.width_m)
        depth = float(props.depth_m)
        height = float(props.height_m)
        front_axis = normalize_front_axis(props.front_axis)
        generated_collection = ensure_generated_collection(context)

        self._remove_existing_objects()
        frame_obj = self._create_frame(
            width,
            depth,
            height,
            event_name,
            variant_name,
            preset_name,
            selected_is_legacy,
            generated_collection,
        )
        self._create_front_arrow(frame_obj, width, depth, height, front_axis, generated_collection)

        self.report(
            {"INFO"},
            tr("generated_message").format(
                event=event_display,
                variant=variant_display,
                type_name=preset_display,
                width=width,
                depth=depth,
            ),
        )
        return {"FINISHED"}

    def _get_selected_spec(self, config_data, props):
        event_name = props.event_name
        variant_name = props.variant_name
        type_name = props.type_name

        if not event_name or not variant_name or not type_name:
            return None

        event = find_event(config_data, event_name)
        if not event:
            return None

        variant = find_variant(event, variant_name)
        if not variant:
            return None

        preset = find_type(variant, type_name)
        if preset:
            return event, variant, preset

        return None

    def _remove_existing_objects(self):
        for name in GENERATED_OBJECT_NAMES:
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

    def _create_frame(self, width, depth, height, event_name, variant_name, type_name, is_legacy, generated_collection):
        bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0), size=2.0)
        frame_obj = bpy.context.active_object
        frame_obj.name = "Booth Frame Reference"
        if frame_obj.data:
            frame_obj.data.name = "Booth Frame Reference Mesh"
        frame_obj.location = (0.0, 0.0, height / 2.0)
        frame_obj.rotation_euler = (0.0, 0.0, 0.0)
        frame_obj.scale = (width / 2.0, depth / 2.0, height / 2.0)
        frame_obj.display_type = "WIRE"
        frame_obj.show_wire = True
        frame_obj.show_in_front = True
        frame_obj.hide_render = True
        frame_obj.hide_select = True
        frame_obj.select_set(False)
        frame_obj.lock_location = (True, True, True)
        frame_obj.lock_rotation = (True, True, True)
        frame_obj.lock_scale = (True, True, True)
        frame_obj.show_axis = False
        frame_obj["booth_generated"] = True
        frame_obj["booth_event"] = event_name
        frame_obj["booth_variant"] = variant_name
        frame_obj["booth_type"] = type_name
        frame_obj["booth_width_m"] = width
        frame_obj["booth_depth_m"] = depth
        frame_obj["booth_height_m"] = height
        frame_obj["booth_legacy"] = bool(is_legacy)
        move_object_to_collection(frame_obj, generated_collection)
        return frame_obj

    def _create_front_arrow(self, frame_obj, width, depth, height, front_axis, generated_collection):
        normalized_axis = normalize_front_axis(front_axis)
        axis_vector = self._axis_to_vector(normalized_axis)

        # Place the marker at booth center so +/- directions can remain inside bounds.
        base_location_world = Vector((0.0, 0.0, height / 2.0))

        if normalized_axis.startswith("x"):
            axis_half_extent = width / 2.0
        elif normalized_axis.startswith("y"):
            axis_half_extent = depth / 2.0
        else:
            axis_half_extent = height / 2.0

        # 0.8 margin keeps the tip and body safely within the frame volume.
        marker_size = max(axis_half_extent * 0.8, 0.05)

        bpy.ops.object.empty_add(type="SINGLE_ARROW", location=base_location_world)
        arrow = bpy.context.active_object
        arrow.name = "Booth Front Arrow"
        arrow.empty_display_type = "SINGLE_ARROW"
        arrow.empty_display_size = marker_size
        arrow.rotation_mode = "QUATERNION"
        arrow.rotation_quaternion = self._quaternion_from_vectors(Vector((0.0, 0.0, 1.0)), axis_vector)
        arrow.parent = None
        arrow.location = base_location_world
        arrow.hide_render = True
        arrow.hide_select = True
        arrow.select_set(False)
        arrow.lock_location = (True, True, True)
        arrow.lock_rotation = (True, True, True)
        arrow.lock_scale = (True, True, True)
        arrow.show_axis = False
        arrow["booth_generated"] = True
        move_object_to_collection(arrow, generated_collection)

        bpy.context.view_layer.update()

    def _axis_to_vector(self, axis):
        axis = normalize_front_axis(axis)
        mapping = {
            "x+": Vector((1.0, 0.0, 0.0)),
            "x-": Vector((-1.0, 0.0, 0.0)),
            "y+": Vector((0.0, 1.0, 0.0)),
            "y-": Vector((0.0, -1.0, 0.0)),
            "z+": Vector((0.0, 0.0, 1.0)),
            "z-": Vector((0.0, 0.0, -1.0)),
        }
        return mapping.get(axis, Vector((0.0, -1.0, 0.0)))

    def _quaternion_from_vectors(self, start, end):
        start_vec = self._normalize_vector(start)
        end_vec = self._normalize_vector(end)
        if start_vec.dot(end_vec) > 0.9999:
            return (1.0, 0.0, 0.0, 0.0)
        if start_vec.dot(end_vec) < -0.9999:
            axis = Vector((0.0, 0.0, 1.0))
            return (math.cos(math.pi / 2.0), axis.x * math.sin(math.pi / 2.0), axis.y * math.sin(math.pi / 2.0), axis.z * math.sin(math.pi / 2.0))
        axis = start_vec.cross(end_vec)
        angle = math.acos(max(-1.0, min(1.0, start_vec.dot(end_vec))))
        return (math.cos(angle / 2.0), axis.x * math.sin(angle / 2.0), axis.y * math.sin(angle / 2.0), axis.z * math.sin(angle / 2.0))

    def _normalize_vector(self, vector):
        vector = Vector(vector)
        length = vector.length
        if length < 1e-6:
            return Vector((0.0, 0.0, 1.0))
        return vector.normalized()


class BOOTH_OT_reset_config(Operator):
    bl_idname = "booth.reset_config"
    bl_label = "Reset"
    bl_description = "Reset all booth preset selections"

    def execute(self, context):
        props = context.scene.booth_config
        props.config_json = load_default_config_text()
        props.config_error = ""
        props.suppress_show_legacy_update = True
        try:
            props.show_legacy = get_default_show_legacy_value()
        finally:
            props.suppress_show_legacy_update = False
        reset_preset_selection_state(props)
        self.report({"INFO"}, tr("reset_selection"))
        return {"FINISHED"}


class BOOTH_OT_remove_generated(Operator):
    bl_idname = "booth.remove_generated"
    bl_label = "Remove Generated"
    bl_description = "Remove frame and arrow objects created by this add-on"

    def execute(self, context):
        removed_count = 0
        for obj in list(bpy.data.objects):
            if obj.get("booth_generated") or obj.name in GENERATED_OBJECT_NAMES:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed_count += 1

        generated_collection = get_generated_collection(context)
        if generated_collection and not generated_collection.objects and not generated_collection.children:
            bpy.data.collections.remove(generated_collection)

        self.report({"INFO"}, tr("removed_generated").format(count=removed_count))
        return {"FINISHED"}


class BOOTH_OT_toggle_frame_visibility(Operator):
    bl_idname = "booth.toggle_frame_visibility"
    bl_label = "Toggle Frame Visibility"
    bl_description = "Show or hide the generated booth frame"

    def execute(self, context):
        frame_obj = get_frame_object()
        if not frame_obj:
            self.report({"WARNING"}, tr("toggle_target_missing").format(target=tr("frame")))
            return {"CANCELLED"}

        frame_obj.hide_viewport = not frame_obj.hide_viewport
        return {"FINISHED"}


class BOOTH_OT_toggle_arrow_visibility(Operator):
    bl_idname = "booth.toggle_arrow_visibility"
    bl_label = "Toggle Arrow Visibility"
    bl_description = "Show or hide the generated front arrow"

    def execute(self, context):
        arrow_obj = get_arrow_object()
        if not arrow_obj:
            self.report({"WARNING"}, tr("toggle_target_missing").format(target=tr("arrow")))
            return {"CANCELLED"}

        arrow_obj.hide_viewport = not arrow_obj.hide_viewport
        return {"FINISHED"}


class BOOTH_OT_select_event(Operator):
    bl_idname = "booth.select_event"
    bl_label = "Select Event"
    value: StringProperty()

    def execute(self, context):
        props = context.scene.booth_config
        props.event_name = self.value
        props.variant_name = ""
        props.type_name = ""
        props.selected_type_is_legacy = False
        return {"FINISHED"}


class BOOTH_OT_select_variant(Operator):
    bl_idname = "booth.select_variant"
    bl_label = "Select Variant"
    value: StringProperty()

    def execute(self, context):
        props = context.scene.booth_config
        props.variant_name = self.value
        props.type_name = ""
        props.selected_type_is_legacy = False
        return {"FINISHED"}


class BOOTH_OT_select_type(Operator):
    bl_idname = "booth.select_type"
    bl_label = "Select Type"
    value: StringProperty()

    def execute(self, context):
        props = context.scene.booth_config
        props.type_name = self.value

        try:
            config_data = get_config_data(props)
        except ValueError:
            return {"FINISHED"}

        event = find_event(config_data, props.event_name)
        if not event:
            return {"FINISHED"}

        variant = find_variant(event, props.variant_name)
        if not variant:
            return {"FINISHED"}

        preset = find_type(variant, props.type_name)
        if preset:
            apply_preset_to_properties(props, preset, variant)
            return {"FINISHED"}
        props.selected_type_is_legacy = False
        return {"FINISHED"}


class BOOTH_MT_event_menu(Menu):
    bl_idname = "BOOTH_MT_event_menu"
    bl_label = "Events"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config
        for name, display_name in get_event_menu_items(props):
            layout.operator("booth.select_event", text=display_name).value = name


class BOOTH_MT_variant_menu(Menu):
    bl_idname = "BOOTH_MT_variant_menu"
    bl_label = "Variants"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config
        for name, display_name in get_variant_menu_items(props):
            layout.operator("booth.select_variant", text=display_name).value = name


class BOOTH_MT_type_menu(Menu):
    bl_idname = "BOOTH_MT_type_menu"
    bl_label = "Types"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config
        for name, display_name in get_type_menu_items(props):
            layout.operator("booth.select_type", text=display_name).value = name


class BOOTH_PT_panel(Panel):
    bl_label = "Metaverse Booth Utility"
    bl_idname = "BOOTH_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Metaverse"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config
        event_display, variant_display, type_display = get_selected_display_names(props)

        layout.label(text=tr("booth_presets"))
        layout.prop(props, "show_legacy", text=tr("show_legacy"))

        event_row = layout.row()
        event_row.label(text=tr("event"))
        event_row.menu("BOOTH_MT_event_menu", text=event_display or tr("select_event"))

        variant_row = layout.row()
        variant_row.label(text=tr("variant"))
        variant_row.enabled = bool(props.event_name)
        variant_row.menu("BOOTH_MT_variant_menu", text=variant_display or tr("select_variant"))

        type_row = layout.row()
        type_row.label(text=tr("type"))
        type_row.enabled = bool(props.event_name and props.variant_name)
        type_row.menu("BOOTH_MT_type_menu", text=type_display or tr("select_type"))

        advanced_box = layout.box()
        advanced_box.prop(props, "advanced_open", text=tr("advanced"), icon="TRIA_DOWN" if props.advanced_open else "TRIA_RIGHT")
        if props.advanced_open:
            advanced_box.prop(props, "width_m", text=tr("width_m"))
            advanced_box.prop(props, "depth_m", text=tr("depth_m"))
            advanced_box.prop(props, "height_m", text=tr("height_m"))
            advanced_box.prop(props, "front_axis", text=tr("front_axis"))

        action_row = layout.row(align=True)
        action_row.operator("booth.generate_frame", text=tr("generate"), icon="CHECKMARK")
        action_row.operator("booth.reset_config", text=tr("reset"), icon="LOOP_BACK")

        frame_obj = get_frame_object()
        arrow_obj = get_arrow_object()

        visibility_row = layout.row(align=True)
        frame_label = tr("hide_frame") if is_object_visible(frame_obj) else tr("show_frame")
        arrow_label = tr("hide_arrow") if is_object_visible(arrow_obj) else tr("show_arrow")
        visibility_row.operator("booth.toggle_frame_visibility", text=frame_label)
        visibility_row.operator("booth.toggle_arrow_visibility", text=arrow_label)

        layout.operator("booth.remove_generated", text=tr("remove_generated"))

        if not validate_config_text(props):
            layout.label(text=tr("invalid_preset_json"), icon="ERROR")
            return

        try:
            config_data = get_config_data(props)
        except ValueError:
            layout.label(text=tr("invalid_preset_json"), icon="ERROR")
            return

        event = find_event(config_data, props.event_name)
        variant = find_variant(event, props.variant_name) if event else None
        selected = find_type(variant, props.type_name) if variant else None
        selected_visible = bool(
            selected
            and (props.show_legacy or not is_legacy_type(selected, variant))
        )

        if selected_visible:
            box = layout.box()
            if props.selected_type_is_legacy:
                box.label(text=tr("legacy_badge"), icon="BOOKMARKS")
            box.label(text=f"{tr('size')}: {selected.get('width_m', 0)} x {selected.get('depth_m', 0)} x {selected.get('height_m', 0)} m")
            box.label(text=f"{tr('front_axis')}: {normalize_front_axis(selected.get('front_axis', 'y-'))}")
        else:
            layout.label(text=tr("select_preset_preview"))


classes = (
    MetaverseBoothUtilityPreferences,
    BoothConfigProperties,
    BOOTH_OT_generate_frame,
    BOOTH_OT_reset_config,
    BOOTH_OT_remove_generated,
    BOOTH_OT_toggle_frame_visibility,
    BOOTH_OT_toggle_arrow_visibility,
    BOOTH_OT_select_event,
    BOOTH_OT_select_variant,
    BOOTH_OT_select_type,
    BOOTH_MT_event_menu,
    BOOTH_MT_variant_menu,
    BOOTH_MT_type_menu,
    BOOTH_PT_panel,
)


def register():
    load_default_config_text()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.booth_config = PointerProperty(type=BoothConfigProperties)

    try:
        scenes = bpy.data.scenes
    except AttributeError:
        scenes = None

    if scenes is not None:
        for scene in scenes:
            scene.booth_config.config_json = DEFAULT_CONFIG_TEXT
            scene.booth_config.config_error = ""
            scene.booth_config.suppress_show_legacy_update = True
            try:
                scene.booth_config.show_legacy = get_default_show_legacy_value()
            finally:
                scene.booth_config.suppress_show_legacy_update = False
            reset_preset_selection_state(scene.booth_config)
            validate_config_text(scene.booth_config)


def unregister():
    del bpy.types.Scene.booth_config
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
