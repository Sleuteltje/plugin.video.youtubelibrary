#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions for playlist manipulation
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
import xbmcgui
import os
import shutil
import xbmc

from resources.lib import vars
from resources.lib import dev
from resources.lib import m_xml
from resources.lib import ytube


#Displays the editplaylist list item
def disp_setting(setting, title, description, level=0):
    #Is the mode in the addon settings high enough to display this setting?
    if level > vars.mode:
        return False #no
    
    #build url
    val = None
    if elem.find(setting) != None:
        val = elem.find(setting).text
        if setting == 'published':
            d = ytube.convert_published(val)
            val = d['day']+'-'+d['month']+'-'+d['year']
        elif setting == 'search_imdb': #Search_IMDB (movies setting)
            options = ['Yes, fallback on addon settings', 'Yes, dont add if imdb fails', 'No, just use addon settings']
            val = options[int(val)]
        elif setting == 'use_ytimage': 
            options = ['Only if no image found on IMDB', 'Always', 'Dont add if no image is found on IMDB', 'Never']
            val = options[int(val)]
    if val == None or val == 'None':
        val = ''
    url = dev.build_url({'mode': 'editPlaylist', 'id': plid, 'set': setting, 'type': pltype})
    if 'hardcoded' in title.lower() and 'genre hardcoded' not in title.lower() or 'fallback' in title.lower() and 'song fallback' not in title.lower():
        dev.adddir('[COLOR blue] --'+title+':[/COLOR] '+val, url, gear, fanart, description)
    else:
        dev.adddir('[COLOR blue]'+title+':[/COLOR] '+val, url, gear, fanart, description)
#Displays the editplaylist list bool item
def disp_bool_setting(setting, title, description, level=0):
    #Is the mode in the addon settings high enough to display this setting?
    if level > vars.mode:
        return False #no
    
    #build url
    val = None
    if elem.find(setting) != None:
        val = elem.find(setting).text
    if val == 'true' or val == '1':
        val = '[COLOR green]ON[/COLOR]'
    else:
        val = '[COLOR red]OFF[/COLOR]'
    url = dev.build_url({'mode': 'editPlaylist', 'id': plid, 'set': setting, 'type': pltype})
    dev.adddir('[COLOR blue]'+title+':[/COLOR] '+val, url, gear, fanart, description)


    
    

