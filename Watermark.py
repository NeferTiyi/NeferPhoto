#!/usr/bin/python
# -*-coding:utf-8 -*

# **********************************************************************
# * ProcessPhotos.py                                                   *
# * ----------------                                                   *
# *                                                                    *
# **********************************************************************


# ======================================================================
# =                          Initializations                           =
# ======================================================================

# Modules
# =======
import sys, os.path, re, argparse, subprocess, fnmatch, math, time, shutil
import PythonMagick

sys.path.append('./python')

from NeferWM     import *

# Command line arguments
# ======================
parser = argparse.ArgumentParser()
parser.add_argument("FileIn", help="Input file")
parser.add_argument("FileOut", help="Output file")
args = parser.parse_args()

FileIn  = args.FileIn
FileOut = args.FileOut


wm = watermark_read("watermark0.png")
watermark_apply(FileIn, FileOut, wm, True, wm_ratio=4)

exit()
