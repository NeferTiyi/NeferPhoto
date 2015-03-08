#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this must come first
from __future__ import print_function, unicode_literals, division


# **********************************************************************
# * ProcessPhotos.py                                                   *
# * ----------------                                                   *
# *                                                                    *
# **********************************************************************


# ======================================================================
# =                          Initializations                           =
# ======================================================================

# Standard library imports
# ========================
import sys
import os.path
import re
import argparse
import subprocess
import fnmatch
import math
import time
import shutil
import PythonMagick
# import os.stat
# import flickrapi

sys.path.append('./python')

# Application library imports
from NeferPhotos import *
from NeferFlickr import *
from HealExif    import *
from NeferWM     import *

# Command line arguments
# ======================
parser = argparse.ArgumentParser()
parser.add_argument("ProjectID", help="The ID of the project")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Verbose mode")
parser.add_argument("-i", "--info", action="store_true",
                    help="Print config.card info")
parser.add_argument("--check", action="store_true",
                    help="Don't do anything, just print what would be done")
parser.add_argument("-n", "--rename", action="store_true",
                    help="Rename pictures")
parser.add_argument("-u", "--update", action="store_true",
                    help="Update data")
parser.add_argument("-d", "--directory",
                    help="Process given directory: SSAAMMJJ/Title")
parser.add_argument("-c", "--count", action="store_true",
                    help="Count local and Flickr pictures")
parser.add_argument("-m", "--missing", action="store_true",
                    help="Search for not processed RAW files or JPG files with no RAW")
parser.add_argument("-td", "--tifdbl", action="store_true",
                    help="Search for already processed TIF pictures")
parser.add_argument("-tm", "--tifmis", action="store_true",
                    help="Search for not processed TIF pictures")
parser.add_argument("-o", "--ori", action="store_true",
                    help="Search for misplaced processed pictures")
parser.add_argument("-p", "--process", action="store_true",
                    help="Process DxO pictures")
parser.add_argument("-lf", "--compar", action="store_true",
                    help="Compare Local and Flickr files")
parser.add_argument("-r", "--rsync", action="store_true",
                    help="Synchronize files")
parser.add_argument("--init", action="store_true",
                    help="Synchronize files")
parser.add_argument("-w", "--watermark", action="store_true",
                    help="Apply watermark")
parser.add_argument("--resize", action="store_true",
                    help="Resize watermarked pictures")
args = parser.parse_args()

ProjectID = args.ProjectID


# Variables
# =========

# Files
# =====
ProjectCatFile = "ProjectCatalog.txt"
FlickrColFile  = "FlickrCollections.txt"

# ======================================================================
# =                            Main program                            =
# ======================================================================

SUBMIT_DIR = os.getcwd()


# Load project catalog
# ====================
ProjectDict = LoadProjectCatalog(ProjectCatFile)


ConfigDict = InitConfigDict(ProjectDict[ProjectID], ProjectID,
                            ProjectCatFile, args.init)

ProjectName = ConfigDict["ProjectName"]
DIR_HOME    = ConfigDict["DIR_HOME"]
DIR_DATA    = ConfigDict["DIR_DATA"]


# Define usefull files and directories
# ====================================
LocalPath  = os.path.join(DIR_DATA, "Local")
FlickrPath = os.path.join(DIR_DATA, "Flickr")

if not os.path.isdir(DIR_DATA):
  print("mkdir %s" % DIR_DATA)
  MakeDir(DIR_DATA)
if not os.path.isdir(LocalPath):
  print("mkdir %s" % LocalPath)
  MakeDir(LocalPath)
if not os.path.isdir(FlickrPath):
  print("mkdir %s" % FlickrPath)
  MakeDir(FlickrPath)

ProjectSetsFile = os.path.join(DIR_DATA,
                               ProjectName + "_Catalog.txt")
CountDblonsFile = os.path.join(DIR_DATA,
                               ProjectName + "_DblonsFile.txt")
FlickrCountFile = os.path.join(DIR_DATA,
                               ProjectName + "_FlickrCount.txt")


# Crossed checking
# ================
if len(sys.argv) == 2:
  args.process = True

if args.process:
  args.ori = True

if args.count:
  if not os.path.exists(CountDblonsFile):
    print("No %s" % CountDblonsFile)
    args.update = True
  if not os.path.exists(FlickrCountFile):
    print("No %s" % FlickrCountFile)
    args.update = True

