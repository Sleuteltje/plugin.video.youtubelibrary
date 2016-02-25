#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions that are called by routes
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
import xbmc, xbmcgui, xbmcplugin

from resources.lib import vars
from resources.lib import dev
from resources.lib import ytube
from resources.lib import m_xml
from resources.lib import service
from resources.lib import playlists

###SERVICE
#Runs the service    
def run_service():
    dev.log('SERVICE started updates again in %s minutes' % vars.service_interval)
    import time

    service.update_playlists()
    
    #vars.service_interval = xbmcplugin.getSetting(vars.addon_handle, 'vars.service_interval')
    #xbmcgui.Dialog().ok('Service started', 'Service started will run again in %s hours' % vars.service_interval)
    
    while True:
        # Sleep/wait for abort for number of hours that is set in the addon settings
        if xbmc.Monitor().waitForAbort(vars.service_interval*60):
        #if monitor.waitForAbort(5*60):
            # Abort was requested while waiting. We should exit
            break
        dev.log("SERVICE is running..! will update again in %s minutes" % vars.service_interval)
        service.update_playlists()
        service.update_playlists('musicvideo') #Update musicvideos as well
    dev.log("Kodi not running anymore, Service terminated")

#Force the running of the service    
def update_all_playlists(type=''):
    service.update_playlists(type=type) #Update all playlists

#Force the updating of 1 playlist
def update_playlist(type=''):
    id = vars.args['id'][0]
    xbmcgui.Dialog().notification(vars.__addonname__, 'Updating '+dev.typeName(type)+' Playlist '+id, vars.__icon__, 3000)
    service.update_playlist(id, type=type)
    xbmcgui.Dialog().notification(vars.__addonname__, 'Done updating '+dev.typeName(type)+' Playlist '+id, vars.__icon__, 3000)
    #Should we also update the video library?
    if vars.update_videolibrary == "true":
        update_dir = vars.tv_folder_path
        if type == 'musicvideo':
            update_dir = vars.musicvideo_folder_path
        dev.log('Updating video library is enabled. Updating librarys directory %s' % update_dir, True)
        xbmc.executebuiltin('xbmc.updatelibrary(Video,'+update_dir+')')

##Index
def index():
    index_dir()
    xbmcplugin.endOfDirectory(vars.addon_handle)

def index_dir():      
    import xbmcaddon
    #Manage TV Playlists
    url = dev.build_url({'mode': 'folder', 'foldername': 'managePlaylists'})
    context_url = dev.build_url({'mode': 'updateplaylists'})
    commands = []
    commands.append(( dev.lang(31003), 'XBMC.RunPlugin('+context_url+')', ))
    dev.adddir(dev.lang(31001), url, description=dev.lang(31002), context=commands)
    
    #Manage Music Video Playlists
    url = dev.build_url({'mode': 'folder', 'foldername': 'managePlaylists', 'type':'musicvideo'})
    context_url = dev.build_url({'mode': 'updateplaylists', 'type':'musicvideo'})
    commands = []
    commands.append(( dev.lang(31003), 'XBMC.RunPlugin('+context_url+')', ))
    dev.adddir(dev.lang(31011), url, description=dev.lang(31012), context=commands)
    
    #Search TV Channel
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchchannel'})
    dev.adddir(dev.lang(31004), url, description=dev.lang(31005))
    
    #Search Music Video Channel
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchchannel', 'type': 'musicvideo'})
    dev.adddir(dev.lang(31008), url, description=dev.lang(31009))
    
    #TEST
    #url = dev.build_url({'mode': 'striptest'})
    #dev.adddir('STRIP TEST', url, description=dev.lang(31009))




### Channel Search
#Searches for a youtube channel by name & displays the results
def search_channel(type=''):
    result = dev.user_input('', 'Search for '+dev.typeName(type)+' Channel')
    if len(result) > 0:
        ytube.search_channel(result, type)
    xbmcplugin.endOfDirectory(vars.addon_handle)

