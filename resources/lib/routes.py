# -*- coding: utf-8 -*-
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
from resources.lib import ytlibrary_api

###SERVICE
#Runs the service    
def run_service():
    dev.log('SERVICE started updates again in %s minutes' % vars.service_interval)
    import time

    service.update_playlists()
    service.update_playlists('musicvideo') #Update musicvideos as well
    service.update_playlists('movies') #Update movies as well
    
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
        service.update_playlists('movies') #Update movies as well
    dev.log("Kodi not running anymore, Service terminated")

#Force the running of the service    
def update_all_playlists(type=''):
    service.update_playlists(type=type) #Update all playlists

#Force the updating of 1 playlist
def update_playlist(type=''):
    id = vars.args['id'][0]
    playlists.update_playlist(id, type=type)

##Index
def index():
    index_dir()
    xbmcplugin.endOfDirectory(vars.addon_handle)

def index_dir():      
    import xbmcaddon
    #Manage TV Playlists
    #Separator
    url = dev.build_url({'mode': 'folder', 'foldername': 'index'})
    dev.adddir('[COLOR blue]-------------------'+dev.lang(31024)+'-------------------[/COLOR]', url, '')
    
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
    
    #Manage Movies Playlists
    url = dev.build_url({'mode': 'folder', 'foldername': 'managePlaylists', 'type':'movies'})
    context_url = dev.build_url({'mode': 'updateplaylists', 'type':'movies'})
    commands = []
    commands.append(( dev.lang(31003), 'XBMC.RunPlugin('+context_url+')', ))
    dev.adddir(dev.lang(31022), url, description=dev.lang(31023), context=commands)
    
    #Separator
    url = dev.build_url({'mode': 'folder', 'foldername': 'index'})
    dev.adddir('[COLOR blue]-------------------'+dev.lang(31025)+'-------------------[/COLOR]', url, '')
    
    
    
    #Search TV Channel
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchchannel'})
    dev.adddir(dev.lang(31004), url, description=dev.lang(31005))
    
    #Search TV Playlist
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchplaylist'})
    dev.adddir(dev.lang(31016), url, description=dev.lang(31017))
    
    #Search Music Video Channel
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchchannel', 'type': 'musicvideo'})
    dev.adddir(dev.lang(31008), url, description=dev.lang(31009))
    
    #Search Music Video Playlist
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchplaylist', 'type': 'musicvideo'})
    dev.adddir(dev.lang(31014), url, description=dev.lang(31015))

    #Search Movie Channel
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchchannel', 'type': 'movies'})
    dev.adddir(dev.lang(31018), url, description=dev.lang(31019))
    
    #Search Movie Playlist
    url = dev.build_url({'mode': 'folder', 'foldername': 'searchplaylist', 'type': 'movies'})
    dev.adddir(dev.lang(31020), url, description=dev.lang(31021))

    #Separator
    url = dev.build_url({'mode': 'folder', 'foldername': 'index'})
    dev.adddir('[COLOR blue]-------------------'+dev.lang(31026)+'-------------------[/COLOR]', url, '')
    
    
    #DONOR FUCNTION - Browse Playlists
    url = dev.build_url({'mode': 'ApiIndex', 'api_url': 'default'})
    dev.adddir(dev.lang(31027), url, description=dev.lang(31028))
    
    
    
    
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
    
### Playlist Search
#Searches for a youtube channel by name & displays the results
def search_playlist(type=''):
    result = dev.user_input('', 'Search for '+dev.typeName(type)+' Playlist')
    if len(result) > 0:
        searched_playlist(result, type)

def searched_playlist(result, type='', pagetoken=''):
    response = ytube.search_playlist(result, type, pagetoken)
    
    if isinstance(response['items'], list):
        # Go through each playlist and display the playlist
        for playlist in response['items']:
          #videos.append(search_result)
          title = playlist['snippet']['title']
          url = dev.build_url({'mode': 'addPlaylist', 'id': playlist['id']['playlistId'], 'type': type})
          dev.adddir(title, url, dev.playlist_highest_thumbnail(playlist), fanart=dev.playlist_highest_thumbnail(playlist), description=dev.lang(31010)+' '+dev.typeName(type)+' \n--------\nPlaylist Description:\n'+playlist['snippet']['description'])
    
    
    if 'prevPageToken' in response:
        if response['prevPageToken'] is not None:
            url = dev.build_url({'mode': 'searchedplaylist', 'search': result, 'type': type, 'pagetoken': response['prevPageToken']})
            dev.adddir('<< Prev Page', url, description='Go to the previous page of available playlists')
    
    if 'nextPageToken' in response:
        if response['nextPageToken'] is not None:
            url = dev.build_url({'mode': 'searchedplaylist', 'search': result, 'type': type, 'pagetoken': response['nextPageToken']})
            dev.adddir('Next Page >>', url, description='Go to the next page of available playlists')

    
    xbmcplugin.endOfDirectory(vars.addon_handle)#Adds a playlist & loads the view to edit it

