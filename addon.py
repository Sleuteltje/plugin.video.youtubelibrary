#    Kodi Addon: Youtube Library
#    Description: Makes it possible to add youtube channels / playlists as tv shows in your library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Determines which route the addon is currently in and starts the appropiate function to handle that request
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

import urlparse
import httplib
#For ripping youtube information & url's
#For XML Reading & Writing
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
# For prettyfing the XML
from xml.dom import minidom
#For youtube api
import httplib2
import six
#from apiclient.discovery import build
import sys
#from googleapiclient.discovery import build
#For database connections to store the resume point and watched flag
#Import database libs
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

#import Functions
from resources.lib import bookmarks
from resources.lib import vars
from resources.lib import dev    
from resources.lib import ytube    
from resources.lib import m_xml    
from resources.lib import generators    
from resources.lib import routes    
from resources.lib import play    


xbmcplugin.setContent(vars.addon_handle, 'episodes')


#Check if this is the first run of the addon
if xbmcvfs.exists(os.path.join(vars.settingsPath,"settings.xml")) == False: #If the settings.xml file can't be found, this is the first addon run
    xbmcgui.Dialog().ok('First Run', 'Please read the online instructions how to use this addon. See online how you can help this project. Have fun!')
    m_xml.create_xml()
      
########## ROUTES ##############      
#Grab which mode the plugin is in    
mode = vars.args.get('mode', None)

##Index
if mode is None:
    dev.log('Mode is Index', True)
    routes.index()

## SERVICE
elif mode[0] == "service":
    routes.run_service()

#Folder
elif mode[0] == 'folder':
    foldername = vars.args['foldername'][0]
    #Which folder should be loaded?
    ## managePlaylists
    if foldername == 'managePlaylists':
        routes.manage_playlists()
    ## Search Channel
    elif foldername == 'searchchannel':
        routes.search_channel()
###### Manage Playlists subroutes 
## RemovePlaylist
elif mode[0] == "deletePlaylist":
    dev.log('Mode is deletePlaylist')
    #Remove this playlist
    id = vars.args['id'][0]
    playlists.delete_playlist(id) #Remove this playlist
    xbmcplugin.endOfDirectory(vars.addon_handle)
## RefreshPlaylist
elif mode[0] == "refreshPlaylist":
    dev.log('Mode is refreshPlaylist')
    #Refresh this playlist
    id = vars.args['id'][0]
    playlists.refresh_playlist(id) #Remove this playlist
    xbmcplugin.endOfDirectory(vars.addon_handle)
## editPlaylist
elif mode[0] == "editPlaylist":
    dev.log('Mode is editPlaylist')
    id = vars.args['id'][0]
    set = vars.args.get('set', None)
    routes.edit_playlist(id, set)
    

##### Search Channel subroutes
## pickedChannel
elif mode[0] == "pickedChannel":
    dev.log('Picked a channel')
    #Display the videos by their channel ID
    id = vars.args['id'][0]
    routes.show_playlists_by_channel(id)
## AddPlaylist
elif mode[0] == "addPlaylist":
    dev.log('Mode is addPlaylist')
    #Display the videos of this playlistID
    id = vars.args['id'][0]
    routes.add_playlist(id)


## Update all playlists
elif mode[0] == 'updateplaylists':
    dev.log('Mode is updateplaylists')
    routes.update_all_playlists()
## PLAY VIDEO
elif mode[0] == "play":
    dev.log('Mode is Play')
    id = vars.args['id'][0] #Grab the vid id which we should be playing
    show = vars.args['show'][0] #Grab the show
    season = vars.args['season'][0] #Grab the season
    episode = vars.args['episode'][0] #Grab the episode
    filename = vars.args['filename'][0] #Grab the filename
    play.playVid(id, filename, season, episode, show) #Update the nfo & strm files for this playlist
    

    

















# ############################################################################## # 
######################################### TESTS ##################################
# ############################################################################## # 
## STRM TEST
elif mode[0] == "strmtest":
    dev.log('Mode is strm test')
    id = vars.args['id'][0] #Grab the playlist id which we should be updating
    update_playlist(id) #Update the nfo & strm files for this playlist
        
    url = dev.build_url({'home': 'home'})
    dev.adddir('Done building strms', url, description = 'Done building all strm files. Press this button to return home')
    xbmcplugin.endOfDirectory(vars.addon_handle)

    
    
    
    
## XML TESTS
elif mode[0] == "xmlcreate":
    dev.log('Mode is xmlcreate')
    #Test the lxml module for writing xml and stuff
    m_xml.create_xml()
    url = dev.build_url({'mode': 'xmlcreate', 'foldername': 'xmlcreate'})
    dev.adddir('XML Create Test', url)
    xbmcplugin.endOfDirectory(vars.addon_handle)
    
    
## DELETE TESTS
elif mode[0] == "deletetest":
    #success = xbmcvfs.rmdir('C:/Users/Mich/AppData/Roaming/Kodi/userdata/addon_data/plugin.video.youtubelibrary/Streams/R_mi GAILLARD') #Remove the directory
    #success = xbmcvfs.rmtree('C:/Users/Mich/AppData/Roaming/Kodi/userdata/addon_data/plugin.video.youtubelibrary/Streams/R_mi GAILLARD/') #Remove the directory
    success = shutil.rmtree('C:/Users/Mich/AppData/Roaming/Kodi/userdata/addon_data/plugin.video.youtubelibrary/Streams/R_mi GAILLARD/', ignore_errors=True) #Remove the directory
    if success:
        xbmcgui.Dialog().ok('Removed from library', 'Deleted this show from your library')
    url = dev.build_url({'mode': 'deletetest', 'foldername': 'deletetest'})
    dev.adddir('Delete test', url)
    xbmcplugin.endOfDirectory(vars.addon_handle)