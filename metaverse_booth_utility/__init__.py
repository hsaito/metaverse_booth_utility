import json
import math
import os

import bpy
from bpy.props import EnumProperty, FloatProperty, PointerProperty, StringProperty
from bpy.types import Menu, Operator, Panel, PropertyGroup
from mathutils import Vector


def get_event_names(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []
    return [item.get("name") for item in data.get("events", []) if item.get("name")]


def get_variant_names(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []
    if not props.event_name:
        return []
    for event in data.get("events", []):
        if event.get("name") == props.event_name:
            return [item.get("name") for item in event.get("variants", []) if item.get("name")]
    return []


def get_type_names(props):
    try:
        data = get_config_data(props)
    except ValueError:
        return []
    if not props.event_name or not props.variant_name:
        return []
    for event in data.get("events", []):
        if event.get("name") != props.event_name:
            continue
        for variant in event.get("variants", []):
            if variant.get("name") == props.variant_name:
                return [item.get("name") for item in variant.get("types", []) if item.get("name")]
    return []

bl_info = {
    "name": "Metaverse Booth Utility",
    "blender": (3, 6, 0),
    "category": "Object",
    "version": (1, 0, 0),
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
FRONT_AXIS_ITEMS = (
    ("x", "+X", "Front points to +X"),
    ("-x", "-X", "Front points to -X"),
    ("y", "+Y", "Front points to +Y"),
    ("-y", "-Y", "Front points to -Y"),
    ("z", "+Z", "Front points to +Z"),
    ("-z", "-Z", "Front points to -Z"),
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
    valid_axes = {item[0] for item in FRONT_AXIS_ITEMS}
    if value in valid_axes:
        return value
    return "-y"


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
    width_m: FloatProperty(name="Width (m)", default=1.0, min=0.1)
    depth_m: FloatProperty(name="Depth (m)", default=1.0, min=0.1)
    height_m: FloatProperty(name="Height (m)", default=1.0, min=0.01)
    front_axis: EnumProperty(name="Front Axis", items=FRONT_AXIS_ITEMS, default="-y")
    advanced_open: bpy.props.BoolProperty(name="Advanced", default=False)

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
            self.report({"ERROR"}, props.config_error or "Unable to load preset JSON")
            return {"CANCELLED"}

        selected = self._get_selected_spec(config_data, props)
        if selected:
            event_name, variant_name, preset = selected
            preset_name = preset.get("name", "Custom")
        else:
            event_name = props.event_name or "Manual"
            variant_name = props.variant_name or "Custom"
            preset_name = props.type_name or "Custom"

        width = float(props.width_m)
        depth = float(props.depth_m)
        height = float(props.height_m)
        front_axis = normalize_front_axis(props.front_axis)

        self._remove_existing_objects()
        frame_obj = self._create_frame(width, depth, height, event_name, variant_name, preset_name)
        self._create_front_arrow(frame_obj, width, depth, height, front_axis)

        self.report({"INFO"}, f"Generated {event_name}/{variant_name}/{preset_name} ({width}x{depth} m)")
        return {"FINISHED"}

    def _get_selected_spec(self, config_data, props):
        event_name = props.event_name
        variant_name = props.variant_name
        type_name = props.type_name

        if not event_name or not variant_name or not type_name:
            return None

        for event in config_data.get("events", []):
            if event.get("name") != event_name:
                continue
            for variant in event.get("variants", []):
                if variant.get("name") != variant_name:
                    continue
                for preset in variant.get("types", []):
                    if preset.get("name") == type_name:
                        return event.get("name"), variant.get("name"), preset

        return None

    def _remove_existing_objects(self):
        for name in GENERATED_OBJECT_NAMES:
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

    def _create_frame(self, width, depth, height, event_name, variant_name, type_name):
        bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0), size=2.0)
        frame_obj = bpy.context.active_object
        frame_obj.name = "Booth Frame Reference"
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
        return frame_obj

    def _create_front_arrow(self, frame_obj, width, depth, height, front_axis):
        axis_vector = self._axis_to_vector(front_axis)
        base_location_world = Vector((0.0, 0.0, 0.0))

        bpy.ops.object.empty_add(type="SINGLE_ARROW", location=base_location_world)
        arrow = bpy.context.active_object
        arrow.name = "Booth Front Arrow"
        arrow.empty_display_type = "SINGLE_ARROW"
        arrow.empty_display_size = 1.0
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

        bpy.context.view_layer.update()

    def _axis_to_vector(self, axis):
        mapping = {
            "x": Vector((1.0, 0.0, 0.0)),
            "-x": Vector((-1.0, 0.0, 0.0)),
            "y": Vector((0.0, 1.0, 0.0)),
            "-y": Vector((0.0, -1.0, 0.0)),
            "z": Vector((0.0, 0.0, 1.0)),
            "-z": Vector((0.0, 0.0, -1.0)),
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
        props.event_name = ""
        props.variant_name = ""
        props.type_name = ""
        props.width_m = 1.0
        props.depth_m = 1.0
        props.height_m = 1.0
        props.front_axis = "-y"
        self.report({"INFO"}, "Reset booth preset selection")
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

        self.report({"INFO"}, f"Removed {removed_count} generated object(s)")
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
        return {"FINISHED"}


class BOOTH_OT_select_variant(Operator):
    bl_idname = "booth.select_variant"
    bl_label = "Select Variant"
    value: StringProperty()

    def execute(self, context):
        props = context.scene.booth_config
        props.variant_name = self.value
        props.type_name = ""
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

        for event in config_data.get("events", []):
            if event.get("name") != props.event_name:
                continue
            for variant in event.get("variants", []):
                if variant.get("name") != props.variant_name:
                    continue
                for preset in variant.get("types", []):
                    if preset.get("name") == props.type_name:
                        props.width_m = float(preset.get("width_m", props.width_m))
                        props.depth_m = float(preset.get("depth_m", props.depth_m))
                        props.height_m = float(preset.get("height_m", props.height_m))
                        props.front_axis = normalize_front_axis(preset.get("front_axis", props.front_axis))
                        return {"FINISHED"}
        return {"FINISHED"}


class BOOTH_MT_event_menu(Menu):
    bl_idname = "BOOTH_MT_event_menu"
    bl_label = "Events"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config
        for name in get_event_names(props):
            layout.operator("booth.select_event", text=name).value = name


class BOOTH_MT_variant_menu(Menu):
    bl_idname = "BOOTH_MT_variant_menu"
    bl_label = "Variants"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config
        for name in get_variant_names(props):
            layout.operator("booth.select_variant", text=name).value = name


class BOOTH_MT_type_menu(Menu):
    bl_idname = "BOOTH_MT_type_menu"
    bl_label = "Types"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config
        for name in get_type_names(props):
            layout.operator("booth.select_type", text=name).value = name


class BOOTH_PT_panel(Panel):
    bl_label = "Metaverse Booth Utility"
    bl_idname = "BOOTH_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Metaverse"

    def draw(self, context):
        layout = self.layout
        props = context.scene.booth_config

        layout.label(text="Booth presets")

        event_row = layout.row()
        event_row.label(text="Event")
        event_row.menu("BOOTH_MT_event_menu", text=props.event_name or "Select Event")

        variant_row = layout.row()
        variant_row.label(text="Variant")
        variant_row.enabled = bool(props.event_name)
        variant_row.menu("BOOTH_MT_variant_menu", text=props.variant_name or "Select Variant")

        type_row = layout.row()
        type_row.label(text="Type")
        type_row.enabled = bool(props.event_name and props.variant_name)
        type_row.menu("BOOTH_MT_type_menu", text=props.type_name or "Select Type")

        advanced_box = layout.box()
        advanced_box.prop(props, "advanced_open", text="Advanced", icon="TRIA_DOWN" if props.advanced_open else "TRIA_RIGHT")
        if props.advanced_open:
            advanced_box.prop(props, "width_m")
            advanced_box.prop(props, "depth_m")
            advanced_box.prop(props, "height_m")
            advanced_box.prop(props, "front_axis")

        row = layout.row()
        row.operator("booth.generate_frame", text="Generate")
        row.operator("booth.reset_config", text="Reset")

        layout.operator("booth.remove_generated", text="Remove Generated")

        if not validate_config_text(props):
            layout.label(text="Invalid preset JSON", icon="ERROR")
            return

        try:
            config_data = get_config_data(props)
        except ValueError:
            layout.label(text="Invalid preset JSON", icon="ERROR")
            return

        selected = None
        for event in config_data.get("events", []):
            if event.get("name") != props.event_name:
                continue
            for variant in event.get("variants", []):
                if variant.get("name") != props.variant_name:
                    continue
                for preset in variant.get("types", []):
                    if preset.get("name") == props.type_name:
                        selected = preset
                        break
                if selected:
                    break
            if selected:
                break

        if selected:
            box = layout.box()
            box.label(text=f"Size: {selected.get('width_m', 0)} x {selected.get('depth_m', 0)} x {selected.get('height_m', 0)} m")
            box.label(text=f"Front axis: {selected.get('front_axis', '-y')}")
        else:
            layout.label(text="Select a preset to preview")


classes = (
    BoothConfigProperties,
    BOOTH_OT_generate_frame,
    BOOTH_OT_reset_config,
    BOOTH_OT_remove_generated,
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
            validate_config_text(scene.booth_config)


def unregister():
    del bpy.types.Scene.booth_config
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
