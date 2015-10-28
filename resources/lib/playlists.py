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

from resources.lib import vars
from resources.lib import dev
from resources.lib import m_xml


#Displays the editplaylist list item
def disp_setting(setting, title, description):
    #build url
    if elem.find(setting) != None:
        val = elem.find(setting).text
    if val == None or val == 'None':
        val = ''
    url = dev.build_url({'mode': 'editPlaylist', 'id': plid, 'set': setting})
    dev.adddir('[COLOR blue]'+title+':[/COLOR] '+val, url, gear, fanart, description)


#Displays and saves the user input if something from editplaylist should be set
def setEditPlaylist(id, set):
    if set == 'enable':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("Enable", "Would you like to enable this playlist?")
        if i == 0:
            m_xml.xml_update_playlist_attr(id, 'enabled', 'no')
            #dialog.ok("Set to disabled", "Playlist is disabled.")
        else:
            m_xml.xml_update_playlist_attr(id, 'enabled', 'yes')
            #dialog.ok("Set to enabled", "Playlist will now be picked up by the scanner")
    elif set == 'writenfo':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("WriteNFO", "Write NFO files for this playlist?")
        if i == 0:
            m_xml.xml_update_playlist_setting(id, 'writenfo', 'no')
        else:
            m_xml.xml_update_playlist_setting(id, 'writenfo', 'Yes')
    else:
        #Its another setting, so its normal text
        elem = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Find this playlist so we can grab the value of the settings
        setting = str(elem.find(set).text) #Convert the setting to a string so we can input it safely
        if setting == None or setting == 'None':
            setting = ''
        result = dev.user_input(setting, 'Change setting '+set) #Ask the user to put in the new setting
        m_xml.xml_update_playlist_setting(id, set, result) #Save the new setting

        
        
#Displays the settings from the settings.xml file and gives the option to edit the functions
def editPlaylist(id):
    global plid #Make the plid global so disp_setting can reach it without calling it
    global elem #Make the elem global so disp_setting can reach it without calling it
    global fanart #Make fanart global so disp_setting can reach it without calling it
    global gear #Make gear global so disp_setting can reach it without calling it
    plid = id
    dev.log('editPlaylist('+id+')')
    #Loads the correct information from the settings.xml
    elem = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id})
    if elem is None:
        #We could not find this playlist to edit!
        dev.log('Could not find playlist '+id+' to edit!')
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
        url = dev.build_url({'mode': 'editPlaylist', 'id': id})
        dev.adddir('[COLOR white]Editing Settings for playlist '+id+'[/COLOR]', url, thumb, fanart, 'This is the edit page for the playlist settings. Set this to your taste to have more control over things as which videos will be included or excluded')
        #Delete playlist
        url = dev.build_url({'mode': 'deletePlaylist', 'id': id})
        dev.adddir('[COLOR red]Delete playlist[/COLOR]', url, dev.media('delete'), fanart, '<!> Careful! <!> This will delete all the settings from this playlist & this playlist will not be scanned into your library anymore')
        #Refresh playlist
        url = dev.build_url({'mode': 'refreshPlaylist', 'id': id})
        dev.adddir('[COLOR red]Refresh playlist[/COLOR]', url, dev.media('delete'), fanart, '<!> Careful! <!> This will refresh all the episodes from this playlist. Only use this if previous episodes are not scanned properly due to wrong playlist settings.')
        
        #Build the Playlist enable/disable button depending on current state
        if elem.attrib['enabled'] == 'yes':
            url = dev.build_url({'mode': 'editPlaylist', 'id': id, 'set': 'enable'})
            dev.adddir('[COLOR green]Playlist is enabled[/COLOR]', url, thumb, fanart, 'The playlist is enabled. Disable it to stop the videos to be scanned into the Kodi Library')
        else:
            url = dev.build_url({'mode': 'editPlaylist', 'id': id, 'set': 'enable'})
            dev.adddir('[COLOR red]Playlist is disabled![/COLOR]', url, thumb, fanart, 'The playlist is disabled, so you can change your settings before scanning into your Kodi Library. When youre done setting up this playlist, enable it so its gets scanned into the Kodi Library.')
        
        #Title
        disp_setting('title', 'Title', 'The title as it will be displayed in Kodi and this Addon')
        #Description
        disp_setting('description', 'Description', 'The description as it will be displayed in Kodi and this Addon')
        #Genres
        disp_setting('genre', 'Genre', 'Settings as displayed in Kodi. For multiple genres use genre1/genre2/genre3')
        #WriteNFO
        url = dev.build_url({'mode': 'editPlaylist', 'id': id, 'set': 'writenfo'})
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
        #Season recognisition setting
        disp_setting('season', 'Season recognisition', 'Set to year to have the episode year upload date as its season. Set to a number to have a hardcoded season for every episode. To find a season from the video title using a regex. Please use regex(yourregexhere). If your regex fails to recognise a season it will fallback on calling it 0.')
        #Episode recognisition setting
        disp_setting('episode', 'Episode recognisition', 'Set to monthday to have the episode month & day upload date as its episode number. Set to pos to have it use its playlist position as its episode number (Know that when videos are removed from the playlist, episode numbering may not be correct for episodes already scanned into the library). Set to a number to have a hardcoded episode for every episode. To find a episode from the video title using a regex. Please use regex(yourregexhere). If your regex fails to recognise a episode it will fallback on calling it 0.')
        #Stripdescription
        disp_setting('stripdescription', 'Strip Description', 'Deletes every text in the description from and including the text filled in here. For instance, if a channel always has a long text in its description thats always the same, like: Check out our website (..). You fill that line in here, and only the part before that line will be included in the description of episodes. For multiple lines to scan for put them between |')
        #removedescription
        disp_setting('removedescription', 'Remove Description', 'Removes this line from the description of episodes.')
        #Striptitle
        disp_setting('striptitle', 'Strip Title', 'Same as stripdescription but for the title')
        #Removetitle
        disp_setting('removetitle', 'Remove Title', 'Same as removedescription but for the title')

        #Overwritefolder
        disp_setting('overwritefolder', 'Folder', 'Use this directory to write the strm & nfo files to. If this is not filled in it will use the title as it will be displayed in the Addon and the Kodi Library')

        
        #Not used (yet)
        #Type
        disp_setting('type', 'Type', '(NOT USED YET) What kind of playlist is this? Possible choices: tv/music/music videos')
        #Delete
        disp_setting('delete', 'Delete older', '(NOT USED YET) Removes videos older then this many hours.')
        #Scansince
        disp_setting('scansince', 'From date', '(NOT USED YET) Skip videos published under this date. But doesnt remove the nfo & strm files like Delete older')

        
