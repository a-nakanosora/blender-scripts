{'VERSION': (0,5,3)}

class Pref:
    control_hook_number =  3

import bpy
from mathutils import Vector

def main():
    set_pref_by_args()

    if bpy.context.mode != 'POSE':
        raise Exception('execute in Pose Mode.')
    armature_object, parent_armature = get_armatures()
    chain = get_ordered_chain()
    ps = chain_main_locations(armature_object, chain, Pref.control_hook_number)
    curve = draw_opened_curve(ps)
    attach_splineIK(chain, curve)
    make_controller_hooks(curve, parent_armature)

def get_armatures():
    if len([obj for obj in bpy.context.selected_objects if obj.type != 'ARMATURE']):
        raise Exception('invalid selected objects. (A)')

    if len(bpy.context.selected_objects) == 1:
        armature = bpy.context.active_object
        parent_armature = None
    elif len(bpy.context.selected_objects) == 2:
        armature = bpy.context.active_object
        parent_armature = [obj for obj in bpy.context.selected_objects if obj != armature][0]
    else:
        raise Exception('invalid selected objects. (B)')

    return (armature, parent_armature)

def set_pref_by_args():
    for n,v in get_args_from_my_filename().items():
        if n=='hooks':
            Pref.control_hook_number = int(v)

def get_args_from_my_filename():
    def get_args_from_filename(filename):
        import re
        args = {}
        for arg_str in re.findall(r'(\[.+?\])', filename):
            for (arg_name, arg_value) in re.findall(r'\[(.+?)=(.+)\]', arg_str):
                args[arg_name] = arg_value
        return args

    import os
    return get_args_from_filename( os.path.basename(__file__) )

def make_controller_hooks(curve, parent_armature):
    scene = bpy.context.scene

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action="DESELECT")
    curve.select = True
    scene.objects.active = curve
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    bps = curve.data.splines[0].bezier_points
    for bp in bps:
        bp.select_control_point = False
        bp.select_right_handle = False
        bp.select_left_handle = False

    if parent_armature:
        armature = parent_armature
        amt_data = armature.data
    else:
        amt_data = bpy.data.armatures.new("SplineIK_Control_Hooks_Data")
        armature = bpy.data.objects.new("SplineIK_Control_Hooks", amt_data)
        bpy.context.scene.objects.link(armature)

        armature.location = curve.location
    scene.objects.active = armature

    tail_offset = Vector((0,0,1))
    co_delta = curve.location - armature.location
    import random
    some_str = "".join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for x in range(10)])
    bpy.ops.object.mode_set(mode='EDIT')
    for i in range(len(bps)):
        bone = amt_data.edit_bones.new('HookBone_%s_%d' % (some_str, i))
        bone.head = bps[i].co + co_delta.copy()
        bone.tail = bone.head + tail_offset

    bpy.ops.object.mode_set(mode='OBJECT')

    scene.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    scene.objects.active = curve
    bpy.ops.object.mode_set(mode='EDIT')
    l0 = len(armature.data.bones) - len(bps)
    for i in range(len(bps)):
        mod_name = 'Hook_%d' % i
        hook_mod = curve.modifiers.new(mod_name, 'HOOK')
        hook_mod.object = armature
        hook_mod.subtarget = armature.data.bones[l0+i].name

        bps = curve.data.splines[0].bezier_points
        bp = bps[i]
        bp.select_control_point = True
        if i==0 or i==len(bps)-1:
            bp.select_right_handle = True
            bp.select_left_handle = True
        bpy.ops.object.hook_assign(modifier=mod_name)
        bp.select_control_point = False
        bp.select_right_handle = False
        bp.select_left_handle = False
        bpy.ops.object.hook_reset(modifier=curve.modifiers[i].name)

    bpy.ops.object.mode_set(mode='OBJECT')

    curve.show_x_ray = True
    armature.show_x_ray = True
    armature.draw_type = 'WIRE'
    armature.data.draw_type = 'STICK'

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action="DESELECT")
    armature.select = True
    scene.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

def attach_splineIK(pose_bone_chain, curve):
    posebone_last = pose_bone_chain[-1]
    constraints = posebone_last.constraints

    if not 'Spline IK' in constraints:
        constraints.new("SPLINE_IK")
    con = constraints['Spline IK']
    con.target = curve
    con.chain_count = len(pose_bone_chain)

def draw_opened_curve(points):
    curvedata = bpy.data.curves.new(name='Curve_SplineIKTarget_Data',type='CURVE')
    curvedata.dimensions = '3D'
    curvedata.show_handles = False
    curve = bpy.data.objects.new("Curve_SplineIKTarget", curvedata)
    bpy.context.scene.objects.link(curve)

    spline = curvedata.splines.new('BEZIER')
    bezier_points = spline.bezier_points
    bezier_points.add( len(points)-1 )

    for i in range(len(points)):
        bezier_points[i].co = points[i]

    bp = bezier_points[0]
    bp.handle_left = bp.co
    bp.handle_right = bp.co

    bp = bezier_points[-1]
    bp.handle_left = bp.co
    bp.handle_right = bp.co

    for i in range(1, len(points)-1):
        bp = bezier_points[i]
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    return curve

def chain_main_locations(armature_object, pose_bone_chain, n):
    if n<2:
        raise Exception('chain_main_locations Error: n<2.')

    armature = armature_object.data
    pp_prev = armature.pose_position
    armature.pose_position="REST"
    bpy.context.scene.update()
    chain = pose_bone_chain
    length_all = 0
    for bone in chain:
        length_all += calc_length(bone)

    start_pos = chain[0].head
    end_pos = chain[-1].tail

    middle_poses = []
    if n==2:
        pass
    elif n==3:
        middle_pos = None
        length_sum = 0
        for bone in chain:
            length_sum += calc_length(bone)
            if length_sum/length_all >= 0.5:
                middle_poses.append( (bone.tail + bone.head)/2 )
                break
    else:
        i = 0
        l = len(chain)
        pos_max = n-1
        pos_count = 1
        length_sum = 0
        length_sum += calc_length(chain[0])
        while i<l and pos_count<pos_max:
            bone = chain[i]
            if length_sum/length_all >= pos_count/pos_max:
                middle_poses.append( (bone.tail + bone.head)/2 )
                pos_count += 1
                continue
            i+=1
            length_sum += calc_length(chain[i])

    pos_sequence = [start_pos] + middle_poses + [end_pos]

    armature.pose_position = pp_prev
    bpy.context.scene.update()

    loc = armature_object.location
    return [p0+loc for p0 in pos_sequence]

def calc_length(bone):
    return (bone.head - bone.tail).length

def get_ordered_chain():
    sel_pbs = bpy.context.selected_pose_bones

    chain_root = None
    for bone in sel_pbs:
        if not bone.parent in sel_pbs:
            if chain_root:
                raise Exception('get_ordered_chain Error: the chain root not unique.')
            chain_root = bone

    pose_bone_ordered_chain = []
    rest = sel_pbs.copy()
    bone = chain_root

    while rest:
        if not bone in rest:
            raise Exception('get_ordered_chain Error: invalid chain.')
        pose_bone_ordered_chain.append(bone)
        rest.remove(bone)
        if len(bone.children) > 1:
            raise Exception('get_ordered_chain Error: (branched chain) not supported yet.')
        bone = bone.child

    return pose_bone_ordered_chain

main()