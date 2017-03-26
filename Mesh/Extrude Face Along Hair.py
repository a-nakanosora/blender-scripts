'''
Blender Script - Extrude Face Along Hair

usage:
    - Particle Hair が有効な Mesh Object をアクティブにした状態で実行
    - Mesh Object の最初のParticle Hairが使用される.
    - 構築されたメッシュ(Extruded Mesh)にはUV, マテリアルが設定される.
      UV はパスの方向に沿ったものが、またマテリアルは元のMesh Objectの一番最初に設定されているものが当てられる.
    - Hair Dynamics を適用するには事前に Hair を Bake しておく必要がある.
'''

{'VERSION': (0,2)}

import bpy
from mathutils import Vector
from collections import namedtuple
import math

def main():
    run()

class Option:
    ignore_face_duplication = True
    use_twist = True

    #taper_profile = lambda t: 1.0
    #taper_profile = lambda t: 1.0-t
    taper_profile = lambda t: 1.0-t*t*(-2*t+3)

    #path_sample = 3
    #path_sample = 5
    path_sample = 10






def run():
    obj = bpy.context.object
    mw = obj.matrix_world
    hairs = obj.particle_systems[0].particles
    ExtrudeProfile = namedtuple('ExtrudeProfile', 'face_index, path')
    extprofs = []
    table_duplication = []
    for h in hairs:
        head = h.hair_keys[0]
        idx = get_closest_face(obj, mw*head.co)
        if idx > -1 and len(h.hair_keys) >= 2 \
         and (idx not in table_duplication if Option.ignore_face_duplication else True):
            path = sample_hair_path(h.hair_keys, Option.path_sample)
            extprofs.append( ExtrudeProfile(idx, path) )
            table_duplication.append(idx)

    mesh = obj.data
    seqobj = make_new_mesh_object('Extrude Face Along Hair')
    if len(mesh.materials):
        mat0 = mesh.materials[0]
        seqobj.data.materials.append(mat0)
    seqobj.matrix_world = obj.matrix_world
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = seqobj
    bpy.ops.object.mode_set(mode='EDIT')

    for ep in extprofs:
        head = ep.path[0]
        ds = [b-a for a,b in pairs(ep.path)]
        ds.append(ds[-1].copy())
        dirs = [d.normalized() for d in ds]
        assert len(ep.path) == len(dirs)

        f = mesh.polygons[ep.face_index]
        baseshape = [mesh.vertices[vidx].co - head for vidx in f.vertices]
        ext_seqs = []
        for v in baseshape:
            extpath = []
            for i,p in enumerate(ep.path):
                t = i/(len(ep.path)-1)
                n = dirs[i-1].cross(dirs[i]).normalized()  if i>0 else  Vector((0,0,1))
                theta = math.acos( clamp(-1.0, 1.0, dirs[0].dot(dirs[i])) )  \
                          if Option.use_twist else 0.0
                q = p + rot_on(n, theta, v * Option.taper_profile(t))
                extpath.append(q)
            ext_seqs.append(extpath)
        make_mesh_from_pathsequence(seqobj, ext_seqs, closed=True)

    bpy.ops.object.mode_set(mode='OBJECT')

def clamp(min, max, v):
    return min if v<min else max if v>max else v

def rot_on(n, theta, a):
    ## e.g. rot_on(Vector((1,0,0)), math.pi/180*90, Vector((0,0,2)))
    if theta==0.0:
        return a.copy()
    b = n*n.dot(a) + (a-n*n.dot(a))*math.cos(theta) - a.cross(n)*math.sin(theta)
    return b

def sample_hair_path(hair_keys, sample):
    return resample_points([h.co for h in hair_keys], sample)

def pairs(ls):
    return zip(ls[:-1], ls[1:])

def resample_points(ps0, resolution=10):
    assert len(ps0) >= 2
    assert resolution >= 2
    assert all(type(p) is Vector for p in ps0)

    lineLengthAll = 0
    for a,b in pairs(ps0):
        lineLengthAll += (b - a).length

    lineLength = 0
    head, tail = ps0[0], ps0[-1]
    ps = []
    ps.append(head.copy())
    i=0
    while i<len(ps0)-1:
        if len(ps) >= resolution-1:
            break

        a = ps0[i]
        b = ps0[i+1]
        ba = b-a
        d = ba.length

        refLen = lineLengthAll*len(ps)/(resolution-1)
        lineLengthNext = lineLength+d
        if d>0 and lineLength <= refLen and refLen < lineLengthNext:
            ss = (refLen-lineLength)/d
            p = a+ba*ss
            ps.append(p)
        else:
            lineLength = lineLengthNext
            i+=1
    ps.append(tail.copy())
    return ps

def make_new_mesh_object(name='mesh_from_script'):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.objects.link(obj)
    return obj

def get_closest_face(obj, p):
    ## p : Vector -- world coordinate
    plocal = obj.matrix_world.inverted() * p
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    face_idx = obj.closest_point_on_mesh(plocal)[-1]
    bpy.ops.object.mode_set( mode = 'EDIT' )
    return face_idx

def make_mesh_from_pathsequence(obj, paths, closed=False):
    assert type(obj) is bpy.types.Object
    assert type(paths) is list
    assert len(paths) >= 2
    for path in paths:
        assert type(path) is list
        assert all(type(v) is Vector for v in path)

    import bmesh
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    if closed:
        paths = paths+[paths[0]]

    paths.reverse() ## to flip normals

    verts_seq = []
    prev_verts = []
    for path in paths:
        verts = []
        verts.append( bm.verts.new(path[0]) )
        for i,pv in enumerate(path):
            if i==0:
                continue
            verts.append( bm.verts.new(pv) )

            u = verts[i-1]
            v = verts[i]
            bm.edges.new([u,v])

            if len(prev_verts) > i:
                pu = prev_verts[i-1]
                pv = prev_verts[i]
                bm.faces.new([pu, pv, v, u])
        prev_verts = verts
        verts_seq.append(verts)

    ## UV
    def _setuv():
        uv_name = 'UVMap - Extrude Face Along Hair'
        uv_layer = bm.loops.layers.uv.get(uv_name) or bm.loops.layers.uv.new(uv_name)
        tex_layer = bm.faces.layers.tex.get(uv_name) or bm.faces.layers.tex.new(uv_name)
        bm.normal_update()

        uv_coord_by_vertindex = {}
        attach_fs = []
        for i, verts in enumerate(verts_seq):
            y = i/(len(verts_seq)-1)
            for j,v in enumerate(verts):
                x = j/(len(verts)-1)
                uv_coord_by_vertindex[v.index] = Vector((x,y))
                for f in v.link_faces:
                    if f not in attach_fs:
                        attach_fs.append(f)

        for f in attach_fs:
            for l in f.loops:
                l[uv_layer].uv = uv_coord_by_vertindex[l.vert.index]
    _setuv()

    ##
    bm.normal_update()
    mesh.update()


main()
