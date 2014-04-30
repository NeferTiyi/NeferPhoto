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

NbError = 0


#Flickr authorization
# flickr = FlickrAuth( APIKey , APISecret )
flickr = flickrapi.FlickrAPI( APIKey , APISecret )

(token, frob) = flickr.get_token_part_one(perms='write')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))


# Photoset list
try : 
  PhotosetList = flickr.photosets_getList( user_id=UserID )
except :
  print "Flickr error"
  exit(2)

for Photoset in PhotosetList[0].findall('.//photoset') :
  if Photoset.find('title').text != "Visible" :
    SetID  = Photoset.get('id')
    Name   = Photoset.find('title').text
    CountP = int( Photoset.get('photos') )
    CountV = int( Photoset.get('videos') )

    Pages = int( math.ceil( float( CountP + CountV ) / 500. ) )

    # print SetID, Name, Count, Pages

    for Page in range( 1 , Pages+1 ) :
      try :
        PhotoList = flickr.photosets_getPhotos( photoset_id=SetID , page=Page )
      except Exception, rc :
        print "Error retrieving photo list for photoset %s : %s" % ( Name , rc )
        exit()
      print "%s : %i photos, %i vidéos, page %i/%i" % \
            ( Name, CountP, CountV, , Page , Pages )

      for Photo in PhotoList[0] :
        PhotoID     = Photo.get('id')
        Title       = Photo.get('title')
        try :
          PhotoInfo = flickr.photos_getInfo( photo_id=PhotoID )
        except Exception, rc :
          print "Error getting info for photo <%s>, in photoset <%s>" % \
                ( Title , Name , rc )
          NbError += 1
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
            print "Error setting perms for <%s>, in photoset <%s> : %s" % \
                  ( Title , Name , rc )
            NbError += 1
        # else :
        #   print Title


print "%i photos could not be updated" % ( NbError ) 

# flickr.photos.setPerms
# Set permissions for a photo.
# Authentification

# Cette méthode exige une authentification avec autorisation d'écriture.

# Remarque : Cette méthode exige une requête HTTP POST.
# Arguments

# api_key (Obligatoire)
#     Your API application key. See here for more details.
# photo_id (Obligatoire)
#     The id of the photo to set permissions for.
# is_public (Obligatoire)
#     1 to set the photo to public, 0 to set it to private.
# is_friend (Obligatoire)
#     1 to make the photo visible to friends when private, 0 to not.
# is_family (Obligatoire)
#     1 to make the photo visible to family when private, 0 to not.
# perm_comment (Obligatoire)
#     who can add comments to the photo and it's notes. one of:
#     0: nobody
#     1: friends & family
#     2: contacts
#     3: everybody
# perm_addmeta (Obligatoire)
#     who can add notes and tags to the photo. one of:
#     0: nobody / just the owner
#     1: friends & family
#     2: contacts
#     3: everybody 

# <photo id="2733" secret="123456" server="12" isfavorite="0" license="3" rotation="90" originalsecret="1bc09ce34a" originalformat="png">
#   <owner nsid="12037949754@N01" username="Bees" realname="Cal Henderson" location="Bedford, UK" />
#   <title>orford_castle_taster</title>
#   <description>hello!</description>
#   <visibility ispublic="1" isfriend="0" isfamily="0" />
#   <dates posted="1100897479" taken="2004-11-19 12:51:19" takengranularity="0" lastupdate="1093022469" />
#   <permissions permcomment="3" permaddmeta="2" />
#   <editability cancomment="1" canaddmeta="1" />
#   <comments>1</comments>
#   <notes>
#     <note id="313" author="12037949754@N01" authorname="Bees" x="10" y="10" w="50" h="50">foo</note>
#   </notes>
#   <tags>
#     <tag id="1234" author="12037949754@N01" raw="woo yay">wooyay</tag>
#     <tag id="1235" author="12037949754@N01" raw="hoopla">hoopla</tag>
#   </tags>
#   <urls>
#     <url type="photopage">http://www.flickr.com/photos/bees/2733/</url>
#   </urls>
# </photo>
