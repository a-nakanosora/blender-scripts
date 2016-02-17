{'VERSION': (1,2,0)}

import bpy

C = bpy.context

def main():
    curve = C.active_object
    sels = [o for o in C.selected_objects if o.name != curve.name  and  o.type in {'MESH','CURVE'}]
    assert curve.type == 'CURVE'
    assert len(sels)>0

    for obj in sels:
        set_parent(obj, curve)
        set_dupli_frame(obj, curve)

def set_parent(obj, curve):
    obj.parent = curve

def set_dupli_frame(obj, curve):
    curve.data.use_path = True
    curve.data.use_path_follow = True

    obj.dupli_type = 'FRAMES'
    obj.use_dupli_frames_speed = False
    obj.dupli_frames_off = 5
    obj.location = (0,0,0)

main()