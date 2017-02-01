'''
Blender Script - Image Processing - Morphological Petit Thinning
    -- Morphology(Dilation)ベースの細線化処理を行う.


usage:
    - Pref.emptyrange, .emptythres, .dilation_max_depth を調節して当スクリプト実行
    - 原画像'A'(==bpy.data.images['A']) に対し処理を施した結果を'B'に出力する.
    - 画像はノンアルファなグレースケール画像であること. RGBAの内R成分のみが使用される.
    - 画像は白地に黒線が描かれているものとする.


requires:
    - Pillow (PIL)

'''


import bpy ## BPY
#import numpy as np
from PIL import Image, ImageFilter

import time


class Pref:
    #emptyrange, emptythres = 3, 0.9
    #emptyrange, emptythres = 5, 0.95
    #emptyrange, emptythres = 5, 0.99
    emptyrange, emptythres = 6, 0.95
    #emptyrange, emptythres = 7, 0.99
    #emptyrange, emptythres = 7, 0.98
    #emptyrange, emptythres = 7, 0.9
    #emptyrange, emptythres = 10, 0.95
    #emptyrange, emptythres = 20, 0.97

    #dilation_max_depth = 1
    dilation_max_depth = 5
    #dilation_max_depth = 10

    temppath_in = 'd:/temp/bpytemp_in.png'
    temppath_out = 'd:/temp/bpytemp_out.png'



def main():
    print('Petit Thinning')
    t0 = time.time()

    blimage_save('A', Pref.temppath_in) ## BPY

    pimg = Image.open(Pref.temppath_in).convert("L")
    pimg2 = process(pimg)
    pimg2.save(Pref.temppath_out)

    blimage_load('B', Pref.temppath_out) ## BPY

    t1 = time.time()
    print('main time:', t1-t0)


def blimage_save(imgname, path):
    def save_as_png(img, path):
        s = bpy.context.scene.render.image_settings
        prev, prev2, prev3 = s.file_format, s.color_mode, s.compression
        s.file_format, s.color_mode, s.compression = 'PNG', 'RGBA', 0
        img.save_render(bpy.path.abspath(path))
        s.file_format, s.color_mode, s.compression = prev, prev2, prev3

    blimg_in = bpy.data.images[imgname]
    save_as_png(blimg_in, path)


def blimage_load(imgname, path):
    def samesize(blimg1, blimg2):
        return blimg1.size[:] == blimg2.size[:] and len(blimg1.pixels) == len(blimg2.pixels)

    def delete_blimage(blimg):
        blimg.user_clear()
        bpy.data.images.remove(blimg)

    blimg_temp = bpy.data.images.load(path)
    blimg_temp.name = 'blimg_temp'
    blimg_prev = bpy.data.images[imgname] if imgname in bpy.data.images else None

    if blimg_prev is not None and samesize(blimg_prev, blimg_temp):
        blimg_prev.pixels = blimg_temp.pixels[:]
    else:
        if blimg_prev is not None:
            delete_blimage(blimg_prev)
        width, height = blimg_temp.size
        img = bpy.data.images.new(imgname, width, height, alpha=True)
        assert len(blimg_temp.pixels) == width*height*4, 'blimage_load# unsupported case.'
        assert len(blimg_temp.pixels) == len(img.pixels), 'blimage_load# unsupported case 2.'
        img.generated_color = (0,0,0,0)
        img.use_fake_user = True
        img.pixels = blimg_temp.pixels[:]

    delete_blimage(blimg_temp)


def process(pimg):
    emptythres = Pref.emptythres
    depth = Pref.dilation_max_depth
    radius = Pref.emptyrange

    emptythres8 = round(emptythres*255)
    img = pimg

    bufs = []
    buf = img.copy()
    for i in range(depth):
        bufs.append(buf.copy())
        buf = buf.filter(ImageFilter.MaxFilter())

    _gen = lambda x: ((x - emptythres8) / (255 - emptythres8)) * 255 if x >= emptythres8 else 0
    convert_table = [_gen(i) for i in range(256)] * len(img.getbands())

    bufs.reverse()
    out_buf = bufs[0].copy()
    for buf in bufs[1:]:
        blurred_img = out_buf.filter(ImageFilter.GaussianBlur(radius=radius))
        mask = blurred_img.point(convert_table)
        out_buf.paste(buf, mask=mask)

    return out_buf


main()
