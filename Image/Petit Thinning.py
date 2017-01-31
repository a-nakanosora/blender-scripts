'''
Blender Script - Image Processing - Morphological Petit Thinning
    -- Morphology(Dilation)ベースの細線化処理を行う.


usage:
    - Pref.emptyrange, .emptythres, .dilation_max_depth を調節して当スクリプト実行
    - 原画像'A'(==bpy.data.images['A']) に対し処理を施した結果を'B'に出力する.
    - 画像はノンアルファなグレースケール画像であること. RGBAの内R成分のみが使用される.
    - 画像は白地に黒線が描かれているものとする.


requires:
    - Numpy
    - Pillow (PIL)

'''


import bpy ## BPY
import numpy as np
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

    pimg = Image.open(Pref.temppath_in)
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
    a0 = np.asarray(pimg)
    a0.flags.writeable = True

    W, H = len(a0[0]), len(a0)
    a = a0[:, :, 0].copy()

    a2 = exec_filters(W, H, a)
    pimg2 = Image.fromarray(np.uint8(a2))
    return pimg2


def exec_filters(W, H, ref_buffer):
    buf = ref_buffer
    bufs = []
    for i in range(Pref.dilation_max_depth):
        buf2 = buf.copy()
        bufs.append(buf2)
        buf = np__dilation3x3(buf2)

    maxv = 255
    emptythres8 = round(Pref.emptythres*255)
    bufs.reverse()
    buf3 = bufs[0].copy()
    for b in bufs[1:]:
        blurred_buf = get_blurred(buf3)

        blurred_buf_f = blurred_buf.flatten()
        buf3_f = buf3.flatten()
        b_f = b.flatten()
        idx = (b_f != maxv) & (blurred_buf_f >= emptythres8)
        tbuf = np.zeros(len(b_f))
        tbuf[idx] = (blurred_buf_f[idx]-emptythres8)/(maxv-emptythres8)
        buf3_f[idx] = tbuf[idx]*b_f[idx] + (1.0-tbuf[idx])*buf3_f[idx]
        buf3 = buf3_f
        buf3.resize(H,W)

    return buf3


def get_blurred(ref_buffer):
    pimg = Image.fromarray(np.uint8(ref_buffer)) ## as GrayScale Image
    pimg2 = pimg.filter(ImageFilter.GaussianBlur(radius=Pref.emptyrange))
    out_buffer = np.asarray(pimg2)
    return out_buffer


def np__map_max3(a_):
    v0 = 0
    a = np.insert(np.append(a_, v0), 0, v0)
    a2 = np.amax([a[1:],a[:-1]],axis=0)
    a3 = np.amax([a2[1:],a2[:-1]],axis=0)
    return a3


def np__dilation3x3(pxs):
    a = []
    for row in pxs:
        a.append(np__map_max3(row))
    b = np.array(a).transpose()
    c = []
    for row in b:
        c.append(np__map_max3(row))
    d = np.array(c).transpose()
    return d


main()
