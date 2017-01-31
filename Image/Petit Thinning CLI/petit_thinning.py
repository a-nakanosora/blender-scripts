'''
Image Processing - Morphological Petit Thinning
    -- Morphology(Dilation)ベースの細線化処理を行う.


usage:
    - commandline
        $ python petit_thinning.py <emptyrange> <emptythres> <dilation_max_depth> <path_in> [<path_out>] [-p]
      e.g.
        $ python petit_thinning.py 6 0.95 5 "d:/temp/a.png"
        $ python petit_thinning.py 3 0.9 10 "d:/temp/a.png" "d:/temp/b.png" -p

    - 画像はノンアルファなグレースケール画像であること. RGBAの内R成分のみが使用される.
    - 画像は白地に黒線が描かれているものとする.


requires:
    - Numpy
    - Pillow (PIL)
'''



import numpy as np
from PIL import Image, ImageFilter

import time
import sys

class Pref:
    path_in = 'd:/sample/file_in.png'
    path_out = 'd:/sample/file_out.png'

    #emptyrange, emptythres = 3, 0.9
    #emptyrange, emptythres = 5, 0.95
    #emptyrange, emptythres = 5, 0.99
    emptyrange, emptythres = 6, 0.95
    #emptyrange, emptythres = 7, 0.99
    #emptyrange, emptythres = 7, 0.98
    #emptyrange, emptythres = 7, 0.9
    #emptyrange, emptythres = 10, 0.95
    #emptyrange, emptythres = 20, 0.97

    dilation_max_depth = 5
    #dilation_max_depth = 1

    print_info = False



def main():
    apply_commandline_args()

    if Pref.print_info:
        print('''Morphological Thinning
emptyrange : {}
emptythres : {}
dilation_max_depth : {}
path_in : {}
path_out : {}
'''.format( Pref.emptyrange
          , Pref.emptythres
          , Pref.dilation_max_depth
          , Pref.path_in
          , Pref.path_out
          ))

    t0 = time.time()

    pimg = Image.open(Pref.path_in)
    pimg2 = process(pimg)
    pimg2.save(Pref.path_out)

    t1 = time.time()
    if Pref.print_info:
        print('main time:', t1-t0)


def apply_commandline_args():
    args = list(sys.argv)
    if '-p' in args:
        Pref.print_info = True
    args = [v for v in args if v != '-p']

    if len(args) < 5:
        print('''
usage:
  $ python petit_thinning.py <emptyrange> <emptythres> <dilation_max_depth> <path_in> [<path_out>] [-p]
e.g.
  $ python petit_thinning.py 6 0.95 5 "d:/temp/a.png"
  $ python petit_thinning.py 3 0.9 10 "d:/temp/a.png" "d:/temp/b.png" -p

  <emptyrange> : int -- emptyrange >= 0
  <emptythres> : float -- 0.0 < emptythres < 1.0
  <dilation_max_depth> : int -- dilation_max_depth >= 1
  <path_in> -- path of input file (.png)
  (Optional) <path_out> -- path of output file (.png)
  (Optional) -p -- show debug info''')
        return exit()



    Pref.emptyrange = int(args[1])
    Pref.emptythres = float(args[2])
    Pref.dilation_max_depth = int(args[3])

    if len(args) == 5:
        Pref.path_in = args[4]
        Pref.path_out = Pref.path_in.replace('.png', '_out.png')
    elif len(args) == 6:
        Pref.path_in = args[4]
        Pref.path_out = args[5]

    assert Pref.path_in.endswith('.png'), 'input file should be a png file'
    assert Pref.path_out.endswith('.png'), 'output file should be a png file'


def process(pimg):
    a0 = np.asarray(pimg)
    a0.flags.writeable = True

    W, H = len(a0[0]), len(a0)
    a = a0[:, :, 0].copy() ## extract only R values

    a2 = exec_filters(W, H, a)

    pimg2 = Image.fromarray(np.uint8(a2)) ## as GrayScale Image
    return pimg2


def exec_filters(W, H, ref_buffer):
    '''
    @arg ref_buffer : Pixels2d (NumpyArray(2D)) -- input image (GrayScale)
    '''

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
        idx = (blurred_buf_f >= emptythres8)
        tbuf = np.zeros(len(b_f))
        tbuf[idx] = (blurred_buf_f[idx]-emptythres8)/(maxv-emptythres8)
        buf3_f[idx] = np.maximum(0, np.minimum(255, tbuf[idx]*b_f[idx] + (1.0-tbuf[idx])*buf3_f[idx] ))
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
    '''
    Morphology :: Dilation filter (3x3)
    @arg pxs : Pixels2d (NumpyArray(2D))
    '''
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
