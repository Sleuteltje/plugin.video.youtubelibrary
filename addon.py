# -*- coding: utf-8 -*-
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
import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

#import Functions
from resources.lib import bookmarks
from resources.lib import vars
from resources.lib import dev    
from resources.lib import ytube    
from resources.lib import m_xml
from resources.lib import generators    
from resources.lib import routes    
from resources.lib import play    
from resources.lib import playlists  
from resources.lib import m_imdb  


xbmcplugin.setContent(vars.addon_handle, 'episodes')


#Check if this is the first run of the addon
if xbmcvfs.exists(os.path.join(vars.settingsPath,"settings.xml")) == False: #If the settings.xml file can't be found, this is the first addon run
    xbmcgui.Dialog().ok(dev.lang(31101), dev.lang(31102))
    #Create the Streams/TV directory
    xbmcvfs.mkdir(vars.addondataPath) #Create the settings dir if it does not exist already
    #xbmcvfs.mkdir(vars.settingsPath) #Create the settings dir if it does not exist already
    #open(os.path.join(vars.settingsPath, "settings.xml"), 'a').close() #Write the settings.xml file
    xbmcvfs.mkdir(vars.streamsPath) #Create the streams dir if it does not exist already
    xbmcvfs.mkdir(vars.streamsPath+'TV') #Create the streams TV dir if it does not exist already
    
    m_xml.create_xml()
if xbmcvfs.exists(os.path.join(vars.settingsPath,"settings_musicvideo.xml")) == False:
    xbmcgui.Dialog().ok(dev.lang(31103), dev.lang(31104))
    
    xbmcvfs.mkdir(vars.streamsPath+'MusicVideos') #Create the streams musicvideos dir if it does not exist already
    
    m_xml.create_xml('settings_musicvideo.xml')
if xbmcvfs.exists(os.path.join(vars.settingsPath,"settings_movies.xml")) == False:
    xbmcgui.Dialog().ok(dev.lang(31103), dev.lang(31106))
    
    xbmcvfs.mkdir(vars.streamsPath+'Movies') #Create the streams musicvideos dir if it does not exist already
    
    m_xml.create_xml('settings_movies.xml')

########## ROUTES ##############      
#Grab which mode the plugin is in    
mode = vars.args.get('mode', None)
type = vars.args.get('type', '')
#Convert type[0] to just type
if type != '':
    type = type[0]


##Index
if mode is None:
    dev.log('Mode is Index', True)
    routes.index()
