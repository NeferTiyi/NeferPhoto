#!/usr/bin/python
# -*-coding:utf-8 -*

import sys, os.path, re, glob, subprocess, fnmatch, shutil, time

# # Flickr ID
# # ---------
# import flickrapi
# from FlickrKey import *
# ======
from NeferFlickr import FlickrPhotoList

# Colors
# ======
from NeferColor import *


# Variables
# =========
# global DirNameLen
global MissByte
MissByte = -99999


def mtime(filename) :

  return os.stat(filename).st_mtime


def MakeDir( DirName ) :

  try :
    os.makedirs( DirName )
  except :
    print "Could not create %s" % ( DirName )
    exit()


def MoveFile( FileIn , FileOut ) :

  try :
    shutil.move( FileIn , FileOut )
  except Exception , rc :
    print "Error during move %s => %s :\n%s" % \
          ( FileIn , FileOut , rc )
    exit()


def RemoveFile( File ) :

  try :
    os.remove( File )
  except Exception , rc :
    print "Error during remove %s :\n%s" % \
          ( File , rc )
    exit()


def ChangeDir( DirName ) :

  try :
    os.chdir( DirName )
  except :
    print "Invalid directory %s" % ( DirName )
    exit()

  # print os.getcwd()


def CleanName ( Name ) :

  CleanDict = {  "/" : "-" , \
                 "(" : ""  , \
                 ")" : ""  , \
                 " " : "_" }

  for New , Old in CleanDict.iteritems() :
    Name = Name.replace( New , Old )

  return Name


def InitConfigDict( DIR_HOME , ID , CatFile, Init ) :

  DictOut = {}

  # Project path
  # ============
  try :
    DictOut["DIR_HOME"] = DIR_HOME
  except :
    print "Project %s not found in %s" % ( ID , CatFile )
    exit()

  # Load config.card
  # ================
  ReadConfigCard( DIR_HOME + "/config_py.card" , DictOut , Init )

  return DictOut


def ReadConfigCard ( File , ConfigDict , Init ) :

  if Init or \
     not os.path.exists( File ) :
    print "Initialize project"
    WriteConfigCard( ConfigDict["DIR_HOME"] , File )

  try :
    S_File = open( File , 'r' )
  # except Exception, rc :
  except IOError as rc :
    print "Error opening %s : %s" % ( File , rc.strerror )
    if rc.errno == 2 :
      Init = True
  except:
    print "Unexpected error:", sys.exc_info()[0]
    exit()

  # Read file
  # ---------
  for line in S_File.readlines() :
    Fields = line.split("=")
    if len(Fields) > 0 :
      if Fields[0][0] != "#" :
        Option = str.strip(Fields[0])
        Valeur = str.strip(Fields[1])
        ConfigDict[Option] = Valeur

  S_File.close()

  # Shell variables subtitution
  # ---------------------------
  for Opt in ConfigDict.iterkeys() :
    for Option, Valeur in ConfigDict.iteritems() :
      if Opt in Valeur :
        ConfigDict[Option] = Valeur.replace("${"+Opt+"}",ConfigDict[Opt])

  return ConfigDict


def WriteConfigCard( DIR_HOME , File ) :

  Year = raw_input("Year?\n")
  ProjectName   = raw_input("Project Name?\n")
  FlickrProject = raw_input("Flickr Project?\n")

  LineList = [ \
    "Year          = " + Year , \
    "ProjectName   = " + ProjectName , \
    "FlickrProject = " + FlickrProject.encode("utf-8") , \
    "LastUpload    = 0000-00-00_00:00" , \
    "DIR_DATA      = ${DIR_HOME}/Output" , \
    "DIR_OUT       = ${DIR_HOME}/Traitees" , \
    "DIR_STORE     = NONE" \
  ]

  try :
    S_File = open( File , 'w' )
  # except Exception, rc :
  except Exception as rc:
    print "Error opening %s : %s" % ( File , rc.strerror )
    exit()

  for Line in LineList :
    # print Line
    try :
      S_File.write( Line + "\n" )
    except :
      print "Error Writing %s" % File

  S_File.close()

  print "You can manually update config file %s\n" % File

  return


