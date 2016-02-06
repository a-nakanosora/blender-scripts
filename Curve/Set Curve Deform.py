{'VERSION': (1,1,0)}

import bpy

C = bpy.context

def main():
    curve = C.active_object
    sels = [o for o in C.selected_objects if o.type=='MESH']
    assert curve.type == 'CURVE'
    assert len(sels)>0

    for obj in sels:
        set_parent(obj, curve)
        set_deform(obj, curve)
        set_constraint(obj, curve)

def set_parent(obj, curve):
    obj.parent = curve

def set_deform(obj, curve):
    for m in obj.modifiers:
        if m.type=='CURVE':
            m.object = curve
            return

    m = obj.modifiers.new(name="Curve", type="CURVE")
    m.object = curve

def set_constraint(obj, curve):
    for c in obj.constraints:
        if c.type=='COPY_LOCATION':
            c.target = curve
            return

    c = obj.constraints.new(type='COPY_LOCATION')
    c.target = curve

main()