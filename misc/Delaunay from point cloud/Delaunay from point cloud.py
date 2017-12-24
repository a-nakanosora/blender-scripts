'''
Blender Script - Delaunay from Point Cloud
                 -- 頂点群に対して3Dドロネー分割を行う.

usage:
    * メッシュオブジェクトをアクティブにした状態でスクリプトを実行.
      そのメッシュの頂点群を入力として3Dドロネー分割を行い、結果としてエッジと表層フェースをメッシュにして出力します.
'''

{'VERSION': (0,2,1)}


import bpy
import bmesh
import math
from mathutils import Vector


class Tetrahedron:
    def __init__(self, v1,v2,v3,v4):
        self.vertices = [v1,v2,v3,v4] # type: List[Vector]
        self.o = None
        self.r = -1
        self.get_center_circumcircle()

    ## 外接円
    def get_center_circumcircle(self):
        v1 = self.vertices[0]
        v2 = self.vertices[1]
        v3 = self.vertices[2]
        v4 = self.vertices[3]

        A = [
            [v2.x - v1.x, v2.y-v1.y, v2.z-v1.z],
            [v3.x - v1.x, v3.y-v1.y, v3.z-v1.z],
            [v4.x - v1.x, v4.y-v1.y, v4.z-v1.z]
        ]
        b = [
            0.5 * (v2.x*v2.x - v1.x*v1.x + v2.y*v2.y - v1.y*v1.y + v2.z*v2.z - v1.z*v1.z),
            0.5 * (v3.x*v3.x - v1.x*v1.x + v3.y*v3.y - v1.y*v1.y + v3.z*v3.z - v1.z*v1.z),
            0.5 * (v4.x*v4.x - v1.x*v1.x + v4.y*v4.y - v1.y*v1.y + v4.z*v4.z - v1.z*v1.z)
        ];
        x = [0,0,0]
        if self.gauss(A, b, x) == 0:
            self.o = None
            self.r = -1
        else:
            self.o = Vector(x)
            self.r = (self.o - v1).length

    def gauss(self, a, b, x):
        n = len(a)
        ip = [0 for _ in range(n)]
        det = self.lu(a, ip)
        if det != 0:
            self.solve(a,b,ip,x)
        return det

    def lu(self, a, ip): ## LU分解による方程式の解法
        n = len(a)
        weight = [0 for _ in range(n)]

        for k in range(n):
            ip[k] = k;
            u = 0
            for j in range(n):
                t = abs(a[k][j])
                if t > u:
                    u = t

            if u == 0:
                return 0
            weight[k] = 1/u

        det = 1
        for k in range(n):
            u = -1
            m = 0;
            for i in range(k,n):
                ii = ip[i]
                t = abs(a[ii][k]) * weight[ii]
                if t>u:
                    u = t
                    m = i

            ik = ip[m]
            if m != k:
                ip[m] = ip[k]
                ip[k] = ik
                det = -det

            u = a[ik][k]
            det *= u;
            if u == 0:
                return 0
            for i in range(k+1, n):
                ii = ip[i]
                a[ii][k] /= u
                t = a[ii][k]
                for j in range(k+1, n):
                    a[ii][j] -= t * a[ik][j]
        return det


    def solve(self, a, b, ip, x):
        n = len(a)
        for i in range(n):
            ii = ip[i]
            t = b[ii]
            for j in range(i):
                t -= a[ii][j] * x[j]
            x[i] = t

        for i in range(n-1, 0-1, -1):
            t = x[i]
            ii = ip[i]
            for j in range(i+1, n):
                t -= a[ii][j] * x[j]
            x[i] = t / a[ii][i]

    def equals(self, t):
        count = 0
        for p1 in self.vertices:
            for p2 in t.vertices:
                #if p1.x == p2.x and p1.y == p2.y and p1.z == p2.z:
                if p1 == p2:
                    count += 1
        return count == 4

    def get_lines(self):
        v1 = self.vertices[0]
        v2 = self.vertices[1]
        v3 = self.vertices[2]
        v4 = self.vertices[3]

        lines = []
        lines.append( Line(v1, v2) )
        lines.append( Line(v1, v3) )
        lines.append( Line(v1, v4) )
        lines.append( Line(v2, v3) )
        lines.append( Line(v2, v4) )
        lines.append( Line(v3, v4) )
        return lines