else: 
    dev.log('Mode is '+mode[0])
    

    ## SERVICE
    if mode[0] == "service":
        routes.run_service()

    #Folder
    elif mode[0] == 'folder':
        foldername = vars.args['foldername'][0]
        #Which folder should be loaded?
        ## managePlaylists
        if foldername == 'managePlaylists':
            routes.manage_playlists(type=type)
        ## Search Channel
        elif foldername == 'searchchannel':
            routes.search_channel(type=type)
        ## Search Playlist
        elif foldername == 'searchplaylist':
            routes.search_playlist(type=type)
        ## Searched Playlist (pagination)
        elif foldername == 'searchedplaylist':
            routes.search_playlist(result=vars.args['search'][0], type=type, pagetoken=vars.args['pagetoken'][0])
    ###### Manage Playlists subroutes 
    ## RemovePlaylist
    elif mode[0] == "deletePlaylist":
        dev.log('Mode is deletePlaylist '+type)
        #Remove this playlist
        routes.deletePlaylist(type)
    ## RefreshPlaylist
    elif mode[0] == "refreshPlaylist":
        dev.log('Mode is refreshPlaylist '+type)
        #Refresh this playlist
        routes.refreshPlaylist(type=type)    
    ## RefreshArtwork
    elif mode[0] == "refreshArtwork":
        dev.log('Mode is refreshArtwork '+type)
        #Refresh the artwork of this playlist
        routes.refreshArtwork(type=type)
    ## editPlaylist
    elif mode[0] == "editPlaylist":
        dev.log('Mode is editPlaylist '+type)
        id = vars.args['id'][0]
        set = vars.args.get('set', None)
        routes.edit_playlist(id, set, type=type)
        

    ##### Search Channel subroutes
    ## pickedChannel
    elif mode[0] == "pickedChannel":
        dev.log('Picked a channel')
        #Display the videos by their channel ID
        id = vars.args['id'][0]
        pagetoken = vars.args['pagetoken'][0]
        routes.show_playlists_by_channel(id, type=type, pagetoken=pagetoken)
    elif mode[0] == "pickedmusicvideoChannel":
        dev.log('Picked a MusicVideo channel')
        #Display the videos by their channel ID
        id = vars.args['id'][0]
        routes.show_playlists_by_channel(id, 'musicvideo')
    ## AddPlaylist
    elif mode[0] == "addPlaylist":
        dev.log('Mode is addPlaylist')
        #Display the videos of this playlistID
        id = vars.args['id'][0]
        routes.add_playlist(id, type=type)



    ## Update all playlists
    elif mode[0] == 'updateplaylists':
        dev.log('Mode is updateplaylists')
        routes.update_all_playlists(type=type)
    elif mode[0] == 'updateplaylist':
        dev.log('Mode is updateplaylist')
        routes.update_playlist(type=type)
    ## PLAY VIDEO
    elif mode[0] == "play":
        dev.log('Mode is Play')
        id = vars.args['id'][0] #Grab the vid id which we should be playing
        show = vars.args['show'][0] #Grab the show
        season = vars.args['season'][0] #Grab the season
        episode = vars.args['episode'][0] #Grab the episode
        filename = vars.args['filename'][0] #Grab the filename
        play.playVid(id, filename, season, episode, show) #Play the video
    ## PLAY MUSICVIDEO
    elif mode[0] == "playmusicvideo":
        dev.log('Mode is PlayMusicVideo')
        id = vars.args['id'][0] #Grab the vid id which we should be playing
        artist = vars.args['artist'][0].decode('utf-8') #Grab the artist
        song = vars.args['song'][0].decode('utf-8') #Grab the song
        filename = vars.args['filename'][0] #Grab the filename
        play.playMusicVid(id, filename, artist, song) #Play the video
    ## PLAY MOVIE
    elif mode[0] == "playmovie":
        dev.log('Mode is PlayMovie')
        id = vars.args['id'][0] #Grab the vid id which we should be playing
        filename = vars.args['filename'][0] #Grab the filename
        folder = vars.args['folder'][0] #Grab the filename
        play.playVid(id, filename, folder=folder, type='movies') #Play the video
        

        

        
        
        
        

    ##########################  API
    ##Index
    elif mode[0] == 'ApiIndex':
        routes.api_home()
    ##Index
    elif mode[0] == 'ApiIndex2':
        type = vars.args['type'][0]
        routes.api_index(type)
    elif mode[0] == "ApiAddPlaylist":
        #Display the videos of this playlistID
        id = vars.args['id'][0]
        type = vars.args['type'][0]
        routes.apiAddPlaylist(id, type)
    elif mode[0] == 'ApiBrowse':
        api_url = vars.args['api_url'][0]
        type = vars.args['type'][0]
        routes.apiBrowse(api_url, type)
    elif mode[0] == 'ApiGenres':
        api_url = vars.args['api_url'][0]
        type = vars.args['type'][0]
        routes.apiGenres(api_url, type)
    elif mode[0] == 'ApiTags':
        api_url = vars.args['api_url'][0]
        type = vars.args['type'][0]
        routes.apiTags(api_url, type)
    elif mode[0] == 'ApiSearch':
        type = vars.args['type'][0]
        routes.apiSearch(type)
    elif mode[0] == 'ApiSearchChannel':
        type = vars.args['type'][0]
        routes.apiSearchChannel(type)







    elif mode[0] == 'testIMDB':
        m_imdb.test()














    # ############################################################################## # 
    ######################################### TESTS ##################################
    # ############################################################################## # 
    ## REMUX TEST
    elif mode[0] == "remuxtest":
        dev.log('Mode is remuxtest');
        
        id = "Ivp6hfbQnts"
        
        from resources.lib import pafy
        pafy.set_api_key(vars.API_KEY)
        #Resolve the youtube video url for ourselves
        v = pafy.new(id)    
        
        url = dev.build_url({'mode': 'play', 'id': id})
        dev.adddir(str(v.getbest()), url, description=v.getbest().url)
        
        url = dev.build_url({'mode': 'playtest', 'foldername': 'remux'})
        dev.adddir(str(v.getbestvideo()), url, description=v.getbestvideo().url)
        
        dev.log('Remuxtest, best Video&Audio: '+str(v.getbest()));
        dev.log('Remuxtest, best Video: '+str(v.getbestvideo()));
        dev.log('Remuxtest, best Audio: '+str(v.getbestaudio()));
        
        xbmcplugin.endOfDirectory(vars.addon_handle)

        
    ##Playvidtest
    elif mode[0] == "striptest":
        dev.log('mode is striptest')
        title = 'Britney Spears - Gimme More (from Britney Spears Live: The Femme Fatale Tour)'
        
        url = dev.build_url({'home': 'home'})
        
        title = generators.strip_quality(title)
        dev.adddir(title, url, description = 'strip_quality')
        dev.log('After strip_quality: '+title)
        if generators.strip_lyrics(title) != title:
            dev.adddir(title, url, description = 'Title does not match strip_lyrics!')
        title = generators.strip_lyrics(title)
        dev.adddir(title, url, description = 'strip_lyrics')
        dev.log('After strip_lyrics: '+title)
        title = generators.strip_audio(title)
        dev.adddir(title, url, description = 'strip_audio')
        dev.log('After strip_audio: '+title)
        title = generators.strip_live(title)
        dev.adddir(title, url, description = 'strip_live')
        dev.log('After strip_live: '+title)
        
        xbmcplugin.endOfDirectory(vars.addon_handle)
        
    elif mode[0] == "playtest":
        dev.log('mode is playtest');
        
        id = "Ivp6hfbQnts"
        
        from resources.lib import pafy
        pafy.set_api_key(vars.API_KEY)
        #Resolve the youtube video url for ourselves
        v = pafy.new(id)    
        
        meta = {};
        meta['title'] = 'Test'
        poster = 'Default.png'
        
        xbmc.Player().play(v.getbestvideo().url) #Play this video
        '''
        liz = xbmcgui.ListItem(meta['title'], iconImage=poster, thumbnailImage=poster)
        liz.setInfo( type="Video", infoLabels=meta )
        liz.setPath(v.getbest().url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)'''

        
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