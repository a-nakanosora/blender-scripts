import bpy
for c in [obj.data for obj in bpy.context.selected_objects if obj.type=='CURVE']:
    c.bevel_resolution = 0

    c.fill_mode = 'HALF'

    if c.resolution_u > 3:
        c.resolution_u = 3
    c.render_resolution_u = 0

    for spline in c.splines:
        if spline.type == 'NURBS':
            spline.order_u = 3

    c.show_handles = False
    c.show_normal_face = False