class Line:
    def __init__(self, start, end):
        self.start = start  # type: Vector
        self.end = end      # type: Vector

    ## 始点と終点をひっくり返す
    def reverse(self):
        tmp = self.start
        self.start = self.end
        self.end = tmp

    def equals(self, l):
        return (self.start == l.start and self.end == l.end) or (self.start == l.end and self.end == l.start)



class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = v1 # type: Vector
        self.v2 = v2
        self.v3 = v3

    ## 法線を求める
    ## 頂点は左回りの順であるとする
    def get_normal(self):
        edge1 = self.v2 - self.v1
        edge2 = self.v3 - self.v1

        normal = edge1.cross(edge2).normalized()
        return normal

    ## 面を裏返す（頂点の順序を逆に）
    def turn_back(self):
        tmp = self.v3
        self.v3 = self.v1
        self.v1 = tmp

    ## 線分のリストを得る
    def get_lines(self):
        l = [
            Line(self.v1, self.v2),
            Line(self.v2, self.v3),
            Line(self.v3, self.v1)
            ]
        return l

    def equals(self, t):
        lines1 = self.get_lines()
        lines2 = t.get_lines()

        cnt = 0
        for l1 in lines1:
            for l2 in lines2:
                if l1.equals(l2):
                    cnt+=1
        return cnt == 3



