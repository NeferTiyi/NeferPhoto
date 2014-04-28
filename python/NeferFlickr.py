#!/usr/bin/python
# -*-coding:utf-8 -*

import sys, os.path, re, glob, subprocess, fnmatch

# Flickr ID
# ---------
import flickrapi
from FlickrKey import *

# # Colors
# # ======
# from NeferColor import *


def FlickrAuth( Key , Secret ) :

  flickr = flickrapi.FlickrAPI( Key , Secret)

  (token, frob) = flickr.get_token_part_one(perms='read')
  if not token: raw_input("Press ENTER after you authorized this program")
  flickr.get_token_part_two((token, frob))
  
  return flickr


def DumpFlickrCatalog( File ) :

  #===================================================================#
  # Get from Flickr the collections title and ID and dump it to file  #
  #===================================================================#

  # Flickr authentication
  # ---------------------
  # print "Flickr Authentication"
  try :
    flickr = FlickrAuth( APIKey , APISecret )
  except:
    print "Flickr authentication failed"
    exit()

  # Get collection tree
  # -------------------
  # print "="*72
  # print "Retrieve collection tree"
  # print "="*72

  try: 
    CollectionTree = flickr.collections_getTree( user_id=UserID )
  except:
    print "Flickr error"
    exit()

  CollectionDict = {}

  for Collection in CollectionTree[0].findall('.//collection') :
    CollectionDict[Collection.get('title')] = Collection.get('id')

  # Open output file
  # ----------------
  try:
    S_File = open( File, 'w' )
  except Exception, rc:
    print "Error opening %s : %s" % ( File, rc )
    exit()

  # Write Collection dictionary to output file
  # ------------------------------------------
  for CollTitle , CollID in CollectionDict.iteritems() :
    S_File.write( CollID + "," + CollTitle.encode( "utf-8") + "\n")

  # Close file
  # ----------
  S_File.close()

  return


def GetFlickrCollPhotosets( CollName , CollID ) :

  # Flickr authentication
  # ---------------------
  # print "Flickr Authentication"
  flickr = FlickrAuth( APIKey , APISecret )

  # Get collection tree
  # -------------------
  # print "="*72
  # print "Retrieve collection tree for ", CollName
  # print "="*72

  try: 
    CollectionTree = flickr.collections_getTree( user_id=UserID , collection_id=CollID )
  except:
    print "Flickr error"
    exit(2)

  PhotosetDict = {}

  for Photoset in CollectionTree[0].findall('.//set') :
    PhotosetDict[Photoset.get('title')] = Photoset.get('id')

  return PhotosetDict


def Flickr2Local( Catalog , InName ) :

  # .. Get local name ..
  OutName = ""
  for Line in Catalog :
      if Line['flickr'] == InName.encode( 'utf-8') :
        OutName = Line['local']
        break

  return OutName


def Local2Flickr( Catalog , InName ) :

  # .. Get local name ..
  OutName = ""
  for Line in Catalog :
      if Line['local'] == InName :
        OutName = Line['flickr']
        break
  if OutName == "" :
    OutName = "-99"

  return OutName


def FlickrCount( PhotosetDict , File ) :

  #===================================================================#
  # Get Flickr count for one collection and dump it to file           #
  #===================================================================#


  # Flickr authentication
  # ---------------------
  # print "Flickr Authentication"
  flickr = FlickrAuth( APIKey , APISecret )


  # for Collection in CollectionTree[0].findall('.//collection') :
  #   CollectionDict[Collection.get('title')] = Collection.get('id')

  # Open output file
  # ----------------
  try:
    S_File = open( File, 'w' )
  except Exception, rc:
    print "Error opening %s : %s" % ( File, rc )
    exit()

  Total = 0

  for Title , ID in PhotosetDict.iteritems() :
    Photoset = flickr.photosets_getInfo(photoset_id=ID)
    Nb = Photoset[0].get('count_photos')
    Total = Total + int( Nb )

    String = "%-50s %4s\n" % ( '"'+Title+'"' , Nb )

    # Write to output file
    # --------------------
    try :
      S_File.write( String.encode( 'utf-8' ) )
    except :
      print "Error Writing %s" % File

  # Write total to output file
  # --------------------------
  String = "%-50s %4s\n" % ( '"Total"' , Total )
  try :
    S_File.write( String.encode( 'utf-8' ) )
  except :
    print "Error Writing %s" % File

  # Close file
  # ----------
  S_File.close()

  return


def FlickrPhotoList( ID ) :

  #===================================================================#
  # Get Flickr photos list for one photoset                           #
  #===================================================================#

  # Flickr authentication
  # ---------------------
  # print "Flickr Authentication"
  flickr = FlickrAuth( APIKey , APISecret )

  try:
    PhotoList = flickr.photosets_getPhotos(photoset_id=ID)
  except:
    print "Error retrieving photo list"
    exit()

  return PhotoList
  