#Route: show_playlists_by_channel
def show_playlists_by_channel(Channelid, type=''):
    search_response = ytube.yt_get_channel_info(Channelid)
    
    #Grab the playlists from the response
    playlists = search_response['items'][0]['contentDetails']['relatedPlaylists']
    
    # Go through each playlist and display the playlist
    for key, value in playlists.iteritems():
      #Grab the number of videos to
      pl = ytube.yt_get_playlist_info(value)
      number_vids = str(pl['items'][0]['contentDetails']['itemCount'])
      #videos.append(search_result)
      url = dev.build_url({'mode': 'addPlaylist', 'id': value, 'type': type})
      dev.adddir(key.capitalize()+' ('+number_vids+')', url, search_response['items'][0]['snippet']['thumbnails']['high']['url'], fanart=search_response['items'][0]['snippet']['thumbnails']['high']['url'], description=dev.lang(31010)+' '+dev.typeName(type)+' \n--------\nPlaylist Description:\n'+search_response['items'][0]['snippet']['description'])
    
    # Grab other playlists this user has created to
    response = ytube.yt_get_playlists_by_channel(Channelid)
    
    if isinstance(response, list):
        # Go through each playlist and display the playlist
        for playlist in response:
          #videos.append(search_result)
          title = playlist['snippet']['title']+' ('+str(playlist['contentDetails']['itemCount'])+')'
          url = dev.build_url({'mode': 'addPlaylist', 'id': playlist['id'], 'type': type})
          dev.adddir(title, url, playlist['snippet']['thumbnails']['high']['url'], fanart=playlist['snippet']['thumbnails']['high']['url'], description=dev.lang(31010)+' '+dev.typeName(type)+' \n--------\nPlaylist Description:\n'+playlist['snippet']['description'])
    xbmcplugin.endOfDirectory(vars.addon_handle)#Adds a playlist & loads the view to edit it


#Adds a playlist & loads the view to edit it
def add_playlist(id, type=''):
    m_xml.xml_add_playlist(id, type)
    playlists.editPlaylist(id, type) #Load the view to edit this playlist
    #xbmc.executebuiltin("Container.Update")
    xbmcplugin.endOfDirectory(vars.addon_handle, updateListing=True)

##Route: Manage Playlists
def manage_playlists(type=''):
    dev.log('manage_playlists('+type+')')
    #pl = m_xml.xml_get_elem('playlists', 'playlists') #Grab <playlists>
    m_xml.xml_get(type)
    pl = m_xml.document.findall('playlists/playlist')
    if pl is not None: 
        for child in pl: #Loop through each playlist
            url = dev.build_url({'mode': 'editPlaylist', 'id': child.attrib['id'], 'type': type})
            #Build the contextmenu item to force the updating of one playlist
            context_url = dev.build_url({'mode': 'updateplaylist', 'id': child.attrib['id'], 'type': type})
            context_url2 = dev.build_url({'mode': 'deletePlaylist', 'id': child.attrib['id'], 'type': type})
            commands = []
            commands.append(( dev.lang(31006), 'XBMC.RunPlugin('+context_url+')', ))
            commands.append(( dev.lang(31007), 'XBMC.RunPlugin('+context_url2+')', ))
            dev.adddir(child.find('title').text, url, child.find('thumb').text, child.find('fanart').text, child.find('description').text, context=commands)
    xbmcplugin.endOfDirectory(vars.addon_handle)
    
#Loads the view of editing a playlist
def edit_playlist(id, set, type=''):
    if set != None:
        set = set[0]
        #We should set a value
        playlists.setEditPlaylist(id, set, type)
    #Display the videos of this playlistID
    playlists.editPlaylist(id, type=type)
    if set == None:
        xbmcplugin.endOfDirectory(vars.addon_handle)
    else:
        xbmc.executebuiltin("Container.Refresh")

def deletePlaylist(type=''):
    id = vars.args['id'][0]
    playlists.delete_playlist(id, type=type) #Remove this playlist
    xbmc.executebuiltin("Container.Refresh")
    #index_dir() #Load the index view
    #url = dev.build_url({'home': 'home'})
    #xbmc.executebuiltin("Action(PreviousMenu)")    
    #xbmc.executebuiltin("Container.Update("+url+","+url+")")
    #xbmcplugin.endOfDirectory(vars.addon_handle)

def refreshPlaylist(type=''):
    id = vars.args['id'][0]
    playlists.refresh_playlist(id, type=type) #Remove this playlist
    xbmc.executebuiltin("Container.Refresh")
    
    
###TESTS
