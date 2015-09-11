{'VERSION': (0,1,0)}

import bpy

def get_subject_pose_bones():
    act = bpy.context.active_pose_bone
    selection = bpy.context.selected_pose_bones

    if len(selection) != 2:
        raise Exception('selected pose bones length not 2.')
    if not act in selection:
        raise Exception('no active pose bone in selection.')

    dest = act
    src = [pb for pb in selection if pb != act][0]
    return src, dest

def main():
    if bpy.context.mode != "POSE":
        raise Exception("run in pose mode.")

    pb_src, pb_dest = get_subject_pose_bones()
    armature = bpy.context.active_object

    bpy.ops.object.mode_set(mode='EDIT')
    ebs = armature.data.edit_bones
    stretcher = ebs.new("Stretcher_Bone")
    stretcher.head = pb_src.head.copy()
    stretcher.tail = pb_dest.head.copy()

    bpy.ops.object.mode_set(mode='POSE')
    stretcher_pb = armature.pose.bones[ stretcher.name ]

    cl = stretcher_pb.constraints.new("COPY_LOCATION")
    cl.target = armature
    cl.subtarget = pb_src.name

    st = stretcher_pb.constraints.new("STRETCH_TO")
    st.target = armature
    st.subtarget = pb_dest.name

main()
