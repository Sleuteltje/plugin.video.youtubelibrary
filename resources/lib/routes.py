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
    dev.log('SERVICE started updates again in % hours' % vars.service_interval)
    import time

    service.update_playlists()
    
    #vars.service_interval = xbmcplugin.getSetting(vars.addon_handle, 'vars.service_interval')
    #xbmcgui.Dialog().ok('Service started', 'Service started will run again in %s hours' % vars.service_interval)
    
    while True:
        # Sleep/wait for abort for number of hours that is set in the addon settings
        if xbmc.Monitor().waitForAbort(vars.service_interval*60*60):
        #if monitor.waitForAbort(5*60):
            # Abort was requested while waiting. We should exit
            break
        dev.log("SERVICE is running..! will update again in %s hours" % vars.service_interval)
        service.update_playlists()
    dev.log("Kodi not running anymore, Service terminated")


##Index
def index():
    index_dir()
    xbmcplugin.endOfDirectory(vars.addon_handle)

def index_dir():      
    url = dev.build_url({'mode': 'folder', 'foldername': 'managePlaylists'})
    dev.adddir('Manage Playlists', url, description='Manage the Channels Playlists you have added as a Tv Show in the Kodi Library')    
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchchannel'})
    dev.adddir('Add new Channel as TV Show', url, description='Search by channel name for a new Channel to add as Tv Show to your Kodi Library')
    url = dev.build_url({'mode': 'xmlcreate', 'foldername': 'xmlcreate'})
    dev.adddir('Update All Playlists (can take a while)', url, description='If playlists are never scanned before, expect a long wait.')
    url = dev.build_url({'mode': 'deletetest'})
    '''
    dev.adddir('XML Create Test', url)
    url = dev.build_url({'mode': 'play', 'id': 'HdaEePsLIc0'})
    dev.adddir('PLAY Test', url)
    url = dev.build_url({'mode': 'strmtest', 'id': 'UUSc16oMxxlcJSb9SXkjwMjA'})
    dev.adddir('STRM Test', url)
    url = dev.build_url({'mode': 'strmtest', 'id': 'PLV8Q_exbQpnYuouifDyV93_a_PlcwNM1l'})
    dev.adddir('STRM StukTV Opdrachten Test', url)
    url = dev.build_url({'mode': 'updateplaylists'})

    dev.adddir('Deletetest', url, description='Test the deleting of an entire directory')'''




### Channel Search
#Searches for a youtube channel by name & displays the results
def search_channel():
    result = dev.user_input('', 'Search for Channel')
    if len(result) > 0:
        ytube.search_channel(result)
    xbmcplugin.endOfDirectory(vars.addon_handle)

#Route: show_playlists_by_channel
def show_playlists_by_channel(Channelid):
    search_response = ytube.yt_get_channel_info(Channelid)
    
    #Grab the playlists from the response
    playlists = search_response['items'][0]['contentDetails']['relatedPlaylists']
    
    # Go through each playlist and display the playlist
    for key, value in playlists.iteritems():
      #Grab the number of videos to
      pl = ytube.yt_get_playlist_info(value)
      number_vids = str(pl['items'][0]['contentDetails']['itemCount'])
      #videos.append(search_result)
      url = dev.build_url({'mode': 'addPlaylist', 'id': value})
      dev.adddir(key.capitalize()+' ('+number_vids+')', url, search_response['items'][0]['snippet']['thumbnails']['high']['url'], fanart=search_response['items'][0]['snippet']['thumbnails']['high']['url'], description='Press Ok to add this playlist to your list of Youtube Kodi Tv Shows \n--------\nPlaylist Description:\n'+search_response['items'][0]['snippet']['description'])
    
    # Grab other playlists this user has created to
    response = ytube.yt_get_playlists_by_channel(Channelid)
    
    if isinstance(response, list):
        # Go through each playlist and display the playlist
        for playlist in response:
          #videos.append(search_result)
          title = playlist['snippet']['title']+' ('+str(playlist['contentDetails']['itemCount'])+')'
          url = dev.build_url({'mode': 'addPlaylist', 'id': playlist['id']})
          dev.adddir(title, url, playlist['snippet']['thumbnails']['high']['url'], fanart=playlist['snippet']['thumbnails']['high']['url'], description='Press Ok to add this playlist to your list of Youtube Kodi Tv Shows \n--------\nPlaylist Description:\n'+playlist['snippet']['description'])
    xbmcplugin.endOfDirectory(vars.addon_handle)#Adds a playlist & loads the view to edit it


#Ads a playlist & loads the view to edit it
def add_playlist(id):
    m_xml.xml_add_playlist(id)
    playlists.editPlaylist(id) #Load the view to edit this playlist
    xbmc.executebuiltin("Container.Update")
    #xbmcplugin.endOfDirectory(vars.addon_handle)

##Route: Manage Playlists
def manage_playlists():
    dev.log('manage_playlists()')
    #pl = m_xml.xml_get_elem('playlists', 'playlists') #Grab <playlists>
    m_xml.xml_get()
    pl = m_xml.document.findall('playlists/playlist')
    if pl is not None: 
        for child in pl: #Loop through each playlist
            url = dev.build_url({'mode': 'editPlaylist', 'id': child.attrib['id']})
            dev.adddir(child.find('title').text, url, child.find('thumb').text, child.find('fanart').text, child.find('description').text)
    xbmcplugin.endOfDirectory(vars.addon_handle)
    
#Loads the view of editing a playlist
def edit_playlist(id, set):
    if set != None:
        set = set[0]
        #We should set a value
        playlists.setEditPlaylist(id, set)
    #Display the videos of this playlistID
    playlists.editPlaylist(id)
    if set == None:
        xbmcplugin.endOfDirectory(vars.addon_handle)
    else:
        xbmc.executebuiltin("Container.Refresh")

def deletePlaylist():
    id = vars.args['id'][0]
    playlists.delete_playlist(id) #Remove this playlist
    xbmc.executebuiltin("Container.Refresh")
    #index_dir() #Load the index view
    #url = dev.build_url({'home': 'home'})
    #xbmc.executebuiltin("Action(PreviousMenu)")    
    #xbmc.executebuiltin("Container.Update("+url+","+url+")")
    #xbmcplugin.endOfDirectory(vars.addon_handle)

def refreshPlaylist():
    id = vars.args['id'][0]
    playlists.refresh_playlist(id) #Remove this playlist
    xbmc.executebuiltin("Container.Refresh")
    
    
###TESTS
#Force the running of the service    
def update_all_playlists():
    service.update_playlists() #Update all playlists
    url = dev.build_url({'home': 'home'})
    dev.adddir('All playlists are now up to date', url, description = 'All playlists have been updated. Press this button to return home')
    xbmcplugin.endOfDirectory(vars.addon_handle)    