#Displays and saves the user input if something from editplaylist should be set
def setEditPlaylist(id, set, type=''):
    if set == 'enable':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("Enable", "Would you like to enable this playlist?")
        if i == 0:
            m_xml.xml_update_playlist_attr(id, 'enabled', 'no', type=type)
            return
            #dialog.ok("Set to disabled", "Playlist is disabled.")
        else:
            m_xml.xml_update_playlist_attr(id, 'enabled', 'yes', type=type)
            return
            #dialog.ok("Set to enabled", "Playlist will now be picked up by the scanner")
    elif set == 'writenfo':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("WriteNFO", "Write NFO files for this playlist?")
        if i == 0:
            i = 'no'
        else:
            i = 'Yes'
    elif set == 'skip_audio':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("Skip Audio Only Videos", "Skip Audio Only Videos?")
        if i == 0:
            i = 'false'
        else:
            i = 'true'
    elif set == 'skip_lyrics':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("Skip Lyrics", "Skip Lyric Videos?")
        if i == 0:
            i = 'false'
        else:
            i = 'true'
    elif set == 'skip_live':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("Skip Live", "Skip Live Videos?")
        if i == 0:
            i = 'false'
        else:
            i = 'true'
    elif set == 'skip_albums':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("Skip Albums", "Skip Album Videos?")
        if i == 0:
            i = 'false'
        else:
            i = 'true'
    elif set == 'published':
        elem = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type) #Find this playlist so we can grab the value of the settings
        setting = str(elem.find(set).text) #Convert the setting to a string so we can input it safely
        if setting == None or setting == 'None':
            setting = '01/01/1901'
        d = ytube.convert_published(setting)
        prev_setting = d['day']+'/'+d['month']+'/'+d['year']
        i = xbmcgui.Dialog().input('Change Published Date', prev_setting, 2)
        if i == '':
            i = prev_setting
        else:
            d = ytube.convert_published(i)
            i = d['day']+'-'+d['month']+'-'+d['year']
    elif set == 'season':
        i = xbmcgui.Dialog().select('Choose Season Numbering', ['year', 's02e12', '02x12', 'number', 'regex'])
        if i == 0:
            i = 'year'
        elif i == 1:
            i = 's02e12'
            m_xml.xml_update_playlist_setting(id, 'episode', i, type=type) #Set this for episode as well
        elif i == 2:
            i = '02x12'
            m_xml.xml_update_playlist_setting(id, 'episode', i, type=type) #Set this for episode as well
        elif i == 3:
            i = xbmcgui.Dialog().numeric(0, 'Set a hardcoded episode number')
        elif i == 4:
            i = dev.user_input('', 'Set a regular expression')
        #m_xml.xml_update_playlist_setting(id, set, i) #Save the new setting
    elif set == 'episode':
        i = xbmcgui.Dialog().select('Choose Episode Numbering', ['Default', 's02e12', '02x12', 'monthday', 'pos', 'number', 'regex'])
        if i == 0:
            i = 'default'
        elif i == 1:
            i = 's02e12'
            m_xml.xml_update_playlist_setting(id, 'season', i, type=type) #Set this for season as well
        elif i == 2:
            i = '02x12'
            m_xml.xml_update_playlist_setting(id, 'season', i, type=type) #Set this for season as well
        elif i == 3:
            i = 'monthday'
        elif i == 4:
            i = 'pos'
        elif i == 5:
            i = xbmcgui.Dialog().numeric(0, 'Set a hardcoded episode number')
        elif i == 6:
            i = dev.user_input('', 'Set a regular expression')
        #m_xml.xml_update_playlist_setting(id, set, i) #Save the new setting
    elif set == 'onlygrab':
        options = ['0', '50', '100', '250', '500', '1000', '5000', '10000']
        i = xbmcgui.Dialog().select('Choose max old videos to grab', options)
        i = options[i]
        #m_xml.xml_update_playlist_setting(id, set, i) #Save the new setting
    elif set == 'updateevery':
        options = ['every 4 hours', 'every 8 hours', 'every 12 hours', 'every 24 hours', 'every 168 hours', 'every day', 'every sunday', 'every monday', 'every tuesday', 'every wednesday', 'every thursday', 'every friday', 'every saturday']
        i = xbmcgui.Dialog().select('Choose when to update this playlist', options)
        i = options[i]
    elif set == 'update_gmt':
        options = dev.timezones()
        i = xbmcgui.Dialog().select('In which timezone should this list be updated?', options)
        i = options[i]
        #m_xml.xml_update_playlist_setting(id, set, i) #Save the new setting
    elif set == 'minlength':
        i = xbmcgui.Dialog().numeric(2, 'Set a minimum length for videos')
    elif set == 'maxlength':
        i = xbmcgui.Dialog().numeric(2, 'Set a maximum length for videos')
    elif set == 'updateat':
        i = xbmcgui.Dialog().numeric(2, 'Update this playlist on this time of the day')
    elif set == 'reverse':
        i = xbmcgui.Dialog().yesno("Reverse Playlist", "Reverse this playlist? \n\r (Only use this if the playlist is sorted oldest->newest and you cant find a playlist sorted newest->oldest)")
        i = str(i)
    
    
    ###MOVIES
    elif set == 'search_imdb':
        i = xbmcgui.Dialog().select(dev.lang(30504), ['Yes, fallback on addon settings', 'Yes, dont add if imdb fails', 'No, just use addon settings'])
        i = str(i)
    elif set == 'imdb_match_cutoff':
        options = ['25', '40', '50', '60', '70', '75', '80', '85', '90', '95', '99', '100']
        i = xbmcgui.Dialog().select(dev.lang(30505), options)
        i = options[i]
    elif set == 'use_ytimage':
        options = ['Only if no image found on IMDB', 'Always', 'Dont add if no image is found on IMDB', 'Never']
        i = xbmcgui.Dialog().select(dev.lang(30520), options)
        i = str(i)
    elif set == 'smart_search':
        i = xbmcgui.Dialog().yesno("Smart Search", "Enable Smart Search?")
        i = str(i)

    
    
    ###MUSIC VIDEOS
    #genre
    elif set == 'genre' and type == 'musicvideo':
        i = xbmcgui.Dialog().select('Choose genre Recognizition', ['hardcoded'])
        if i == 0:
            i = 'hardcoded'
    elif set == 'genre_fallback' and type == 'musicvideo':
        i = xbmcgui.Dialog().select('Choose genre Recognizition Fallback', ['hardcoded', 'do not add'])
        if i == 0:
            i = 'hardcoded'
        elif i == 1:
            i = 'do not add'
    #Song Fallback
    elif set == 'song_fallback' and type == 'musicvideo':
        i = xbmcgui.Dialog().select('Choose Song Recognizition Fallback', ['video title', 'video title (original)', 'do not add'])
        if i == 0:
            i = 'video title'
        elif i == 1:
            i = 'video title (original)'
        elif i == 2:
            i = 'do not add'
    #Artist
    elif set == 'artist':
        i = xbmcgui.Dialog().select('Choose Artist Recognizition', ['video title and description', 'playlist channelname', 'video channelname', 'hardcoded'])
        if i == 0:
            i = 'video title and description'
        elif i == 1:
            i = 'playlist channelname'
        elif i == 2:
            i = 'video channelname'
        elif i == 3:
            i = 'hardcoded'
    elif set == 'artist_fallback':
        i = xbmcgui.Dialog().select('Choose Artist Recognizition Fallback', ['hardcoded', 'playlist channelname', 'video channelname', 'do not add'])
        if i == 0:
            i = 'hardcoded'
        elif i == 1:
            i = 'playlist channelname'
        elif i == 2:
            i = 'video channelname'
        elif i == 3:
            i = 'do not add'
    #album		
    elif set == 'album':
        i = xbmcgui.Dialog().select('Choose album Recognizition', ['video title and description', 'artist + published year', 'hardcoded'])
        if i == 0:
            i = 'video title and description'
        elif i == 1:
            i = 'artist + published year'
        elif i == 2:
            i = 'hardcoded'
    elif set == 'album_fallback':
        i = xbmcgui.Dialog().select('Choose album Recognizition Fallback', ['hardcoded', 'published year', 'do not add'])
        if i == 0:
            i = 'hardcoded'
        elif i == 1:
            i = 'published year'
        elif i == 2:
            i = 'do not add'
    #plot
    elif set == 'plot':
        i = xbmcgui.Dialog().select('Choose plot Recognizition', ['lyrics in video description', 'video description', 'playlist description', 'hardcoded'])
        if i == 0:
            i = 'lyrics in video description'
        elif i == 1:
            i = 'video description'
        elif i == 2:
            i = 'playlist description'
        elif i == 3:
            i = 'hardcoded'
    elif set == 'plot_fallback':
        i = xbmcgui.Dialog().select('Choose plot Recognizition Fallback', ['hardcoded', 'video description', 'playlist description', 'do not add'])
        if i == 0:
            i = 'hardcoded'
        elif i == 1:
            i = 'video description'
        elif i == 2:
            i = 'playlist description'
        elif i == 3:
            i = 'do not add'
    #year
    elif set == 'year':
        i = xbmcgui.Dialog().select('Choose year Recognizition', ['video title and description', 'published year', 'hardcoded'])
        if i == 0:
            i = 'video title and description'
        elif i == 1:
            i = 'published year'
        elif i == 2:
            i = 'hardcoded'
    elif set == 'year_fallback':
        i = xbmcgui.Dialog().select('Choose year Recognizition Fallback', ['hardcoded', 'published year', 'do not add'])
        if i == 0:
            i = 'hardcoded'
        elif i == 1:
            i = 'published year'
        elif i == 2:
            i = 'do not add'
            
            
    ### NORMAL SETTING
    else:
        #Its another setting, so its normal text
        elem = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type) #Find this playlist so we can grab the value of the settings
        setting = None
        if elem.find(set) != None:
            setting = str(elem.find(set).text) #Convert the setting to a string so we can input it safely
        if setting == None or setting == 'None':
            setting = ''
        i = dev.user_input(setting, 'Change setting '+set) #Ask the user to put in the new setting
    
    m_xml.xml_update_playlist_setting(id, set, i, type=type) #Save the new setting

        
        
