#!/usr/bin/env python
# -*-coding:utf-8 -*

# ****************************
# Modules
# =======
# import re, subprocess, fnmatch, shutil, time
import sys
# import os.path
# import glob
import math

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageEnhance
from PIL import ImageFile

sys.path.append('./python')

def watermark_build(text=u"\u00A9" + " Sonia Labetoulle", opacity=0.66) :

  # font_name = "/home/slipsl/.fonts/SegoePrint.ttf"
  font_name = "/usr/local/share/fonts/s/segoepr.ttf"
  font_size = 300

  font = ImageFont.truetype(font_name, font_size)

  wm = Image.new("RGBA", font.getsize(text))
  draw = ImageDraw.Draw(wm)

  ratio = font_size / 15
  for a in xrange(0, 360, 30) :
    coords = (ratio * math.cos(a*math.pi/180),
              ratio * math.sin(a*math.pi/180))
    draw.text(coords, text, font=font, fill="#000000")

  draw.text((0, 0), text, font=font, fill="#ffffff")

  # Apply opacity to watermark
  # ==========================
  if opacity < 1. :
    wm = ImageEnhance.Brightness(wm).enhance(opacity)

  wm.save("watermark.png", "PNG")

  return wm


def watermark_read(wm_img, opacity=0.66) :

  wm = Image.open(wm_img)

  if wm.mode != "RGBA" :
    wm = wm.convert("RGBA")

  # Apply opacity to watermark
  # ==========================
  if opacity < 1. :
    wm = ImageEnhance.Brightness(wm).enhance(opacity)

  return wm


# def watermark_build1(text=u"\u00A9" + " Sonia Labetoulle") :

#   font_name = "/home/slipsl/.fonts/SegoePrint.ttf"
#   font_size = 300

#   font = ImageFont.truetype(font_name, font_size)

#   wm = Image.new("RGBA", font.getsize(text))
#   draw = ImageDraw.Draw(wm)

#   draw.text((30, 30), text, font=font, fill="#000000")
#   draw.text((0, 0), text, font=font, fill="#ffffff")

#   return wm


# def watermark_build2(text=u"\u00A9" + " Sonia Labetoulle") :

#   font_name = "/home/slipsl/.fonts/SegoePrint.ttf"
#   font_size = 300

#   font = ImageFont.truetype(font_name, font_size)

#   wm1 = Image.new("RGBA", font.getsize(text))
#   draw = ImageDraw.Draw(wm1)
#   draw.text((0, 0), text, font=font, fill="#ff0000")
#   wm1_w, wm1_h = wm1.size

#   wm2 = Image.new("RGBA", font.getsize(text))
#   draw = ImageDraw.Draw(wm2)
#   draw.text((0, 0), text, font=font, fill="#0000ff")

#   ratio = 0.75
#   wm2_resize = (int(ratio*wm1_w), int(ratio*wm1_h))
#   wm2 = wm2.resize(wm2_resize, Image.ANTIALIAS)
#   wm2_w, wm2_h = wm2.size

#   paste_pos = ((wm1_w-wm2_w)/2, (wm1_h-wm2_h)/2)
#   wm1.paste(wm2, paste_pos, wm2)

#   return wm1


# def watermark_apply(
#   img_in, img_out, wm, text=u"\u00A9" + " Sonia Labetoulle",
#   opacity=0.66, wm_ratio=3) :
def watermark_apply(img_in, img_out, wm, resize, wm_ratio=3) :

  max_size = 2048

  img = Image.open(img_in)

  img_width, img_height = img.size
  # img_mode = img.mode
  img_format = img.format

  # wm = watermark_build3(text, opacity)
  wm_width, wm_height = wm.size

  # print max(img.size), img.size

  # Resize watermark according to image width
  # =========================================
  if wm_width > (img_width / wm_ratio) :
    # ratio = float(img_width) / (wm_ratio*float(wm_width))
    ratio = float(max(img.size)) / (wm_ratio*float(wm_width))
    wm_resize = (int(ratio*wm_width), int(ratio*wm_height))

    wm = wm.resize(wm_resize, Image.ANTIALIAS)

  # # Apply opacity to watermark
  # # ==========================
  # wm = ImageEnhance.Brightness(wm).enhance(opacity)

  # Paste watermark on image
  # ========================
  pad_width = int(float(img_width) / 100.)
  # pad_height = 0
  pad_height = pad_width
  wm_width, wm_height = wm.size
  wm_pos = (img_width  - (wm_width+pad_width),
            img_height - (wm_height+pad_height))

  img.paste(wm, wm_pos, wm)

  # Reduce image size to max 2048
  # =============================
  if resize :
    if max(img.size) > max_size :
      # print "=> Resize"
      ratio = float(max_size) / float(max(img.size))
      img_resize = (int(ratio*img_width), int(ratio*img_height))
      img = img.resize(img_resize, Image.ANTIALIAS)
      # print img_resize

  ImageFile.MAXBLOCK = max(img.size)**2

  img.save(img_out, "JPEG", quality=95, optimize=True, progressive=True)

  return


# if __name__ == '__main__':

#   dir_in  = "img"
#   dir_out = os.path.join(dir_in, "wm")

#   for img_in in glob.glob(os.path.join(dir_in, "*.jpg")) :
#     img_name = os.path.basename(img_in).split(".")[0]
#     img_ext  = os.path.basename(img_in).split(".")[1]
#     img_out  = os.path.join(dir_out, img_name+"_wm."+img_ext)
#     print img_in, img_out
#     watermark_apply(img_in, img_out, opacity=0.50)