flickr_ok = True


# Build DirList
# =============
(DirList, DirListOri) = \
  BuildDirList(DIR_HOME, SUBMIT_DIR, \
                ConfigDict["Year"], args.directory)

# if args.verbose:
#   for DirName in DirList:
#     print DirName
#   for DirName in DirListOri:
#     print DirName


# Load photosets list
# ===================
if not os.path.exists(ProjectSetsFile):
  BuildPhotosetCatalog(ProjectSetsFile, DirList)

PhotosetList = LoadPhotosetCatalog(ProjectSetsFile)


# Print project information
# =========================
if args.info:
  PrintInfos(ProjectID, ConfigDict)
  if args.verbose:
    print("\n%3s directories\n===============" % (len(DirList)))
    # for DirName in DirListOri:
    #   print DirName
    # print 72*"-"
    for DirName in DirList:
      print(DirName)


# Construct files
# ===============
if args.update:

  print("Update!")

  # Doublons
  # --------
  try:
    S_File = open(CountDblonsFile, 'w')
  except Exception as rc:
    print("Error opening %s: %s" % (CountDblonsFile, rc))
    exit()

  ChangeDir(DIR_HOME)

  for DirName in DirList:
    if not os.path.isdir(DirName):
      continue

    RawList = GetRawList(DirName)

    for File in RawList:
      JpgFile = Raw2Jpg(File, ProjectName)

      Matches = FindMatches(DirName, JpgFile)
      Count =  len(Matches)

      if Count > 1:
        for Match in Matches[1:]:
          try:
            S_File.write(Match + "\n")
          except:
            print("Error Writing %s" % CountDblonsFile)

  S_File.close()

  ChangeDir(SUBMIT_DIR)

  # Photosets list
  # --------------
  FlickrProject = ConfigDict["FlickrProject"]

  if not os.path.isfile(FlickrColFile):
    print("File \"%s\" doesn't exist" % FlickrColFile)
    DumpFlickrCatalog(FlickrColFile)

  CollectionDict = LoadFlickrCatalog(FlickrColFile)
  try:
    CollectionID = CollectionDict[FlickrProject]
  except KeyError as rc:
    print("Flickr collection \"{}\" not found".format(FlickrProject))
    CollectionID = None
    flickr_ok = False

  if flickr_ok:
    PhotosetDict = GetFlickrCollPhotosets(FlickrProject, CollectionID)

  # Count
  # -----
  if flickr_ok:
    FlickrCount(PhotosetDict, FlickrCountFile)

  # Full photo lists
  # ----------------
  FullPhotolist("Local", LocalPath)
  if flickr_ok:
    FullPhotolist("Flickr", FlickrPath)


# Rename pictures
# ===============
if args.rename:

  ChangeDir(DIR_HOME)

  RawList = []

  for DirName in DirListOri:
    if not os.path.isdir(DirName):
      continue

    RawList = RawList               + \
              GetRawList(DirName) + \
              FindMatches(DirName, "*.MTS")

  SortedList = sorted(RawList, key=mtime)

  NewNum  = 0
  PrevNum = 0
  PrevPre = ""

  # if args.verbose:
  #   for File in SortedList:
  #     print File

  # nwrit = 0

  FileLog = "MoveFiles.sh"
  try:
    S_File = open(FileLog, 'w')
  except Exception as rc:
    print("Error opening %s: %s" % (FileLog, rc))
    exit()

  for File in SortedList:

    if args.verbose:
      print(File)

    NewNum = NewNum + 1

    TmpDir = os.path.join(os.path.dirname(File), "tmp")
    if not os.path.isdir(TmpDir):
      print("mkdir %s" % TmpDir)
      MakeDir(TmpDir)

    filebase = os.path.basename(File)
    if args.verbose:
      print(filebase)

    Pos = filebase.find(".")
    Ext = filebase[Pos+1:]

    if Ext == "JPG" and filebase[0] == "P":
      Num = filebase[4:8]
      Pre = "P000"
    elif Ext == "MTS": 
      Num = filebase[1:5]
      Pre = "VID_"
    else:
      Pos = filebase.find("_")
      Num = filebase[Pos+1:Pos+5]
      Pre = filebase[0:Pos+1]

    if (PrevNum > int(Num)) and \
       (PrevPre == Pre):
       print("/!\ %s" % (File))

    PrevNum = int(Num)
    PrevPre = Pre

    FileOut = Pre + "%04i" % (NewNum) + "." + Ext

    String = "mv -i {:50s} {:50s}\n".format(
               '\"' + File + '\"',
               '\"' + os.path.join(TmpDir, FileOut) + '\"'
            )
    if args.verbose:
      print(String)
    S_File.write(String)
    MoveFile(File, os.path.join(TmpDir, FileOut))

  S_File.close()

  print("%4i input files"   % (len(SortedList)))
  print("%4i renamed files" % (NewNum))