#Displays the settings from the settings.xml file and gives the option to edit the functions
def editPlaylist(id, type=''):
    global plid #Make the plid global so disp_setting can reach it without calling it
    global elem #Make the elem global so disp_setting can reach it without calling it
    global fanart #Make fanart global so disp_setting can reach it without calling it
    global gear #Make gear global so disp_setting can reach it without calling it
    global pltype #make type global so disp_setting can reach it without calling it
    plid = id
    pltype = type
    dev.log('editPlaylist('+id+', '+type+')')
    #Loads the correct information from the settings.xml
    elem = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type)
    if elem is None:
        #We could not find this playlist to edit!
        dev.log('Could not find playlist '+id+' ('+type+') to edit!')
        return False
    else:
        '''
            Build the edit Playlist form
        '''
        #Grab all art to be used with this playlist edit
        thumb = elem.find('thumb').text
        fanart = elem.find('fanart').text
        gear = dev.media('gear')
        
        #Return to home button
        url = dev.build_url({'home': 'home'})
        dev.adddir('[COLOR white]Return to Main Menu[/COLOR]', url, dev.media('home'), fanart)
        #Edit playlist info
        url = dev.build_url({'mode': 'editPlaylist', 'id': id, 'type': type})
        dev.adddir('[COLOR white]Editing Settings for playlist '+id+'[/COLOR]', url, thumb, fanart, 'This is the edit page for the playlist settings. Set this to your taste to have more control over things as which videos will be included or excluded')
        #Delete playlist
        url = dev.build_url({'mode': 'deletePlaylist', 'id': id, 'type': type})
        dev.adddir('[COLOR red]Delete playlist[/COLOR]', url, dev.media('delete'), fanart, '<!> Careful! <!> This will delete all the settings from this playlist & this playlist will not be scanned into your library anymore')
        #Refresh playlist
        url = dev.build_url({'mode': 'refreshPlaylist', 'id': id, 'type': type})
        dev.adddir('[COLOR red]Refresh playlist[/COLOR]', url, dev.media('delete'), fanart, '<!> Careful! <!> This will refresh all the episodes from this playlist. Only use this if previous episodes are not scanned properly due to wrong playlist settings.')
        
        #Build the Playlist enable/disable button depending on current state
        if elem.attrib['enabled'] == 'yes':
            url = dev.build_url({'mode': 'editPlaylist', 'id': id, 'set': 'enable', 'type': type})
            dev.adddir('[COLOR green]Playlist is enabled[/COLOR]', url, thumb, fanart, 'The playlist is enabled. Disable it to stop the videos to be scanned into the Kodi Library. \n It is also a good idea to disable it if it only contains videos that wont be updated. That way you spare some precious computer resources.')
        else:
            url = dev.build_url({'mode': 'editPlaylist', 'id': id, 'set': 'enable', 'type': type})
            dev.adddir('[COLOR red]Playlist is disabled![/COLOR]', url, thumb, fanart, 'The playlist is disabled, so you can change your settings before scanning into your Kodi Library. When you are done setting up this playlist, enable it so it gets scanned into the Kodi Library.')
        
        
        #Title
        extra_desc = ''
        if type == '' or type == 'tv':
            extra_desc = 'Kodi and'
        disp_setting('title', 'Title', 'The title as it will be displayed in '+extra_desc+' this Addon')
        #Description
        disp_setting('description', 'Description', 'The description as it will be displayed in '+extra_desc+' this Addon')
        #Tags
        disp_setting('tags', 'Tags', 'Tags for Kodi. For multiple tags use tag1 / tag2 / tag3 (note the space between each / )')
        #Genres & Stuff
        if type == 'musicvideo':
            #Genres
            #disp_setting('genre', 'Genre', 'Genre Recognizition', 1)
            genre = elem.find('genre').text
            if genre != 'hardcoded' and genre != 'video title' and genre != 'playlist channelname' and genre != 'published year' and genre != 'video channelname' and genre != 'artist + published year' and genre != 'video description':
                disp_setting('genre_fallback', 'Genre Fallback', dev.lang(31900), 1)
            disp_setting('genre_hardcoded', 'Genre Hardcoded', dev.lang(31901)+' \n For multiple genres use genre1 / genre2 / genre3 (note the space between each / )')            
            
            #Skip
            disp_bool_setting('skip_audio', 'Skip Audio Only', 'If enabled, tries to skip videos that are audio only')
            disp_bool_setting('skip_lyrics', 'Skip Lyrics', 'If enabled, tries to skip Lyric videos')
            disp_bool_setting('skip_live', 'Skip Live', 'If enabled, tries to skip Live videos')
            disp_bool_setting('skip_albums', 'Skip Albums', 'If enabled, tries to skip Album videos')
            
            #Song Fallback
            disp_setting('song_fallback', 'Song Fallback', 'Song Fallback', 1)            
            #artists
            disp_setting('artist', 'artist', 'Artist Recognizition', 1)
            artist = elem.find('artist').text
            if artist != 'hardcoded' and artist != 'video title' and artist != 'playlist channelname' and artist != 'published year' and artist != 'video channelname' and artist != 'artist + published year' and artist != 'video description':
                disp_setting('artist_fallback', 'Artist Fallback', dev.lang(31900), 1)
            if elem.find('artist').text == 'hardcoded' or elem.find('artist_fallback').text == 'hardcoded':
                disp_setting('artist_hardcoded', 'Artist Hardcoded', dev.lang(31901))
            #albums
            disp_setting('album', 'album', 'Album Recognizition', 1)
            album = elem.find('album').text
            if album != 'hardcoded' and album != 'video title' and album != 'playlist channelname' and album != 'published year' and album != 'video channelname' and album != 'artist + published year' and album != 'video description':
                disp_setting('album_fallback', 'album Fallback', dev.lang(31900), 1)
            if elem.find('album').text == 'hardcoded' or elem.find('album_fallback').text == 'hardcoded':
                disp_setting('album_hardcoded', 'album Hardcoded', dev.lang(31901))
            #plots
            disp_setting('plot', 'plot', 'plot Recognizition', 1)
            plot = elem.find('plot').text
            if plot != 'hardcoded' and plot != 'video title' and plot != 'playlist channelname' and plot != 'published year' and plot != 'video channelname' and plot != 'artist + published year' and plot != 'video description':
                disp_setting('plot_fallback', 'plot Fallback', dev.lang(31900), 1)
            if elem.find('plot').text == 'hardcoded' or elem.find('plot_fallback').text == 'hardcoded':
                disp_setting('plot_hardcoded', 'plot Hardcoded', dev.lang(31901))
            #years
            disp_setting('year', 'year', 'year Recognizition', 1)
            year = elem.find('year').text
            if year != 'hardcoded' and year != 'video title' and year != 'playlist channelname' and year != 'published year' and year != 'video channelname' and year != 'artist + published year' and year != 'video description':
                disp_setting('year_fallback', 'year Fallback', dev.lang(31900), 1)
            if elem.find('year').text == 'hardcoded' or elem.find('year_fallback').text == 'hardcoded':
                disp_setting('year_hardcoded', 'year Hardcoded', dev.lang(31901))
            
        else:
            #Genre
            disp_setting('genre', 'Genre', 'Settings as displayed in Kodi. For multiple genres use genre1 / genre2 / genre3 (note the space between each / )')
        
        ###MOVIES
        if type == 'movies':
            disp_setting('set', dev.lang(30519), 'The set the movies will belong to in the Kodi library')
            if vars.mode > 1: #Expert mode
                disp_bool_setting('smart_search', dev.lang(30521), 'Use some smart filters to strip out must unwanted stuff from titles. Also try to guess info like Director and year in the process.')
            disp_setting('search_imdb', dev.lang(30504), 'Do you want to try to find a match on imdb? And if so, what to do if no match is found?')
            if vars.mode > 1:
                disp_setting('imdb_match_cutoff', dev.lang(30505), 'How much of a percentage does the title need to match the IMDB result?')
            disp_setting('use_ytimage', dev.lang(30520), 'In case of an IMDB match, would you still like to use the Youtube Image as the Poster image?')
        
        
        #Published
        if type == '' or type == 'tv':
            disp_setting('published', 'Published', 'The date the show first aired', 1)
        #WriteNFO
        if vars.mode > 0:
            disp_bool_setting('reverse', dev.lang(30522), 'Reverse this playlist? \n\r (Only use this if the playlist is sorted oldest->newest and you cant find a playlist sorted newest->oldest)')
        
            #Only get last X videos
            disp_setting('onlygrab', 'Grab last X videos', 'Instead of adding all old episodes, only add the last X episodes')
            
            
            disp_setting('updateevery', 'Update every', 'Update this playlist at a specific time interval or day')
            disp_setting('updateat', 'Update at', 'Update this playlist at a specific time if updateevery is set to a specific day.  (This setting is ignored when "update every" is set to every X hours)')
            disp_setting('update_gmt', 'Timezone', 'Set the timezone for this playlist. YTlibrary will calculate the time to update according to the difference to your current timezone. (This setting is ignored when "update every" is set to every X hours)')
        
            url = dev.build_url({'mode': 'editPlaylist', 'id': id, 'set': 'writenfo', 'type': type})
            dev.adddir('[COLOR blue]Write NFO:[/COLOR] '+elem.find('writenfo').text, url, gear, fanart, 'NFO Files are needed for Kodi to recognise the youtube episodes as episodes, so it can scan it in its library. If you only want strm files, set this to No')
            
            #Filters
            #Only include
            disp_setting('onlyinclude', 'Only Include', 'Only include videos containing the following text in the title. Placing words in between | will create an or. So review|trailer will only pick up videos with either review or trailer in its title')
            #Exclude words
            disp_setting('excludewords', 'Exclude', 'Excludes videos containing the following text in the title. Placing words in between | will create an or. So review|trailer will refuse videos with either review or trailer in its title')
            #Min Length
            disp_setting('minlength', 'Min length', 'Only include videos with this minimum length')
            #Max Length
            disp_setting('maxlength', 'Max length', 'Only include videos under this maximum length')
        
        #NFO Options
        if type == '' or type == 'tv':
            #Season recognisition setting
            description = """Set to [COLOR blue]year[/COLOR] to have the episode year upload date as its season.
-------
[COLOR blue]s02e12[/COLOR] to grab the season/episode numbering as s02e12 from the title. 
-------
[COLOR blue]02x12[/COLOR] to grab the season/episode numbering as 02x12 from the title. 
-------
Set to a [COLOR blue]number[/COLOR] to have a hardcoded season for every season. 
-------
To find a season from the video title using a [COLOR blue]regex[/COLOR]. Please use regex(yourregexhere). If your regex fails to recognise a season it will fallback on calling it 0.
            """
            disp_setting('season', 'Season recognisition', description)
            #Episode recognisition setting
            description = """'[COLOR blue]Default[/COLOR] will only number the episodes scanned in the library starting with 1 each season.
------
[COLOR blue]s02e12[/COLOR] to grab the season/episode numbering as s02e12 from the title. 
------
[COLOR blue]02x12[/COLOR] to grab the season/episode numbering as 02x12 from the title. 
------
[COLOR blue]monthday[/COLOR] to have the month & day upload date as its episode number. 
------
[COLOR blue]pos[/COLOR] to have it use its playlist position as its episode number (Know that when videos are removed from the playlist, episode numbering may not be correct for episodes already scanned into the library). 
------
Set to a [COLOR blue]number[/COLOR] to have a hardcoded episode for every episode. 
------
Use [COLOR blue]regex[/COLOR] to type in a regular expression. Please use regex(yourregexhere). If your regex fails to recognise a episode it will fallback on calling it 0.'
            """
            disp_setting('episode', 'Episode recognisition', description)
        if vars.mode > 0: #Normal mode or higher
            #Stripdescription
            disp_setting('stripdescription', 'Strip Description', 'Deletes every text in the description from and including the text filled in here. For instance, if a channel always has a long text in its description thats always the same, like: Check out our website (..). You fill that line in here, and only the part before that line will be included in the description of episodes. For multiple lines to scan for put them between |')
            #removedescription
            disp_setting('removedescription', 'Remove Description', 'Removes this line from the description of episodes.')
            #Striptitle
            disp_setting('striptitle', 'Strip Title', 'Same as stripdescription but for the title')
            #Removetitle
            disp_setting('removetitle', 'Remove Title', 'Same as removedescription but for the title')
        if vars.mode > 1: #Expert mode or higher
            #Overwritefolder
            disp_setting('overwritefolder', 'Folder', 'Use this directory to write the strm & nfo files to. If this is not filled in it will use the title as it will be displayed in the Addon and the Kodi Library')
        
        #Not used (yet)
        #Type
        #disp_setting('type', 'Type', '(NOT USED YET) What kind of playlist is this? Possible choices: tv/music/music videos')
        #Delete
        #disp_setting('delete', 'Delete older', '(NOT USED YET) Removes videos older then this many hours.')
        #Scansince
        #disp_setting('scansince', 'From date', '(NOT USED YET) Skip videos published under this date. But doesnt remove the nfo & strm files like Delete older')

        
