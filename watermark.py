#coding:utf-8
"""
watermark
~~~~~~~~~~~
使用python库PIL对图片添加水印，在安装PIL前需要先安装：
libjpeg
lzlib
freetype

PIL能取到图片的metadata信息，但是在保存时会丢掉这些信息，PIL没有好的解决办法。
于是安装了pyexiv2库。
mac 下安装方法：
https://gist.github.com/819680

注意pyexiv2的api接口有变化，采用新文档
http://tilloy.net/dev/pyexiv2/tutorial.html#reading-and-writing-exif-tags
"""

import sys
from cStringIO import StringIO
import Image, ImageDraw, ImageFont
from ExifTags import TAGS
import pyexiv2


def picopen(image):
    if not image:return

    if hasattr(image, 'getim'): # a PIL Image object
        im = image
    else:
        if not hasattr(image, 'read'): # image content string
            image = StringIO(image)
        try:
            im = Image.open(image.read()) # file-like object
        except IOError, e:
            print e
            return

    print "mode", im.mode

    if im.mode == 'RGBA':
        p = Image.new('RGBA', im.size, 'white')
        try:
            x, y = im.size
            p.paste(im, (0, 0, x, y), im)
            im = p
        except:
            pass
        del p

    if im.mode == 'P':
        need_rgb = True
    elif im.mode == 'L':
        need_rgb = True
    elif im.mode == 'CMYK':
        need_rgb = True
    else:
        need_rgb = False

    if need_rgb:
        im = im.convert('RGB', dither=Image.NONE)

    return im

def copy_image_metadata(source_file, dest_file):
    source_metadata = pyexiv2.ImageMetadata(source_file)
    source_metadata.read()

    dest_metadata = pyexiv2.ImageMetadata(dest_file)
    dest_metadata.read()

    for key in source_metadata.exif_keys:
        tag = source_metadata[key]
        try:
            dest_metadata[key] = pyexiv2.ExifTag(key, tag.value)
        except:
            pass

    dest_metadata.write()

def watermark_use_text(im, text, outfile, pos_x=0, pos_y=0, fonttype="", fontsize=60, fontcolor=(0,0,0)):
    if not hasattr(im, 'getim'): # a PIL Image object
        raise NotIsPilObject
    watermark = Image.new("RGBA", (im.size[0], im.size[1]))

    draw = ImageDraw.ImageDraw(watermark, "RGBA")

    font = ImageFont.truetype(fonttype, fontsize)

    if fontcolor:
        draw.text((pos_x, pos_y), text, font=font, fill=fontcolor)
    else:
        draw.text((pos_x, pos_y), text, font=font)

    im.paste(watermark, None, watermark)

    im.save(outfile)


def get_metadata(im):
    ret = {}
    if not hasattr(im, 'getim'): # a PIL Image object
        raise NotIsPilObject
    info = im._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

class NotIsPilObject(Exception):
    "not is a PIL Object"


def handler(source_file, target_file, text=None):
    fontcolor = (239, 238, 86)
    fontsize = 90
    fonttype="founder-simplified.ttf"
    im = picopen(source_file)
    if not text:
        meta = get_metadata(im)
        _date = meta.get("DateTime")
        if _date:
            text = _date.split(" ")[0].replace(":", "/")
    text = " ".join(list(text))
    pos_x = im.size[0] * 0.75
    pos_y = im.size[1] * 0.8
    watermark_use_text(im, text, target_file, pos_x=pos_x, pos_y=pos_y, fonttype=fonttype, fontsize=fontsize, fontcolor=fontcolor)
    copy_image_metadata(source_file, target_file)


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) >= 3:
        text = None
        source_file = argv[1]
        target_file = argv[2]
        if len(argv) == 4:
            text = argv[3]
        handler(source_file, target_file, text)
        ##handler(source_file, target_file, text)

