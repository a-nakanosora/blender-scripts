{'VERSION': (0,0,1)}

import bpy
from collections import namedtuple

C = bpy.context

def main():
    assert C.mode == 'EDIT_CURVE'

    curve_obj = C.active_object
    splines_nurbs = [spline for spline in curve_obj.data.splines if spline.type=='NURBS']

    SelectedPointDetails = namedtuple('SelectedPointDetails', 'co, parent') # type: co :PointCoord, parent :Spline
    sel_ps = [] # type: List[ SelectedPointDetails ]
    for spline in splines_nurbs:
        for i,p in enumerate(spline.points):
            if p.select:
                sel_ps.append( SelectedPointDetails(p.co.copy(), spline) )

    bpy.ops.curve.select_all(action='DESELECT')
    for pd in sel_ps:
        bpy.ops.curve.select_all(action='DESELECT')
        p = get_point_by(pd.co, pd.parent)
        p.select = True
        bpy.ops.curve.select_next()
        bpy.ops.curve.select_previous()
        bpy.ops.curve.subdivide()

    bpy.ops.curve.select_all(action='DESELECT')
    def slide(p, a, b, t=0.02):
        p.co = a.co+(b.co-a.co)*t

    for pd in sel_ps:
        p = get_point_by(pd.co, pd.parent)

        q = get_prev(p, pd.parent)
        if q is not None:
            b = get_prev(q, pd.parent)
            slide(q, p, b)

        q = get_next(p, pd.parent)
        if q is not None:
            b = get_next(q, pd.parent)
            slide(q, p, b)

def get_point_by(co :'PointCoord', parent :'Spline') -> 'Optional[SplinePoint]':
    for i,p in enumerate(parent.points):
        if co == p.co:
            return p
    return None
def get_index_of(point :'SplinePoint', parent :'Spline') -> int:
    for i,p in enumerate(parent.points):
        if point.co == p.co:
            return i
    return -1
def get_next(point :'SplinePoint', parent :'Spline') -> 'Optional[SplinePoint]':
    i = get_index_of(point, parent)
    if i>=0 and i+1 < len(parent.points):
        return parent.points[i+1]
    return None
def get_prev(point :'SplinePoint', parent :'Spline') -> 'Optional[SplinePoint]':
    i = get_index_of(point, parent)
    if i>=0 and i-1 >= 0:
        return parent.points[i-1]
    return None

main()