#### DELETES A PLAYLIST ####
#Deletes a playlist and has an option to remove the directory containing the file to
def delete_playlist(id, type=''):
    #Grab the settings from this playlist
    settings = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type) #Grab the xml settings for this playlist
    if settings is None:
        dev.log('deletePlaylist: Could not find playlist '+id+' in the '+dev.typeXml(type)+' file', True)
        return False
    else:         
        i = xbmcgui.Dialog().yesno("Delete Playlist", "Are you sure you want to delete this playlist?")
        if i == 0:
            editPlaylist(id, type=type)
        else:
            if m_xml.xml_remove_playlist(id, type=type) is True:
                #Remove the episodenr xml file to
                file = os.path.join(vars.settingsPath+dev.typeEpnr(type), id+'.xml' )
                if os.path.isfile(file):
                    success = os.remove(file) #Remove the episodenr xml file
                
                xbmcgui.Dialog().ok('Removed Playlist', 'Succesfully removed playlist '+id)
                i = xbmcgui.Dialog().yesno('Delete from library', 'Do you also want to delete the videos from your library?')
                if i != 0:
                    #Check in which folder the show resides
                    folder = settings.find('overwritefolder').text
                    if folder is None or folder == '':
                        folder = dev.legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
                    else:
                        folder = dev.legal_filename(folder)
                    movieLibrary = vars.tv_folder #Use the directory from the addon settings
                    if type == 'musicvideo':
                        movieLibrary = vars.musicvideo_folder
                    elif type == 'movies':
                        movieLibrary = vars.movies_folder
                    dir = os.path.join(movieLibrary, folder) #Set the folder to the maindir/dir
                    
                    success = shutil.rmtree(dir, ignore_errors=True) #Remove the directory
                    xbmcgui.Dialog().ok('Removed from library', 'Deleted the videos from your library (You should clean your library, otherwise they will still show in your library)')
            