#### DELETES A PLAYLIST ####
#Deletes a playlist and has an option to remove the directory containing the file to
def delete_playlist(id):
    #Grab the settings from this playlist
    settings = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Grab the xml settings for this playlist
    if settings is None:
        dev.log('deletePlaylist: Could not find playlist '+id+' in the settings.xml file', True)
        return False
    else:         
        i = xbmcgui.Dialog().yesno("Delete Playlist", "Are you sure you want to delete this playlist?")
        if i == 0:
            editPlaylist(id)
        else:
            if m_xml.xml_remove_playlist(id) is True:
                xbmcgui.Dialog().ok('Removed Playlist', 'Succesfully removed playlist '+id)
                i = xbmcgui.Dialog().yesno('Delete from library', 'Do you also want to delete the episodes from your library?')
                if i != 0:
                    #Check in which folder the show resides
                    folder = settings.find('overwritefolder').text
                    if folder is None or folder == '':
                        folder = dev.legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
                    else:
                        folder = dev.legal_filename(folder)
                    movieLibrary = vars.tv_folder #Use the directory from the addon settings
                    dir = os.path.join(movieLibrary, folder) #Set the folder to the maindir/dir
                    
                    success = shutil.rmtree(dir, ignore_errors=True) #Remove the directory
                    xbmcgui.Dialog().ok('Removed from library', 'Deleted this show from your library (You should clean your library, otherwise they will still show in your library)')
            

#Refresh a playlist and has an option to remove the directory containing the file to
def refresh_playlist(id):
    #Grab the settings from this playlist
    settings = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Grab the xml settings for this playlist
    if settings is None:
        dev.log('refreshPlaylist: Could not find playlist '+id+' in the settings.xml file', True)
        return False
    else:         
        i = xbmcgui.Dialog().yesno("Refresh Playlist", "Are you sure you want to refresh this playlist?")
        if i != 0:
            m_xml.xml_update_playlist_setting(id, 'lastvideoId', '')
            xbmcgui.Dialog().ok('Refreshed Playlist', 'Succesfully refreshed playlist '+id)
            i = xbmcgui.Dialog().yesno('Delete from library', 'Do you also want to delete the previous episodes from your library?')
            if i != 0:
                #Check in which folder the show resides
                folder = settings.find('overwritefolder').text
                if folder is None or folder == '':
                    folder = dev.legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
                else:
                    folder = dev.legal_filename(folder)
                movieLibrary = vars.tv_folder #Use the directory from the addon settings
                dir = os.path.join(movieLibrary, folder) #Set the folder to the maindir/dir
                
                success = shutil.rmtree(dir, ignore_errors=True) #Remove the directory
                xbmcgui.Dialog().ok('Removed from library', 'Deleted the previous episodes from your library (You should clean your library, otherwise they will still show in your library)')
            editPlaylist(id) #Load the editplaylist view