'''
Blender Script - Symmetrize GP Strokes
    -- アクティブな Grease Pencil Layer のストロークをX軸方向(+X -> -X)に反転コピーする.


- ミラー方向となる軸は、下に挙げる各条件によって異なる座標が採用される：
    1. もしGP Layerに`Parent`が設定されてあれば、そのオブジェクトのローカル座標上でのX軸
    2. 選択オブジェクトがあればそのオブジェクトのローカル座標
    3. 上記に該当しない場合はグローバル空間でのX軸方向

'''

import bpy
from mathutils import Matrix
from collections import namedtuple

def main():
    GPStrokePointDetail = namedtuple('GPStrokePointDetail', 'co, pressure, strength')
    GPStrokeDetail = namedtuple('GPStrokeDetail', 'points, colorname, line_width, mirroraxis')

    scene = bpy.context.scene
    gp = scene.grease_pencil
    gpl = gp.layers.active
    fl = gpl.active_frame

    next_strokes = []

    for st in fl.strokes:
        pts = st.points
        next_pts = []

        if gpl.parent:
            obj = gpl.parent
            if obj.type=='ARMATURE' and gpl.parent_bone and gpl.parent_bone in obj.pose.bones:
                pb = obj.pose.bones[gpl.parent_bone]
                mirroraxis = pb.matrix.copy()
            else:
                mirroraxis = obj.matrix_world.copy()
            ## <!> force recalc point coords
            gpl.parent = None
            gpl.parent = obj
        elif bpy.context.selected_objects:
            obj = bpy.context.active_object if bpy.context.active_object in bpy.context.selected_objects \
                                            else bpy.context.selected_objects[0]
            mirroraxis = obj.matrix_world.copy()
        else:
            mirroraxis = Matrix()

        m_inv = mirroraxis.inverted()
        for p in pts:
            if (m_inv*p.co).x >= 0:
                next_pts.append( GPStrokePointDetail(p.co.copy(), p.pressure, p.strength) )
            else:
                if next_pts:
                    next_strokes.append( GPStrokeDetail(next_pts, st.colorname, st.line_width, mirroraxis) )
                    next_pts = []
        if next_pts:
            next_strokes.append( GPStrokeDetail(next_pts, st.colorname, st.line_width, mirroraxis) )


    ## re-stroke
    mirror_x = Matrix()
    mirror_x[0][0] = -1

    for st in list(fl.strokes):
        fl.strokes.remove(st)

    for nst in next_strokes:
        st = fl.strokes.new(nst.colorname)
        st.draw_mode = '3DSPACE'
        st.line_width = nst.line_width
        pts = st.points
        pts.add(len(nst.points))
        for i,np in enumerate(nst.points):
            p = pts[i]
            p.co = np.co.copy()
            p.pressure = np.pressure
            p.strength = np.strength

        ## add a mirrored stroke
        st = fl.strokes.new(nst.colorname)
        st.draw_mode = '3DSPACE'
        st.line_width = nst.line_width
        pts = st.points
        pts.add(len(nst.points))
        m = nst.mirroraxis
        for i,np in enumerate(nst.points):
            p = pts[i]
            p.co = m*mirror_x*m.inverted()*np.co.copy()
            p.pressure = np.pressure
            p.strength = np.strength


main()