class Delaunay:
    @classmethod
    def make_tetras(cls, vertices):
        ## 1    : 点群を包含する四面体を求める
        ##   1-1: 点群を包含する球を求める
        v_max = Vector((-999, -999, -999))
        v_min = Vector(( 999,  999,  999))
        for v in vertices:
            if v_max.x < v.x: v_max.x = v.x
            if v_max.y < v.y: v_max.y = v.y
            if v_max.z < v.z: v_max.z = v.z
            if v_min.x > v.x: v_min.x = v.x
            if v_min.y > v.y: v_min.y = v.y
            if v_min.z > v.z: v_min.z = v.z

        center = (v_max - v_min)*0.5

        r = max([(center-v).length for v in vertices]) ## 半径
        r += 0.1 ## ちょっとおまけ

        ## 1-2: 球に外接する四面体を求める
        v1 = Vector(( center.x
                    , center.y + 3.0*r
                    , center.z
                    ))

        v2 = Vector(( center.x - 2.0*math.sqrt(2)*r
                    , center.y - r
                    , center.z
                    ))

        v3 = Vector(( center.x + math.sqrt(2)*r
                    , center.y - r
                    , center.z + math.sqrt(6)*r
                    ))

        v4 = Vector(( center.x + math.sqrt(2)*r
                    , center.y - r
                    , center.z - math.sqrt(6)*r
                    ))

        outer = [v1, v2, v3, v4]
        tetras = []
        tetras.append(Tetrahedron(v1, v2, v3, v4))


        def to_identifier(tetra):
            vs = sorted(tetra.vertices, key=lambda v:v.x)
            a,b,c,d = vs
            return '{}/{}/{}//{}/{}/{}//{}/{}/{}//{}/{}/{}'.format( a.x,a.y,a.z
                                                                  , b.x,b.y,b.z
                                                                  , c.x,c.y,c.z
                                                                  , d.x,d.y,d.z
                                                                  )
        def __scan__(hash_tetras, hash_added, tetra):
            ide = to_identifier(tetra)
            if ide in hash_added:
                if ide in hash_tetras:
                    del hash_tetras[ide]
                return
            hash_tetras[ide] = tetra
            hash_added[ide] = True


        ## 幾何形状を動的に変化させるための一時リスト
        for v in vertices:
            hash_tetras = {}
            hash_added = {}

            tmp_tlist = []
            for t in tetras:
                if t.o is not None  and  t.r > (v - t.o).length:
                    tmp_tlist.append(t)

            for t1 in tmp_tlist:
                ## まずそれらを削除
                tetras.remove(t1)

                v1 = t1.vertices[0]
                v2 = t1.vertices[1]
                v3 = t1.vertices[2]
                v4 = t1.vertices[3]
                __scan__(hash_tetras, hash_added, Tetrahedron(v1, v2, v3, v))
                __scan__(hash_tetras, hash_added, Tetrahedron(v1, v2, v4, v))
                __scan__(hash_tetras, hash_added, Tetrahedron(v1, v3, v4, v))
                __scan__(hash_tetras, hash_added, Tetrahedron(v2, v3, v4, v))

            for t in hash_tetras.values():
                tetras.append( t )

        def cleanup(tetras, t4):
            for p1 in t4.vertices:
                for p2 in outer:
                    #if p1.x == p2.x and p1.y == p2.y and p1.z == p2.z:
                    if p1 == p2:
                        tetras.remove(t4)
                        return

        for t4 in tetras.copy():
            cleanup(tetras, t4)

        return tetras


    @classmethod
    def get_edges(cls, tetras):
        hashtable = {}
        def to_identifier(line):
            a = line.start
            b = line.end
            if b.x < a.x:
                b,a = a,b
            return '{}/{}/{}//{}/{}/{}'.format(a.x,a.y,a.z, b.x,b.y,b.z)

        edges = []
        for t in tetras:
            for l1 in t.get_lines():
                ide = to_identifier(l1)
                if ide not in hashtable:
                    hashtable[ide] = True
                    edges.append(l1)
        return edges

    @classmethod
    def get_surfaces(cls, tetras):
        ## 面を求める

        hashtable = {}
        def to_identifier(tri):
            a,b,c = sorted([tri.v1, tri.v2, tri.v3], key=lambda v:v.x)
            return '{}/{}/{}//{}/{}/{}//{}/{}/{}'.format( a.x,a.y,a.z
                                                        , b.x,b.y,b.z
                                                        , c.x,c.y,c.z
                                                        )
        def __scan__(tri, opposite_vert):
            ide = to_identifier(tri)
            if ide in hashtable:
                del hashtable[ide]
                return
            hashtable[ide] = tri

            ## 面の向きを決める
            n = tri.get_normal()
            if n.dot(tri.v1) < n.dot(opposite_vert):
                tri.turn_back()


        for t in tetras:
            v1 = t.vertices[0]
            v2 = t.vertices[1]
            v3 = t.vertices[2]
            v4 = t.vertices[3]

            tri1 = Triangle(v1, v2, v3)
            tri2 = Triangle(v1, v3, v4)
            tri3 = Triangle(v1, v4, v2)
            tri4 = Triangle(v4, v3, v2)

            __scan__(tri1, v4)
            __scan__(tri2, v2)
            __scan__(tri3, v3)
            __scan__(tri4, v1)

        surface_tris = list( hashtable.values() )



        hashtable_edges = {}
        def to_identifier_edge(line):
            a = line.start
            b = line.end
            if b.x < a.x:
                b,a = a,b
            return '{}/{}/{}//{}/{}/{}'.format(a.x,a.y,a.z, b.x,b.y,b.z)

        def __scan_edge__(line):
            ide = to_identifier_edge(line)
            if ide in hashtable_edges:
                del hashtable_edges[ide]
                return
            hashtable_edges[ide] = line

        for tri in surface_tris:
            for l in tri.get_lines():
                __scan_edge__(l)

        surface_edges = list( hashtable_edges.values() )

        return surface_edges, surface_tris


    @classmethod
    def verts_to_edges(cls, vertices):
        tetras = cls.make_tetras(vertices)
        edges = cls.get_edges(tetras)
        return edges

    @classmethod
    def verts_to_surfaces(cls, vertices):
        tetras = cls.make_tetras(vertices)
        surface_edges, surface_tris = cls.get_surfaces(tetras)
        return surface_edges, surface_tris

    #@classmethod
    #def from_vertices(cls, vertices):
    #    tetras = cls.make_tetras(vertices)
    #    edges = cls.get_edges(tetras)
    #    surface_edges, surface_tris = cls.get_surfaces(tetras)
    #    return tetras, edges, surface_edges, surface_tris

    @classmethod
    def from_vertices(cls, vertices):
        import time
        a = time.time()
        tetras = cls.make_tetras(vertices)
        b = time.time()
        edges = cls.get_edges(tetras)
        c = time.time()
        surface_edges, surface_tris = cls.get_surfaces(tetras)
        d = time.time()

        print('make_tetras time:', b-a)
        print('get_edges time:', c-b)
        print('get_surfaces time:', d-c)
        return tetras, edges, surface_edges, surface_tris












