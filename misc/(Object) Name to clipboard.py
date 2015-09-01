import bpy

def main():
    name = ''
    if bpy.context.mode == 'POSE' or bpy.context.mode == 'EDIT_ARMATURE':
        if bpy.context.active_bone:
            name = bpy.context.active_bone.name
    elif bpy.context.mode == 'OBJECT':
        if bpy.context.active_object:
            name = bpy.context.active_object.name
            
    print('copy name: ' + name)
    
    if name:
        bpy.context.window_manager.clipboard = name
    
main()