# Search for misplaced processed pictures
# =======================================
if args.ori:

  ChangeDir(DIR_HOME)

  FindOri(DirListOri)

  ChangeDir(SUBMIT_DIR)


# Check for missing files
# =======================
if args.missing:

  ChangeDir(DIR_HOME)

  for DirName in DirList:
    if not os.path.isdir(DirName):
      continue

    PrintDir = True

    RawList = GetRawList(DirName)

    JpgList = GetJpgList(DirName, ProjectName)

    # Check RAW files
    # ---------------
    for File in RawList:
      JpgFile = Raw2Jpg(File, ProjectName)

      Matches = FindMatches(DirName, JpgFile)
      Count =  len(Matches)

      if Count != 1:
        PrintDir = PrintDirName(DirName, PrintDir)

      if Count == 0:
        print("No %s" % (JpgFile))
      elif Count > 1:
        print("More than one %s" % (JpgFile))
        for Match in Matches:
          print("  => %s" % Match)

    # Check JPG files
    # ---------------
    for File in JpgList:
      (RawFile1, RawFile2, RawFile3) = Jpg2Raw(File, ProjectName)

      EOSjpg  = False
      Matches = FindMatches(DirName, RawFile1) + \
                FindMatches(DirName, RawFile2)
      Count = len(Matches)

      if Count == 0:
        EOSjpg  = True
        Matches = FindMatches(DirName, RawFile3)
      Count = len(Matches)

      if Count == 0 or EOSjpg:
        PrintDir = PrintDirName(DirName, PrintDir)

      if Count == 0:
        print("No %s|%s nor %s" %
              (os.path.join(DirName, "Ori", RawFile1),
               os.path.join(DirName, "Ori", RawFile3),
               os.path.join(DirName, "Ori", RawFile2)))

      if EOSjpg:
        print("Only JPG for %s" % File)

  ChangeDir(SUBMIT_DIR)


# Print local and flickr counts
# =============================
if args.count:

  ChangeDir(DIR_HOME)

  TotalO = 0
  TotalI = 0
  TotalB = 0
  TotalF = 0
  DeltaF = 0
  CountF = 0

  PrintCount("head")

  for DirName in DirList:
    if not os.path.isdir(DirName):
      continue

    # Local Count
    # -----------
    CountO = len(GetJpgList(DirName, ProjectName))
    CountI = len(GetRawList(DirName))
    CountB = GetCountB(DirName, CountDblonsFile)
    DeltaL = CountO - CountI

    TotalO = TotalO + CountO
    TotalI = TotalI + CountI
    TotalB = TotalB + CountB

    # Flickr Count
    # ------------
    if flickr_ok:
      DirFlickr = Local2Flickr(PhotosetList, DirName)

      CountF = GetCountF(DirFlickr, FlickrCountFile)
      if CountF != MissByte:
        DeltaF = CountF - CountO

    # Status
    # ------
    (StatD, StatL, StatO, StatF) = \
                      GetStatus(DeltaL, DeltaF, CountB, CountF)

    PrintCount("ligne", DirName,
                CountI, CountO, CountB, CountF,
                DeltaL, DeltaF,
                StatD, StatL, StatO, StatF)

  # Total
  # -----
  # TotalF = GetCountF("Total", FlickrCountFile)
  # if TotalF == MissByte:
  #   TotalF = 0
  DeltaL = TotalO - TotalI
  if flickr_ok:
    TotalF = GetCountF("Total", FlickrCountFile)
    DeltaF = TotalF - TotalO
  else:
    TotalF = 0
    DeltaF = 0
  (StatD, StatL, StatO, StatF) = \
                  GetStatus(DeltaL, DeltaF, TotalB, TotalF)

  PrintCount("total", "Total",
              TotalI, TotalO, TotalB, TotalF,
              DeltaL, DeltaF,
              StatD, StatL, StatO, StatF)

  PrintCount("foot")


