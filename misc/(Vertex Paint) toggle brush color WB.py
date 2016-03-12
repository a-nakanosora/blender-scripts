import bpy
act_brush = bpy.context.tool_settings.vertex_paint.brush
cl = act_brush.color
if (cl.r, cl.g, cl.b) != (1.0, 1.0, 1.0):
    cl.r = cl.g = cl.b = 1.0
else:
    cl.r = cl.g = cl.b = 0.0