def PrintInfos( ProjectID , ConfigDict ) :

  Format = "%-13s : %s"
  print Format % ( "ProjectID"     , ProjectID )
  print Format % ( "ProjectName"   , ConfigDict["ProjectName"] )
  print Format % ( "FlickrProject" , ConfigDict["FlickrProject"] )
  print Format % ( "Year"          , ConfigDict["Year"] )
  print Format % ( "DIR_HOME"      , ConfigDict["DIR_HOME"] )
  print Format % ( "DIR_OUT"       , ConfigDict["DIR_OUT"] )
  print Format % ( "DIR_DATA"      , ConfigDict["DIR_DATA"] )
  print Format % ( "DIR_STORE"     , ConfigDict["DIR_STORE"] )
  print Format % ( "LastUpload"    , ConfigDict["LastUpload"] )


def LoadProjectCatalog( File ) :

  #===================================================================#
  # Load in memory the local project catalog                          #
  #===================================================================#

  # Open output file
  # ----------------
  try :
    S_File = open( File, 'r' )
  except Exception, rc :
    print "Error opening %s : %s" % ( File, rc )
    exit()

  # Load collections list from file
  # -------------------------------
  ProjectDict = {}

  for line in S_File.readlines() :
    Fields = line.split()
    ProjectID   = str.rstrip(Fields[0])
    ProjectPath = str.rstrip(Fields[1])
    ProjectDict[ProjectID] = ProjectPath

  # Close file
  # ----------
  S_File.close()

  return ProjectDict


def LoadFlickrCatalog( File ) :

  #===================================================================#
  # Read Flickr collections title and ID from file                    #
  #===================================================================#

  # Open output file
  # ----------------
  try :
    S_File = open( File, 'r' )
  except Exception, rc :
    print "Error opening %s : %s" % ( File, rc )
    exit()

  # Load collections list from file
  # -------------------------------
  CollectionDict = {}

  for line in S_File.readlines() :
    Fields = line.split(',')
    CollID    = str.rstrip(Fields[0])
    CollTitle = str.rstrip(Fields[1])
    CollectionDict[CollTitle] = CollID

  # Close file
  # ----------
  S_File.close()

  return CollectionDict


def BuildDirList( DIR_HOME , SUBMIT_DIR , Year , DirName ) :

  global DirNameLen
  MaxDirNameLen = 50

  ChangeDir( DIR_HOME )

  if DirName :
    if not os.path.exists( DirName ) :
      print "Invalid directory %s" % ( DirName )
      exit()
    else :
      DirList    = [ os.path.normpath( DirName ) ]
      DirListOri = [ os.path.normpath( os.path.join( DirName , "Ori" ) ) ]
  else :
    DirList    = []
    DirListOri = []

    for origin in glob.glob( Year + "*" ) :
      for root, dirs, files in os.walk( origin ) :
        if "Ori" in dirs :
          DirList.append( root )
          DirListOri.append( os.path.join( root , "Ori" ) )

  ChangeDir( SUBMIT_DIR )

  DirNameLen = max( map( len , DirList ) )
  if DirNameLen > MaxDirNameLen : 
    DirNameLen = MaxDirNameLen

  return DirList , DirListOri


def BuildPhotosetCatalog( File, DirList ) :

  # Open output file
  # ----------------
  try :
    S_File = open( File, 'w' )
  except Exception, rc :
    print "Error opening %s : %s" % ( File, rc )
    exit()

  # Write photosets list to file
  # ----------------------------
  PhotosetList = []

  for DirName in DirList :
    String = "%-40s \"\"\n" % ( DirName )
    S_File.write( String )

  # Close file
  # ----------
  S_File.close()

  return PhotosetList


def LoadPhotosetCatalog( File ) :

  # Open input file
  # ---------------
  try :
    S_File = open( File, 'r' )
  except Exception, rc :
    print "Error opening %s : %s" % ( File, rc )
    exit()

  # Load photosets list from file
  # -----------------------------
  PhotosetList = []

  for line in S_File.readlines() :
    Fields = line.split('"')
    Local  = str.strip(Fields[0])
    Flickr = str.strip(Fields[1])
    PhotosetList.append( { 'local' : Local, 'flickr' : Flickr} )

  # Close file
  # ----------
  S_File.close()

  return PhotosetList