##
def test():
    vs = [ Vector((0,0,0))
         , Vector((1,0,0))
         , Vector((1,1,0))
         , Vector((1,1,1))
         , Vector((2,1,1))
         , Vector((0,2,1))
         , Vector((0,2,3))
         , Vector((5,2,3))
         ]
    tetras, edges, surface_edges, surface_tris = Delaunay.from_vertices(vs)

    print('{} Delaunay surface_tris'.format(len(surface_tris)))
    for tri in surface_tris:
        print(tri.v1, tri.v2, tri.v3)


def test_from_vertices():
    ''' 選択中のオブジェクトの頂点群を入力として3Dドロネー分割による各エッジ＆表層のフェースを取り出し、それらをメッシュとして生成する.
        端部を共有しているエッジでもそれぞれの頂点は位置が同じだけで独立しているので、Remove Doublesを忘れずに.
    '''
    import time
    import random
    random_factor = .01
    print('=== test_from_vertices() ===')

    obj = bpy.context.active_object
    ''' random_factor - 頂点間が完全に等距離の時だと過剰に分割されてしまい正しい結果が得られないことがあるため、あらかじめある程度揺らぎをもたせておく.
    '''
    #verts_co = [v.co for v in obj.data.vertices]
    verts_co = [v.co + Vector(((random.random()-0.5)*random_factor
                              ,(random.random()-0.5)*random_factor
                              ,(random.random()-0.5)*random_factor)) for v in obj.data.vertices]
    print('verts:', len(verts_co))

    t0 = time.time()
    tetras, edges, surface_edges, surface_tris = Delaunay.from_vertices(verts_co)
    t1 = time.time()
    print('Delaunay.from_vertices() time:', t1-t0)

    delaunay_edge_mesh_obj = make_mesh_edges( edges )
    delaunay_edge_mesh_obj.location = obj.location
    delaunay_face_mesh_obj = make_mesh_faces( surface_tris )
    delaunay_face_mesh_obj.location = obj.location
    print('edges:', len(edges))
    print('surface_tris:', len(surface_tris))
    print('=== done ===')



def make_new_mesh_object(name='delaunay_mesh'):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.objects.link(obj)
    return obj

def make_mesh_edges(delaunay_edges):
    bm = bmesh.new()
    for line in delaunay_edges:
        v0 = bm.verts.new(line.start)
        v1 = bm.verts.new(line.end)
        bm.edges.new([v0,v1])

    obj = make_new_mesh_object('delaunay_edge')
    mesh = obj.data
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    return obj

def make_mesh_faces(delaunay_tris):
    bm = bmesh.new()
    for tri in delaunay_tris:
        v1 = bm.verts.new(tri.v1)
        v2 = bm.verts.new(tri.v2)
        v3 = bm.verts.new(tri.v3)
        bm.faces.new([v1,v2,v3])

    obj = make_new_mesh_object('delaunay_surface')
    mesh = obj.data
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    return obj



if __name__ == '__main__':
    #test()
    test_from_vertices()