# Search for already processed TIF pictures
# =========================================
if args.tifdbl:

  ChangeDir(DIR_HOME)

  for DirName in DirList:
    PrintDir = True
    if not os.path.isdir(DirName):
      continue

    JpgList = FindMatches(DirName, "*_tif.jpg")

    for File in JpgList:
      (JpgDir, JpgFile, TifFile) = \
        JpgTifFiles(File, "_tif.jpg", ".tif")

      Matches = FindMatches(DirName, TifFile)

      if len(Matches) > 0:
        PrintDir = PrintDirName(DirName, PrintDir)
        print("%s  &  %s" % (JpgFile, TifFile))

  ChangeDir(SUBMIT_DIR)


# Search for not processed TIF pictures
# =====================================
if args.tifmis:

  ChangeDir(DIR_HOME)
  # print os.getcwd()

  for DirName in DirList:
    PrintDir = True
    if not os.path.isdir(DirName):
      continue

    TifList = FindMatches(DirName, "*.tif")

    for File in TifList:
      (TifDir, TifFile, JpgFile) = \
        JpgTifFiles(File, ".tif", "_tif.jpg")

      Matches = FindMatches(DirName, JpgFile)

      if len(Matches) == 0:
        PrintDir = PrintDirName(DirName, PrintDir)
        print(TifFile)

  ChangeDir(SUBMIT_DIR)


# Process files
# =============
if args.process:

  ChangeDir(DIR_HOME)

  for DirName in DirList:
    if not os.path.isdir(DirName):
      continue

    PrintDir = True

    FileList = FindMatches(DirName, "*_DxO*.jpg") + \
               FindMatches(DirName, "*_DxO*.tif") 

    FileList.sort()
    if len(FileList) > 0:
      PrintDir = PrintDirName(DirName, PrintDir)

      for File in FileList:

        NewerIn  = False
        IdemIn   = False
        ExistOut = False

        (FileIn, FileOut) = DxO2InOut(File, ProjectName, DIR_HOME)

        add_author(FileIn)

        if os.path.isfile(FileOut):
          ExistOut = True

          TimeIn  = os.path.getmtime(FileIn)
          TimeOut = os.path.getmtime(FileOut)
          if (TimeIn > TimeOut):
            NewerIn = True
            IdemIn  = CheckFilesIdem(FileIn, FileOut)

        if (args.update) or \
           (NewerIn and not IdemIn) or \
           (not ExistOut):
          print("mv %s %s" % (FileIn, FileOut))
          if not args.check:
            os.rename(FileIn, FileOut)

    FileList = FindMatches(DirName, ProjectName+"*_tif.jpg") + \
               FindMatches(DirName, ProjectName+"*_ice.jpg")

    FileList.sort()
    if len(FileList) > 0:
      for File in FileList:
        if not check_exif_ok(File):
          if PrintDir:
            print("Heal exif data for TIF/ICE pictures")
            PrintDir = False

          if File.find("_tif") > 0:
            FileDxO = File.replace("_tif", "")
          else:
            FileDxO = File.replace("_ice", "")
          if args.check:
            print("Get exif data from %s for %s" % (FileDxO, File))
          else:
            heal_exif(File, FileDxO)

  ChangeDir(SUBMIT_DIR)


# Compare local and Flickr files
# ==============================
if args.compar:

  ChangeDir(DIR_HOME)

  for DirName in DirList:
    PrintDir = True
    if not os.path.isdir(DirName):
      continue

    DirLog = CleanName(DirName)

    Pattern   = "PhotoList_" + DirLog + ".txt"
    LocalLog  = os.path.join(LocalPath, "Local"+Pattern)
    FlickrLog = os.path.join(FlickrPath, "Flickr"+Pattern)
    DirFlickr = Local2Flickr(PhotosetList, DirName)

    if args.update:
      UpdateLocal(LocalLog, DirName, ProjectName+"_*.jpg")
      UpdateFlickr(FlickrLog, DirFlickr, PhotosetDict)

    if os.path.isfile (LocalLog) and os.path.isfile (FlickrLog):
      IdemFiles = False
      IdemFiles = CheckFilesIdem(LocalLog, FlickrLog)
      if (not IdemFiles):
        print("Files {} and {} are identical".format(LocalLog, FlickrLog))
      else:
        Status = LaunchGvim(LocalLog, FlickrLog)
    else:
      print(os.path.isfile(LocalLog), os.path.isfile(FlickrLog))


  LocalLog  = os.path.join(LocalPath , "LocalPhotoList_full.txt")
  FlickrLog = os.path.join(FlickrPath, "FlickrPhotoList_full.txt")
  if os.path.isfile (LocalLog) and os.path.isfile (FlickrLog):
    IdemFiles = False
    IdemFiles = CheckFilesIdem(LocalLog, FlickrLog)
    if IdemFiles:
      print("Files {} and {} are identical".format(LocalLog, FlickrLog))
    else:
      Status = LaunchGvim(LocalLog, FlickrLog)

  ChangeDir(SUBMIT_DIR)