def PrintCount( mode , DirName="" , \
                CountI=0 , CountO=0 , CountB=0 , CountF=0 , \
                DeltaL=0 , DeltaF=0 , \
                StatD="" , StatL="" , StatO="" , StatF="" ) :

  #===================================================================#
  # Print local and Flickr count                                      #
  #===================================================================#

  FormatList = [ DirNameLen , 4 , 4 , 4 , 6 , 6 , 5 ]
  # if countdirlen :
  #   FormatList[0] = int(countdirlen)

  FormatHead = "| %s%-" + str(FormatList[0]) + "s%s " + \
               "| %s%-" + str(FormatList[1]) + "s%s " + \
               ". %s%-" + str(FormatList[2]) + "s%s " + \
               ". %s%-" + str(FormatList[3]) + "s%s " + \
               "| %s%-" + str(FormatList[4]) + "s%s " + \
               "| %s%-" + str(FormatList[5]) + "s%s " + \
               "| %s%-" + str(FormatList[6]) + "s%s |"

  FormatSep  = "| " + FormatList[0]*"-" + " " + \
               "| " + FormatList[1]*"-" + " " + \
               ". " + FormatList[2]*"-" + " " + \
               ". " + FormatList[3]*"-" + " " + \
               "| " + FormatList[4]*"-" + " " + \
               "| " + FormatList[5]*"-" + " " + \
               "| " + FormatList[6]*"-" + " |"

  LineLen = sum(FormatList) + 3*len(FormatList) + 1
  FormatLine = "| %s%-" + str(FormatList[0]) + "s%s " + \
               "| %"    + str(FormatList[1]) + "i "   + \
               ". %s%"  + str(FormatList[2]) + "i%s " + \
               ". %"    + str(FormatList[3]) + "i "   + \
               "| %s%"  + str(FormatList[4]) + "i%s " + \
               "| %s%"  + str(FormatList[5]) + "i%s " + \
               "| %s%"  + str(FormatList[6]) + "i%s |"

  FormatMiss = "| %s%-" + str(FormatList[0]) + "s%s " + \
               "| %"    + str(FormatList[1]) + "i "   + \
               ". %s%"  + str(FormatList[2]) + "i%s " + \
               ". %"    + str(FormatList[3]) + "i "   + \
               "| %s%"  + str(FormatList[4]) + "i%s " + \
               "| "     + FormatList[5]*"?"  + " "    + \
               "| "     + FormatList[6]*"?"  + " |"


  if mode == "head" :
    print LineLen*"="

    print FormatHead % \
          ( Bold,"DirName",NoCol , \
            Bold," RAW",NoCol , Bold," JPG",NoCol , Bold," Dbl",NoCol , \
            Bold," Delta",NoCol , Bold,"Flickr",NoCol , Bold,"Delta",NoCol )
    print FormatSep

  elif mode == "foot" :
    print LineLen*"="

  elif mode == "miss" :
    print FormatMiss % ( BoldRed,DirName,NoCol )

  elif mode == "ligne" :
    if CountF == MissByte :
      print FormatMiss % \
            ( StatD,DirName,NoCol , \
              CountI, StatO,CountO,NoCol , CountB , \
              StatL,DeltaL,NoCol )
    else :
      print FormatLine % \
            ( StatD,DirName,NoCol , \
              CountI, StatO,CountO,NoCol , CountB , \
              StatL,DeltaL,NoCol , StatF,CountF,NoCol , StatF,DeltaF,NoCol )
  elif mode == "total" :
    print FormatSep
    print FormatLine % \
          ( StatD,DirName,NoCol , \
            CountI, StatO,CountO,NoCol , CountB , \
            StatL,DeltaL,NoCol , StatF,CountF,NoCol , StatF,DeltaF,NoCol )


def FindOri ( DirListOri ) :

  #===================================================================#
  # Search for misplaced processed pictures                           #
  #===================================================================#

  for DirName in DirListOri :
    PrintDir = True
    FileList = glob.glob( os.path.join( DirName , "*.tif" ) ) + \
               glob.glob( os.path.join( DirName , "*.jpg" ) )

    if len( FileList ) > 0 :
      PrintDir = PrintDirName( DirName , PrintDir )
      # if PrintDir :
      #   print "\n%-30s" % DirName
      #   print 30*"-"
      #   PrintDir = False
      FileList.sort()
      for FileName in FileList : 
        print os.path.basename( FileName )


def CheckFilesIdem( File1 , File2 ) :

  Command = [ "diff" , "-q" , File1 , File2 ]

  try :
    output = subprocess.call( Command , stdout=open(os.devnull, 'wb') )
  except Exception, rc :
    print "Couldn't diff files %s and %s" % ( File1 , File2 )
    output = -1

  Status = ( output == 0 )

  return Status


