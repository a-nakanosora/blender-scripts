import bpy
bpy.a = bpy.context.copy()

class Object:pass
context = Object()
for n,v in bpy.a.items():
    context.__dict__[n] = v
bpy.b = context