# Local and remote rsync
# ======================
if args.rsync:

  ChangeDir(DIR_HOME)

  Pattern = ProjectName + "_*.jpg"


  # Local rsync: from individual dir to DIR_OUT
  # --------------------------------------------
  if ConfigDict["DIR_OUT"] != "NONE":

    print(72*"=")
    print("  Local sync to %s" % ConfigDict["DIR_OUT"])
    print(72*"=")

    if not os.path.isdir(ConfigDict["DIR_OUT"]):
      print("mkdir %s" % ConfigDict["DIR_OUT"])
      MakeDir(ConfigDict["DIR_OUT"])

    for DirName in DirList:
      PrintDir = True
      if not os.path.isdir(DirName):
        continue

      NbPic = len(glob.glob(os.path.join(DirName, Pattern)))
      if NbPic > 0:
        print("Up to %i pictures to synchronize" % NbPic)
      else:
        print("Nothing to do")
        continue

      PrintDir = PrintDirName(DirName, PrintDir)

      RsyncExec(DirName, Pattern, ConfigDict["DIR_OUT"])


  # Remote rsync: from individual dir to remote store dir
  # ------------------------------------------------------
  if ConfigDict["DIR_STORE"] != "NONE":

    print(72*"=")
    print("  Remote sync to %s" % ConfigDict["DIR_STORE"])
    print(72*"=")

    UploadDir = os.path.join(ConfigDict["DIR_STORE"], "upload")

    print(ConfigDict["LastUpload"])
    LastUpload = time.strptime(ConfigDict["LastUpload"], \
                                "%Y-%m-%d_%H:%M")
    print(time.mktime(LastUpload))

    if not os.path.isdir(ConfigDict["DIR_STORE"]):
      print("mkdir %s" % ConfigDict["DIR_STORE"])
      MakeDir(ConfigDict["DIR_STORE"])
    if not os.path.isdir(UploadDir):
      print("mkdir %s" % UploadDir)
      MakeDir(UploadDir)


    for DirName in DirList:
      PrintDir = True
      if not os.path.isdir(DirName):
        continue

      NbPic = len(glob.glob(os.path.join(DirName, Pattern)))
      if NbPic > 0:
        print("Up to %i pictures to synchronize" % NbPic)
      else:
        print("Nothing to do")
        continue

      PrintDir = PrintDirName(DirName, PrintDir)

      UploadClean ("upload", Pattern, ConfigDict["DIR_STORE"])

      RsyncExec(DirName, Pattern, ConfigDict["DIR_STORE"])


    # Remote rsync: from individual dir to remote store dir
    # ------------------------------------------------------
    
    print(72*"=")
    print("  Files to upload")
    print(72*"=")

    UploadList(ConfigDict["DIR_STORE"], Pattern, "upload", \
                time.mktime(LastUpload))

  ChangeDir(SUBMIT_DIR)


# Apply watermark
# ===============
if args.watermark:

  # wm = watermark_build()
  wm = watermark_read("watermark0.png")
  # exit()

  ChangeDir(DIR_HOME)

  for DirName in DirList:
    PrintDir = True
    if not os.path.isdir(DirName):
      continue

    WmDir = os.path.join(DirName, "wm")

    if not os.path.isdir(WmDir):
      print("mkdir %s" % WmDir)
      MakeDir(WmDir)

    JpgList = FindMatches(DirName, ProjectName+"_*.jpg")

    for File in JpgList:
      WmFile = os.path.join(WmDir, Jpg2Wm(File))
      if not os.path.isfile(WmFile):
        print("%s => %s" % (File, WmFile))
        watermark_apply(File, WmFile, wm, args.resize, wm_ratio=4)

  ChangeDir(SUBMIT_DIR)

exit()