def LaunchGvim( File1 , File2 ) :

  Command = [ "gvim" , "-d" , File1 , File2 ]

  try :
    output = subprocess.call( Command , stdout=open(os.devnull, 'wb') )
  except Exception, rc :
    print "Couldn't launch gvim"
    output = -1

  Status = ( output == 0 )

  return Status


def PrintDirName( DirName , PrintDir ) :

  if PrintDir :
    print "\n%s" % DirName
    print 30*"-"
  PrintDir = False

  return PrintDir


def DxO2InOut( DxOFile, ProjectName , DIR_HOME ) :

  BaseFile = os.path.basename( os.path.splitext( DxOFile )[0] )
  ImgDir   = os.path.dirname( DxOFile )
  ImgNum   = BaseFile[4:8]
  ImgOrd   = BaseFile.split("DxO")[1]
  ImgExt   = os.path.splitext( DxOFile )[1]

  FileIn  = os.path.join( DIR_HOME , DxOFile )
  FileOut = os.path.join( \
              DIR_HOME , ImgDir, \
              ProjectName+"_"+ImgNum+ImgOrd+ImgExt )

  return FileIn , FileOut


def Raw2Jpg( RawFile , ProjectName ) :

  Pos = RawFile.find(".")
  Num = RawFile[Pos-4:Pos]

  JpgFile = ProjectName + "_" + Num + "*.jpg"

  return JpgFile


def Jpg2Raw( JpgFile , ProjectName ) :

  Pos = os.path.basename( JpgFile ).find( "_" )
  Num = os.path.basename( JpgFile )[Pos+1:Pos+5]

  RawFile1 = "IMG_" + Num + ".CR2"
  RawFile2 = "P000" + Num + ".JPG"

  return RawFile1 , RawFile2


def JpgTifFiles( File , Pattern1 , Pattern2 ) :

  ( Dir1 , File1 ) = os.path.split( File )
  File2 = File1.replace( Pattern1 , Pattern2 )

  return Dir1 , File1 , File2


def GetRawList( DirName ) :

  List = FindMatches( DirName , "*.CR2" ) + \
         FindMatches( DirName , "*.JPG" )

  return List


def GetJpgList( DirName , ProjectName ) :

  List = FindMatches( DirName , ProjectName+"_*.jpg" )

  return List


def GetCountB( DirName , File ) :

  Command = [ "grep" , "-c" , DirName , File ]
  try :
    # output  = float( subprocess.check_output( Command ) )
    output  = int( subprocess.check_output( Command ) )
  except Exception, rc :
    output = -1

  if output > 0 :
    # CountB  = int( math.ceil( output / 2 ) )
    CountB  = output
  else :
    CountB = 0

  return CountB


def GetCountF( DirFlickr , File ) :

  CountF = MissByte

  if not DirFlickr == "-99" :
    try :
      Command = [ "grep" , '"'+DirFlickr+'"' , File ]
      output = subprocess.check_output( Command )
    except Exception, rc :
      output = "-1"
    if output != "-1" :
      CountF = int(output.split('"')[2])

  return CountF


def GetStatus( DeltaL , DeltaF , CountB , CountF ) :

  if DeltaL != 0 and DeltaL != CountB :
    StatL = BoldRed
  else :
    StatL = BoldGreen

  if DeltaF != 0 and CountF != 0 :
    StatF = BoldRed
  else :
    StatF = BoldGreen

  if ( ( DeltaF == 0 and DeltaL == 0 ) or \
       ( DeltaF == 0 and DeltaL == CountB ) ) :
    StatD = BoldGreen
  else :
    StatD = Brown

  if ( ( DeltaL == 0 ) or \
       ( DeltaL == CountB ) ) :
    StatO = BoldGreen
  else :
    StatO = Brown

  return StatD , StatL , StatO , StatF


def FindMatches( DirName , Pattern ) :

  Matches = glob.glob( os.path.join( DirName , Pattern ) ) + \
            glob.glob( os.path.join( DirName , "Ori", Pattern ) )

  Matches.sort()

  return Matches


def UpdateLocal( FileOut , DirName , Pattern ) :

  try :
    S_File = open( FileOut , 'w' )
  except Exception, rc :
    print "Error opening %s : %s" % ( FileOut , rc )
    exit()

  for File in FindMatches( DirName , Pattern ) :
    try :
      S_File.write( os.path.basename( File ) + "\n" )
    except :
      print "Error Writing %s" % FileOut

  S_File.close()


