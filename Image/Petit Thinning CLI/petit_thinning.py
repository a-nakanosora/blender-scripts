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
    - Pillow (PIL)
'''



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

    #dilation_max_depth = 10
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

    pimg = Image.open(Pref.path_in).convert("L")
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
