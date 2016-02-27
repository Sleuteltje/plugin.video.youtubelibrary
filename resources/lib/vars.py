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
import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import re
import urlparse
import sys

# Set API_KEY to the "API key" value from the "Access" tab of the
# Google APIs Console http://code.google.com/apis/console#access
# Please ensure that you have enabled the YouTube Data API and Freebase API
# for your project.
API_KEY = "AIzaSyBtO0Bl38DJKCuPh9e4mRW3-1UcGPPnQfs"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"    



#####Settings######
#Log prefix
LPREF = 'MICHS YoutubeLibrary:::::::: '
#Tell the log that our addon is running
xbmc.log(LPREF+'Running')
#The link that should be written in the strm file, so the videoaddon can play
KODI_ADDONLINK= 'plugin://plugin.video.youtube/play/?video_id='




##NONCONFIGURABLE
#Kodi Settings
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
databaseFile = os.path.join(dataPath, 'settings.db')

#Paths
addonPath = xbmcaddon.Addon().getAddonInfo("path")
IMG_DIR = os.path.join(addonPath,'resources/media')
gearArt = os.path.join(addonPath,'resources/media/gear.png')
addondataPath = os.path.join(xbmc.translatePath('special://profile/userdata/addon_data/plugin.video.youtubelibrary'), '')
settingsPath = os.path.join(xbmc.translatePath('special://profile/userdata/addon_data/plugin.video.youtubelibrary/Settings'), '')
streamsPath = os.path.join(xbmc.translatePath('special://profile/userdata/addon_data/plugin.video.youtubelibrary/Streams'), '')


#Addonname and icon
__addonname__ = xbmcaddon.Addon().getAddonInfo('name')
__icon__ = xbmcaddon.Addon().getAddonInfo('icon')
__fanart__ = xbmcaddon.Addon().getAddonInfo('path') + '/fanart.jpg'
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
musicvideo_folder_path = xbmc.translatePath(__settings__.getSetting("musicvideo_folder"))
musicvideo_folder = os.path.join(musicvideo_folder_path, '') #The directory where all the music videos .strm & nfo files will be added
update_videolibrary = __settings__.getSetting("update_videolibrary") #Should we update the video library after updating all playlists?
mode = int(__settings__.getSetting("mode"))


#Double userdata fix
double = { 
    '\\userdata\\userdata' : '\\userdata',
    '\userdata\userdata' : '\userdata',
    '//userdata//userdata' : '//userdata',
    '/userdata/userdata' : '/userdata'
}

for key, val in double.iteritems():
    settingsPath = settingsPath.replace(key, val) #Fix for double userdata :S?
    addondataPath = addondataPath.replace(key, val) #Fix for double userdata :S?
    streamsPath = streamsPath.replace(key, val) #Fix for double userdata :S?

    tv_folder = tv_folder.replace(key, val) #Fix for double userdata :S?
    tv_folder_path = tv_folder_path.replace(key, val) #Fix for double userdata :S?
    musicvideo_folder = musicvideo_folder.replace(key, val) #Fix for double userdata :S?
    musicvideo_folder_path = musicvideo_folder_path.replace(key, val) #Fix for double userdata :S?

#Extra Kodi Paths
#skinPath = xbmc.translatePath('special://skin/')
#cachesourcesFile = os.path.join(dataPath, 'sources.db')
#cachemetaFile = os.path.join(dataPath, 'metacache.db')
#cacheFile = os.path.join(dataPath, 'cache.db')