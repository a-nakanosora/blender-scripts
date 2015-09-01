import bpy
print('paths:')
for s in bpy.utils.blend_paths():
	print(s)
print('')