#Route: show_playlists_by_channel
def show_playlists_by_channel(Channelid, type='', pagetoken='default'):
    if pagetoken == 'default' or pagetoken == '':
        search_response = ytube.yt_get_channel_info(Channelid)
        
        #Grab the playlists from the response
        playlists = search_response['items'][0]['contentDetails']['relatedPlaylists']
        
        # Go through each playlist and display the playlist
        for key, value in playlists.iteritems():
          if value == 'WL' or value == 'HL':
             continue #The watch later and watch history playlists are not giving their normal id's, so skip them
          #Grab the number of videos to
          pl = ytube.yt_get_playlist_info(value)
          number_vids = str(pl['items'][0]['contentDetails']['itemCount'])
          #videos.append(search_result)
          url = dev.build_url({'mode': 'addPlaylist', 'id': value, 'type': type})
          dev.adddir(key.capitalize()+' ('+number_vids+')', url,  dev.playlist_highest_thumbnail(search_response['items'][0]), fanart=dev.playlist_highest_thumbnail(search_response['items'][0]), description=dev.lang(31010)+' '+dev.typeName(type)+' \n--------\nPlaylist Description:\n'+search_response['items'][0]['snippet']['description'])
    
    # Grab other playlists this user has created to
    response = ytube.yt_get_playlists_by_channel(Channelid, pagetoken)
    
    
    if isinstance(response['items'], list):
        # Go through each playlist and display the playlist
        for playlist in response['items']:
          #videos.append(search_result)
          title = playlist['snippet']['title']+' ('+str(playlist['contentDetails']['itemCount'])+')'
          url = dev.build_url({'mode': 'addPlaylist', 'id': playlist['id'], 'type': type})
          dev.adddir(title, url, dev.playlist_highest_thumbnail(playlist), fanart= dev.playlist_highest_thumbnail(playlist), description=dev.lang(31010)+' '+dev.typeName(type)+' \n--------\nPlaylist Description:\n'+playlist['snippet']['description'])
    
    
    if 'prevPageToken' in response:
        if response['prevPageToken'] is not None:
            url = dev.build_url({'mode': 'pickedChannel', 'id': Channelid, 'type': type, 'pagetoken': response['prevPageToken']})
            dev.adddir('<< Prev Page', url, description='Go to the previous page of available playlists')
    
    if 'nextPageToken' in response:
        if response['nextPageToken'] is not None:
            url = dev.build_url({'mode': 'pickedChannel', 'id': Channelid, 'type': type, 'pagetoken': response['nextPageToken']})
            dev.adddir('Next Page >>', url, description='Go to the next page of available playlists')

    
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
            context_url3 = dev.build_url({'mode': 'refreshPlaylist', 'id': child.attrib['id'], 'type': type})
            context_url4 = dev.build_url({'mode': 'refreshArtwork', 'id': child.attrib['id'], 'type': type})
            commands = []
            commands.append(( dev.lang(31006), 'XBMC.RunPlugin('+context_url+')', ))
            commands.append(( dev.lang(31007), 'XBMC.RunPlugin('+context_url2+')', ))
            commands.append(( dev.lang(31029), 'XBMC.RunPlugin('+context_url3+')', ))
            commands.append(( dev.lang(31030), 'XBMC.RunPlugin('+context_url4+')', ))
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
    playlists.refresh_playlist(id, type=type) #Refresh this playlist
    xbmc.executebuiltin("Container.Refresh")
    
def refreshArtwork(type=''):
    id = vars.args['id'][0]
    playlists.refresh_artwork(id, type=type) #Refresh the artwork of this playlist
    xbmc.executebuiltin("Container.Refresh")
    




