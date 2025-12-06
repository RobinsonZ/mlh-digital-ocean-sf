import shutil

import bpy

source_blend = "empty.blend"
new_blend = "lyrics_project.blend"

shutil.copy(source_blend, new_blend)

bpy.ops.wm.open_mainfile(filepath=new_blend)


def add_text(x: float, y: float, text: str):
    bpy.ops.object.text_add(location=(x, y, 0))
    text_obj = bpy.context.object
    text_obj.data.body = text

    width = text_obj.dimensions.x
    height = text_obj.dimensions.y

    text_obj.location.x = -width / 2
    text_obj.location.y = -height / 2

    return text_obj


def set_appear_keyframe(obj, frame: int):
    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert(data_path="hide_render", frame=frame - 1)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame - 1)
    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=frame)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)


def set_disappear_keyframe(obj, frame: int):
    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=frame - 1)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame - 1)
    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert(data_path="hide_render", frame=frame)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)


obj = add_text(-1, 0, "Text")
set_appear_keyframe(obj, 20)
set_disappear_keyframe(obj, 100)

bpy.ops.wm.save_mainfile()
