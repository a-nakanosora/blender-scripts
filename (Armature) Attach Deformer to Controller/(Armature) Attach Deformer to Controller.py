import bpy

def get_subject_armatures_from_selection():
    act = bpy.context.active_object
    selection = bpy.context.selected_objects

    if len(selection) != 2:
        raise Exception('selected objects length not 2.')
    if not act in selection:
        raise Exception('no active object in selected objects.')

    def head(iter): return next(iter)
    deformer_armature = head( filter(lambda v:v!=act, selection) )
    controller_armature = act

    return [deformer_armature, controller_armature]

def main():
    [deformer_armature, controller_armature] = get_subject_armatures_from_selection()

    for controller_bone in controller_armature.pose.bones:
        bone_name = controller_bone.name
        if not bone_name in deformer_armature.pose.bones:
            continue
        bone = deformer_armature.pose.bones[bone_name]
        constraints = bone.constraints
        if not 'Copy Transforms' in constraints:
            constraints.new("COPY_TRANSFORMS")
        c = constraints['Copy Transforms']
        c.target = controller_armature
        c.subtarget = bone_name

main()