#!/usr/bin/env python
# -*-coding:utf-8 -*

#import sys
import os.path
#import re
#import glob
import subprocess
#import fnmatch

# Variables
# =========
Author    = "Sonia Labetoulle"
Orient    = "Horizontal (normal)"
Copyright = "-copyright="+Author
Artist    = "-artist="+Author


def CheckExifOk(FileIn) :

  Command = ["exiftool" , "-make" , FileIn]

  try :
    output = subprocess.check_output(Command)
  except Exception as rc :
    print "Error"
    output = ""

  Status = (not output == "")

  return Status


def HealExif(FileIn, FileDxO) :

  Command = ["exiftool", "-overwrite_original_in_place",
             Copyright, Artist, "-addTagsFromFile",
             FileDxO, FileIn]

  if not os.path.isfile(FileDxO) :
    print "Missing %s" % FileDxO
  else :
    print "%s @ %s" % (FileIn , FileDxO)

    try :
      subprocess.call(Command)
    except Exception as rc :
      print "Error in exiftool for %s" % FileIn
      exit()
