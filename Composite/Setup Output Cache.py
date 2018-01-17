'''
Blender Script - Setup Output Cache
    -- Composite Node 上に File Output ノードと、その出力先と同パスを示す Image Sequence ノードを作成する.

usage:
    - Composite Node Editor を開いている状態で当スクリプトを実行.
'''

import bpy
import time
import random
from functools import reduce

class Pref:
    margin = 100
    width_img = 170
    width_fo = 285
    use_custom_color = True
    #use_custom_color = False
    basedir = '//render/_outputcache'


def main():
    context = bpy.context

    space_data = get_nodeeditor_space(context)
    if space_data is None:
        return

    basename = 'Cache {}'.format(int(time.time()))
    path = '{}/{}/'.format(Pref.basedir, basename)

    for n in space_data.node_tree.nodes:
        n.select = False
    imgnode = space_data.node_tree.nodes.new('CompositorNodeImage')
    imgnode.location = space_data.edit_tree.view_center
    img = bpy.data.images.new(basename,1,1,alpha=True)
    img.source = 'SEQUENCE'
    img.filepath = '{}Image0001.png'.format(path)
    imgnode.frame_duration = 100000
    imgnode.image = img

    fonode = space_data.node_tree.nodes.new('CompositorNodeOutputFile')
    fonode.location = space_data.edit_tree.view_center
    fonode.base_path = path
    fonode.label = 'File Output - {}'.format(basename)

    ##
    imgnode.width = Pref.width_img
    fonode.width = Pref.width_fo
    imgnode.location.x -= Pref.margin
    fonode.location.x += Pref.margin

    if Pref.use_custom_color:
        color = (random.random(), random.random(), random.random())
        imgnode.use_custom_color = True
        imgnode.color = color
        fonode.use_custom_color = True
        fonode.color = color



def get_nodeeditor_space(context):
    if context.area.type == 'NODE_EDITOR' and context.space_data.tree_type == 'CompositorNodeTree':
        return context.space_data

    #ws = [context.window]
    ws = [context.window] + reduce(lambda a,b:a+b, [wm.windows[:] for wm in bpy.data.window_managers])

    for w in ws:
        for a in w.screen.areas:
            if a.type == 'NODE_EDITOR':
                for s in a.spaces:
                    if s.type == 'NODE_EDITOR' and s.tree_type == 'CompositorNodeTree':
                        return s
    return None


main()
