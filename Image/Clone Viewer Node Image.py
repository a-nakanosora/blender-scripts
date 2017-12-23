'''
Blender Script - Clone Viewer Node Image
    -- clone 'Viewer Node' image correctly
'''

import bpy
import tempfile

def main():
    if 'Viewer Node' not in bpy.data.images:
        return
    img = bpy.data.images['Viewer Node']
    w,h = img.size
    img2 = bpy.data.images.new('Viewer Node Clone', w, h)

    ## make temporary image to avoid Color Management problem
    temppath = '{}/blenderscript_cloneviewnode.bmp'.format( bpy.context.user_preferences.filepaths.temporary_directory  \
                                                            or tempfile.gettempdir() )
    save_as_bmp(img, temppath)
    imgtemp = bpy.data.images.load(temppath)
    img2.pixels[:] = imgtemp.pixels[:]

    bpy.data.images.remove(imgtemp)
    print('clone Viewer Node: {}'.format(img2.name))

def save_as_bmp(img, path):
    scene = bpy.context.scene
    prev = scene.render.image_settings.file_format
    scene.render.image_settings.file_format = 'BMP'
    img.save_render(path)
    scene.render.image_settings.file_format = prev

main()
