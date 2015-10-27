#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Sets the global variables for use in the script
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os, shutil
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import urllib
import urllib2
import re
import urlparse
import httplib
#For ripping youtube information & url's
import pafy 
#For XML Reading & Writing
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
# For prettyfing the XML
from xml.dom import minidom
#For youtube api
import httplib2
import six
from apiclient.discovery import build
import sys
#from googleapiclient.discovery import build
#For database connections to store the resume point and watched flag
#Import database libs
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

#import Functions
#from resources.lib import bookmarks
    





#Kodi Settings
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

#####Settings######
#Log prefix
LPREF = 'MICHS YoutubeLibrary:::::::: '
#Tell the log that our addon is running
xbmc.log(LPREF+'Running')
#The link that should be written in the strm file, so the videoaddon can play
KODI_ADDONLINK= 'plugin://plugin.video.youtube/play/?video_id='
#Set the type of content view
xbmcplugin.setContent(addon_handle, 'episodes')

# Set API_KEY to the "API key" value from the "Access" tab of the
# Google APIs Console http://code.google.com/apis/console#access
# Please ensure that you have enabled the YouTube Data API and Freebase API
# for your project.
API_KEY = "AIzaSyBtO0Bl38DJKCuPh9e4mRW3-1UcGPPnQfs"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
#Set the youtube api key for pafy to
pafy.set_api_key(API_KEY)

##NONCONFIGURABLE
addonInfo = xbmcaddon.Addon().getAddonInfo
#skinPath = xbmc.translatePath('special://skin/')
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
databaseFile = os.path.join(dataPath, 'settings.db')
#cachesourcesFile = os.path.join(dataPath, 'sources.db')
#cachemetaFile = os.path.join(dataPath, 'metacache.db')
#cacheFile = os.path.join(dataPath, 'cache.db')
#Paths
addonPath = xbmcaddon.Addon().getAddonInfo("path")
IMG_DIR = os.path.join(addonPath,'resources/media')
gearArt = os.path.join(addonPath,'resources/media/gear.png')
settingsPath = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.youtubelibrary/Settings'), '')
#Addonname and icon
__addonname__ = xbmcaddon.Addon().getAddonInfo('name')
__icon__ = xbmcaddon.Addon().getAddonInfo('icon')

##Grab the addon settings
__settings__ = xbmcaddon.Addon("plugin.video.youtubelibrary")
service_interval = __settings__.getSetting("service_interval") #The interval at which the service will run & update
#Convert service interval back to an integer
if service_interval == '':
    service_interval = 12 #Default service_interval
else:
    service_interval = int(service_interval)
tv_folder_path = xbmc.translatePath(__settings__.getSetting("tv_folder"))
tv_folder = os.path.join(tv_folder_path, '') #The directory where all the tv-shows .strm & nfo files will be added
update_videolibrary = __settings__.getSetting("update_videolibrary") #Should we update the video library after updating all playlists?