def UpdateFlickr( FileOut , DirFlickr , PhotosetDict ) :

  if not DirFlickr == "-99" :
    try :
      SetID = PhotosetDict[DirFlickr.decode("utf-8")]
    except Exception, rc :
      print "Error retrieving flickr set ID for <%s> from photoset catalog : %s" % \
            ( DirFlickr , rc )
      return

    # print DirFlickr, SetID
    PhotoList = FlickrPhotoList( SetID )

    try :
      S_File = open( FileOut , 'w' )
    except Exception, rc :
      print "Error opening %s : %s" % ( FileOut , rc )
      exit()

    for Photo in PhotoList[0] :
      Title = Photo.get('title')
      String = Title + ".jpg\n"
      try :
        S_File.write( String.encode("utf-8") )
      except Exception, rc :
        print "Error writing %s : %s" % ( FileOut , rc )

    S_File.close()


def FullPhotolist( Mode , PathIO ) :

  Pattern = "PhotoList_*.txt"
  FileOut = Mode + "PhotoList_full.txt"

  Matches = glob.glob( os.path.join( PathIO  , Mode+Pattern ) )

  with open( os.path.join( PathIO , FileOut ) , 'wb' ) as O_File :
    for Match in Matches :
      if os.path.basename( Match ) != FileOut :
        with open( Match ) as I_File :
            shutil.copyfileobj( I_File , O_File )

  with open( os.path.join( PathIO , FileOut ) , 'r' ) as I_File :
    PhotoList = I_File.readlines()

  SortedPhotoList = sorted( set( PhotoList ) )

  with open( os.path.join( PathIO , FileOut ) , 'w' ) as O_File :
    for Photo in SortedPhotoList :
      try :
        O_File.write( Photo )
      except :
        print "Error Writing %s" % FileOut


def RsyncExec( DirName , Pattern , DirOut ) :

  BackDir = os.getcwd()

  ChangeDir( DirName )

  Command = [ "rsync" , "-va" , "./" , "--exclude" , "Ori*" , \
              "--include" , Pattern , DirOut ]

  try :
    output = subprocess.call( Command )
  except Exception, rc :
    print "Rsync failed", rc
    output = -1
  print output

  ChangeDir( BackDir )


# def LocalRsync( DirName , Pattern , DirOut ) :

#   BackDir = os.getcwd()

#   ChangeDir( DirName )

#   Command = [ "rsync" , "-va" , "./" , "--exclude" , "Ori*" , \
#               "--include" , Pattern , DirOut ]

#   try :
#     output = subprocess.call( Command )
#   except Exception, rc :
#     print "Rsync failed", rc
#     output = -1
#   print output

#   ChangeDir( BackDir )


# def RemoteRsync( DirName , Pattern , LastUpload , DirOut ) :

#   BackDir = os.getcwd()

#   # # A little cleanin'
#   # # -----------------
#   # ChangeDir( DirOut )

#   # for File in glob.glob( os.path.join( "upload" , Pattern ) ) :
#   #   print os.getcwd() , File , DirOut
#   #   try :
#   #     shutil.move( File , DirOut )
#   #   except Exception , rc :
#   #     print "Error during move %s => %s : %i" % \
#   #           ( File , DirOut , rc )
  
#   # ChangeDir( BackDir )


#   # # Sync
#   # # ----
#   ChangeDir( DirName )

#   Command = [ "rsync" , "-va" , "./" , "--exclude" , "Ori*" , \
#               "--include" , Pattern , DirOut ]

#   try :
#     output = subprocess.call( Command )
#   except Exception, rc :
#     print "Rsync failed", rc
#     output = -1
#   print output

#   ChangeDir( BackDir )


def UploadClean( DirIn , Pattern , DirOut ) :

  BackDir = os.getcwd()

  ChangeDir( DirOut )

  for File in glob.glob( os.path.join( DirIn , Pattern ) ) :

    IdemFiles = False
    IdemFiles = CheckFilesIdem( File , os.path.join( DirOut , File ) )
    if ( not IdemFiles ) :
      # MoveFile( File , DirOut )
      MoveFile( File , os.path.join( DirOut , File ) )
      # print "mv %s %s" % ( File , DirOut )
    else :
      RemoveFile( File )

  ChangeDir( BackDir )


def UploadList( DirIn , Pattern , DirOut , LastUpload ) :

  BackDir = os.getcwd()

  ChangeDir( DirIn )

  for File in glob.glob( Pattern ) :
    if os.path.getmtime( File ) > LastUpload :
      MoveFile( File , DirOut )
  
  ChangeDir( BackDir )

