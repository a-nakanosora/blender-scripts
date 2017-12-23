'''
Blender Script - Clipboard Copy Image (for Windows)
'''

import bpy

def main():
    img = bpy.data.images['Viewer Node']
    temppath = '{}/blenderscript_clipboardtemp.bmp'.format(bpy.context.user_preferences.filepaths.temporary_directory)

    save_as_bmp(img, temppath)

    f = open(temppath, "rb")
    f.read(14)
    bmpdata = f.read()
    f.close()

    clipboard_copy_image(bmpdata)
    print('copied the image to clipboard')


def save_as_bmp(img, path):
    scene = bpy.context.scene
    prev = scene.render.image_settings.file_format
    scene.render.image_settings.file_format = 'BMP'
    img.save_render(path)
    scene.render.image_settings.file_format = prev


def clipboard_copy_image(bitmapbinary):
    import io

    import ctypes
    msvcrt = ctypes.cdll.msvcrt
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    CF_DIB = 8
    GMEM_MOVEABLE = 0x0002

    data = bitmapbinary
    global_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    global_data = kernel32.GlobalLock(global_mem)
    msvcrt.memcpy(ctypes.c_char_p(global_data), data, len(data))
    kernel32.GlobalUnlock(global_mem)
    user32.OpenClipboard(None)
    user32.EmptyClipboard()
    user32.SetClipboardData(CF_DIB, global_mem)
    user32.CloseClipboard()


main()
