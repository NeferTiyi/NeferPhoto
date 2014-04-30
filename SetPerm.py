#!/usr/bin/python
# -*-coding:utf-8 -*

# **********************************************************************
# * SetPerm.py                                                         *
# * ----------                                                         *
# *                                                                    *
# **********************************************************************


# ======================================================================
# =                          Initializations                           =
# ======================================================================

# Modules
# =======
import sys, os.path, re, argparse, subprocess, fnmatch, math, time, shutil
       # , os.stat
# import flickrapi

sys.path.append('./python')

from NeferPhotos import *
from NeferFlickr import *

PerPage = 500 # Max 500

#Flickr authorization
flickr = flickrapi.FlickrAPI( APIKey , APISecret )

(token, frob) = flickr.get_token_part_one(perms='write')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))


# Photoset list
try: 
  PhotosetList = flickr.photosets_getList( user_id=UserID )
except:
  print "Flickr error"
  exit(2)

for Photoset in PhotosetList[0].findall('.//photoset') :
  if Photoset.find('title').text == "Visible" :
    SetID  = Photoset.get('id')
    Name   = Photoset.find('title').text
    CountP = int( Photoset.get('photos') )
    CountV = int( Photoset.get('videos') )

    Pages  = int( math.ceil( float( CountP + CountV ) / float( PerPage ) ) )

    # for Page in range( 1 , Pages+1 ) :
    for Page in range( Pages, 1, -1 ) :
      try :
        PhotoList = flickr.photosets_getPhotos( \
                      photoset_id=SetID , per_page=PerPage , page=Page )
      except Exception, rc :
        print "Error retrieving photo list for photoset %s : %s" % \
              ( Name , rc )
        continue
      print "%s : %i photos, %i videos, page %i/%i" % \
            ( Name, CountP, CountV, Page , Pages )

      Nb = 0

      for Photo in PhotoList[0] :
        PhotoID     = Photo.get('id')
        Title       = Photo.get('title')
        try :
          PhotoInfo   = flickr.photos_getInfo( photo_id=PhotoID )
        except Exception, rc :
          print "Error getting info for %s in photoset %s : %s / %s" % \
                ( Title , Name , rc, PhotoInfo )
          continue
        IsPublic    = PhotoInfo.find('.//visibility').get('ispublic')
        IsFriend    = PhotoInfo.find('.//visibility').get('isfriend')
        IsFamily    = PhotoInfo.find('.//visibility').get('isfamily')
        PermComment = PhotoInfo.find('.//permissions').get('permcomment')
        PermAddmeta = PhotoInfo.find('.//permissions').get('permaddmeta')

        if PermComment != "3" or PermAddmeta != "1" :
          print IsPublic, IsFriend, IsFamily, PermComment, PermAddmeta, Title
          try :
            Result = flickr.photos_setPerms( 
              photo_id=PhotoID , 
              is_public=IsPublic , is_friend=IsFriend , is_family=IsFamily , 
              perm_comment="3" , perm_addmeta="1"
            )
          except Exception, rc :
            print "Error updating perms for %s in photoset %s : %s / %s" % \
                  ( Title , Name , rc , Result )
        # else :
        #   print Title

        Nb += 1

        if Nb%10 == 0 :
          print Nb