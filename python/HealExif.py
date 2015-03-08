#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this must come first
from __future__ import print_function, unicode_literals, division

# Standard library imports
import sys
import os.path
import re
import glob
import subprocess
import fnmatch

# Application library imports


# Variables
# =========
author    = "Sonia Labetoulle"
orient    = "Horizontal (normal)"
copyright = "-copyright={}".format(author)
artist    = "-artist={}".format(author)


def check_exif_ok(filein) :

  command = ["exiftool", "-make", filein]

  try :
    output = subprocess.check_output(command)
  except Exception as rc :
    print("Error")
    output = ""

  status = (not output == "")

  return status


def heal_exif(filein, filedxo) :

  command = ["exiftool", "-overwrite_original_in_place",
             copyright, artist, "-addTagsFromFile",
             filedxo, filein]

  if not os.path.isfile(filedxo) :
    print("Missing {}".format(filedxo))
  else :
    print("{} @ {}".format(filein, filedxo))

    try :
      subprocess.call(command)
    except Exception as rc :
      print("Error in exiftool for {}".format(filein))
      exit()


def add_author(filein):

  command = ["exiftool", "-copyright", filein]

  try :
    output = subprocess.check_output(command)
  except Exception as rc :
    print("Error")
    output = None

  if not output:
    command = ["exiftool", "-overwrite_original_in_place",
               copyright, artist, filein]

    try :
      subprocess.call(command)
    except Exception as rc :
      print("Error in exiftool for {}".format(filein))
      exit()

