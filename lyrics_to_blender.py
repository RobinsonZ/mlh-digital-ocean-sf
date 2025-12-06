import re
import shutil
from dataclasses import dataclass

import bpy

source_blend = "empty.blend"
new_blend = "lyrics_project.blend"

shutil.copy(source_blend, new_blend)
bpy.ops.wm.open_mainfile(filepath=new_blend)


@dataclass
class Lyric:
    m: int
    s: int
    c: int
    text: str

    def frame(self, fps: int = 240) -> int:
        total_seconds = self.m * 60 + self.s + self.c / 100.0
        return int(total_seconds * fps) + 1


def parse_lrc_file(filepath: str) -> list[Lyric]:
    lyrics = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            match = re.match(r"\[(\d+):(\d+)\.(\d+)\]\s*(.*)", line.strip())
            if match:
                lyric = Lyric(
                    m=int(match.group(1)),
                    s=int(match.group(2)),
                    c=int(match.group(3)),
                    text=match.group(4),
                )
                lyrics.append(lyric)
    lyrics.sort(key=lambda x: x.frame())
    return lyrics


def create_text_material():
    mat = bpy.data.materials.new(name="TextMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    emission = nodes.new(type="ShaderNodeEmission")
    emission.inputs["Color"].default_value = (1, 1, 1, 1)
    emission.inputs["Strength"].default_value = 1.0
    output = nodes.new(type="ShaderNodeOutputMaterial")
    mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


_text_material = None


def add_text(x: float, y: float, text: str):
    global _text_material
    bpy.ops.object.text_add(location=(x, y, 0))
    text_obj = bpy.context.object
    text_obj.data.body = text
    bpy.context.view_layer.update()
    width = text_obj.dimensions.x
    text_obj.location.x = -width / 2
    text_obj.location.y = -0.5
    if _text_material is None:
        _text_material = create_text_material()
    text_obj.data.materials.append(_text_material)
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


lyrics = parse_lrc_file("songs/you_make_me_feel_remix.lrc")

for i, lyric in enumerate(lyrics):
    if not lyric.text:
        continue
    obj = add_text(0, 0, lyric.text)
    frame = lyric.frame()
    set_appear_keyframe(obj, frame)
    if i < len(lyrics) - 1:
        next_frame = lyrics[i + 1].frame()
    else:
        next_frame = frame + (240 * 2)
    set_disappear_keyframe(obj, next_frame)
    set_disappear_keyframe(obj, 0)

bpy.ops.wm.save_mainfile()