#Refresh a playlist and has an option to remove the directory containing the file to
def refresh_playlist(id, type=''):
    #Grab the settings from this playlist
    settings = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type) #Grab the xml settings for this playlist
    if settings is None:
        dev.log('refreshPlaylist: Could not find playlist '+id+' in the '+typeXml(type)+' file', True)
        return False
    else:         
        i = xbmcgui.Dialog().yesno("Refresh Playlist", "Are you sure you want to refresh this playlist?")
        if i != 0:
            m_xml.xml_update_playlist_setting(id, 'lastvideoId', '', type=type)
            #Delete the .xml containing all scanned videoId's as well
            file = os.path.join(vars.settingsPath, dev.typeEpnr(type))
            file = os.path.join(file, id+'.xml')
            if os.path.isfile(file):
                success = os.remove(file) #Remove the episodenr xml file
            
            xbmcgui.Dialog().ok('Refreshed Playlist', 'Succesfully refreshed playlist '+id)
            i = xbmcgui.Dialog().yesno('Delete from library', 'Do you also want to delete the previous videos from your library?')
            if i != 0:
                #Check in which folder the show resides
                folder = settings.find('overwritefolder').text
                if folder is None or folder == '':
                    folder = dev.legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
                else:
                    folder = dev.legal_filename(folder)
                movieLibrary = vars.tv_folder #Use the directory from the addon settings
                if type == 'musicvideo':
                    movieLibrary = vars.musicvideo_folder
                elif type == 'movies':
                    movieLibrary = vars.movies_folder
                dir = os.path.join(movieLibrary, folder) #Set the folder to the maindir/dir
                
                success = shutil.rmtree(dir, ignore_errors=True) #Remove the directory
                #if vars.update_videolibrary == "true" and type=='':
                #    update_dir = vars.tv_folder_path
                #    if type == 'musicvideo':
                #        update_dir = vars.musicvideo_folder_path
                #    dev.log('Updating video library is enabled. Cleaning librarys directory %s' % update_dir, True)
                #    xbmc.executebuiltin('xbmc.updatelibrary(Video,'+update_dir+')')

                xbmcgui.Dialog().ok('Removed from library', 'Deleted the previous videos from your library (You should clean your library, otherwise they will still show in your library)')
            editPlaylist(id, type=type) #Load the editplaylist view