####API
def api_home():
    if vars.__settings__.getSetting('enable_donor') == 'false':
        xbmcgui.Dialog().ok(dev.lang(31991), dev.lang(31992))
    elif len(vars.__settings__.getSetting('api_token')) < 60:
         xbmcgui.Dialog().ok(dev.lang(31993), dev.lang(31994)) 
    else:
        import xbmcaddon
        #Browse All Playlists
        url = dev.build_url({'mode': 'ApiIndex2', 'api_url': 'default', 'type' : 'tv'})
        dev.adddir('TV', url, description='Easily add pre-configured TV playlists from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        #Browse All Genres
        url = dev.build_url({'mode': 'ApiIndex2', 'api_url': 'default', 'type' : 'musicvideo'})
        dev.adddir('Musicvideos', url, description='Easily add pre-configured Musicvideo playlists by Genre from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        #Browse By Tag
        url = dev.build_url({'mode': 'ApiIndex2', 'api_url': 'default', 'type' : 'movies'})
        dev.adddir('Movies', url, description='Easily add pre-configured Movies playlists by Tag from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        
    xbmcplugin.endOfDirectory(vars.addon_handle)
####API
def api_index(type=''):
    if vars.__settings__.getSetting('enable_donor') == 'false':
        xbmcgui.Dialog().ok(dev.lang(31991), dev.lang(31992))
    elif len(vars.__settings__.getSetting('api_token')) < 60:
         xbmcgui.Dialog().ok(dev.lang(31993), dev.lang(31994)) 
    else:
        import xbmcaddon
        #Browse All Playlists
        url = dev.build_url({'mode': 'ApiBrowse', 'api_url': 'default', 'type' : type})
        dev.adddir('Browse All Playlists', url, description='Easily add pre-configured playlists from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        #Browse All Genres
        url = dev.build_url({'mode': 'ApiGenres', 'api_url': 'default', 'type' : type})
        dev.adddir('Browse By Genre', url, description='Easily add pre-configured playlists by Genre from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        #Browse By Tag
        url = dev.build_url({'mode': 'ApiTags', 'api_url': 'default', 'type' : type})
        dev.adddir('Browse By Tag', url, description='Easily add pre-configured playlists by Tag from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        #Search by Title / Description
        url = dev.build_url({'mode': 'ApiSearch', 'type' : type})
        dev.adddir('Search by Title / Description', url, description='Search by title / description to add a pre-configured playlist from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        #Search by Channel
        url = dev.build_url({'mode': 'ApiSearchChannel', 'type' : type})
        dev.adddir('Search by Channel', url, description='Search by channel name to add a pre-configured playlist from Youtubelibrary.nl. Available for Donors only at the moment. But you can still visit Youtubelibrary.nl to manually add them!')
        
    xbmcplugin.endOfDirectory(vars.addon_handle)


        
        
def apiBrowse(api_url = '', type=''):
    ytlibrary_api.browse(api_url, type=type)
    xbmcplugin.endOfDirectory(vars.addon_handle)

def apiGenres(api_url = '', type=''):
    ytlibrary_api.browse_genres(api_url, type)
    xbmcplugin.endOfDirectory(vars.addon_handle)
def apiTags(api_url = '', type=''):
    ytlibrary_api.browse_tags(api_url, type)
    xbmcplugin.endOfDirectory(vars.addon_handle)
    
def apiAddPlaylist(id, type=''):
    playlist = ytlibrary_api.add_playlist(id, type)
    m_xml.xml_add_playlist(playlist['ytplaylistid'], type, playlist)
    playlists.editPlaylist(playlist['ytplaylistid'], type) #Load the view to edit this playlist
    #xbmc.executebuiltin("Container.Update")
    xbmcplugin.endOfDirectory(vars.addon_handle, updateListing=True)

def apiSearch(type=''):
    result = dev.user_input('', 'Search by Title / Description')
    if len(result) > 0:
        ytlibrary_api.browse(params={'search': result}, type=type)
    xbmcplugin.endOfDirectory(vars.addon_handle)

def apiSearchChannel(type=''):
    result = dev.user_input('', 'Search by Channel')
    if len(result) > 0:
        ytlibrary_api.browse(params={'channel': result}, type=type)
    xbmcplugin.endOfDirectory(vars.addon_handle)







    
###TESTS
