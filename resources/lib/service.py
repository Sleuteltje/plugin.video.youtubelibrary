#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions that will handle updating of playlists in the library (required functions for the service)
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
import xbmc, xbmcgui

from resources.lib import vars
from resources.lib import dev
from resources.lib import m_xml
from resources.lib import generators
from resources.lib import ytube


#Writes the nfo & strm files for all playlists
def update_playlists():
    xbmcgui.Dialog().notification(vars.__addonname__, 'Updating Youtube Playlists...', vars.__icon__, 3000)
    dev.log('Updating All Youtube Playlists')
    m_xml.xml_get()
    pl = m_xml.document.findall('playlists/playlist')
    if pl is not None: 
        for child in pl: #Loop through each playlist
            if child.attrib['enabled'] == 'yes': #Playlist has to be enabled
                update_playlist(child.attrib['id']) #Update the nfo & strm files for this playlist
    xbmcgui.Dialog().notification(vars.__addonname__, 'Done Updating Youtube Playlists', vars.__icon__, 3000)
    #Should we also update the video library?
    if vars.update_videolibrary == "true":
        dev.log('Updating video library is enabled. Updating librarys directory %s' % vars.tv_folder_path, True)
        xbmc.executebuiltin('xbmc.updatelibrary(Video,'+vars.tv_folder_path+')')
        
#Writes the nfo & strm files for the given playlist
def update_playlist(id):
    settings = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Grab the xml settings for this playlist
    if settings is None:
        dev.log('Could not find playlist '+id+' in the settings.xml file', True)
        return False
    else:
        dev.log('Updating playlist %s (Id: %s)' % (settings.find('title').text, id))
        #Check in which folder the show should be added
        folder = settings.find('overwritefolder').text
        if folder is None or folder == '':
            folder = dev.legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
        else:
            folder = dev.legal_filename(folder)
        
        #Create the tvshow.nfo
        writenfo = settings.find('writenfo').text
        if writenfo != 'no':
            generators.write_tvshow_nfo(folder, settings)
        
        update_playlist_vids(id, folder, settings)
    
        return True

#Updates the videos of a playlist
    #the id of the playlist
    #the folder where the strm & nfo files should go
    #the elementtree element containing the playlist xml settings
    #the id of the fist videoId, so it can save that one in the xml if it parsed all videos. Since the newest is the video it should be stopping the next time.
def update_playlist_vids(id, folder, settings, nextpage=False, firstvid = False):
    resp = ytube.vids_by_playlist(id, nextpage) #Grab the videos belonging to this playlist
    vids = resp.get("items", [])
    if firstvid == False:
        #Save the first videoId for later reference
        for vid in vids:
            firstvid = vid['contentDetails']['videoId']
            break #we only want the first item
            
    lastvid = False
    lastvidId = settings.find('lastvideoId').text #Grab the lastvideoId that has been processed from the xml
    
    #Grab settings from the settings.xml for this playlist
    minlength = settings.find('minlength').text
    maxlength = settings.find('maxlength').text
    
    if minlength is not '' and minlength is not None:
        #Recalculate minlength
        minlength = ytube.hms_to_sec(minlength)
    else:
        minlength = None
    if maxlength is not '' and maxlength is not None:
        #Recalculate maxlength
        maxlength = ytube.hms_to_sec(maxlength)
    else:
        maxlength = None
    
        
    #Grab the duration of the videos. We will need it for the minlength and maxlength filters, and for the duration tag in the .nfo file
    #We are gonna grab the duration of all 50 videos, saving on youtube api calls.
    dev.log('Grabbing duration of videos')
    all_vidids = []
    for vid in vids:
        if vid['snippet']['title'] != 'Private video' and vid['snippet']['title'] != 'Deleted Video':
            all_vidids.append(vid['contentDetails']['videoId']) #Collect all videoids in one list
    duration = ytube.get_duration_vids(all_vidids) #Get all the duration of the videos
    
    #Loop through all 50< vids and check with filters if we should add it
    for vid in vids:
        #Check if we already had this video, if so we should skip it
        if vid['contentDetails']['videoId'] == lastvidId:
            lastvid = True
            #Appereantly Youtube sometimes has a different order in the playlist as it is on the website. Very annoying. To make it more likely that we grab every new video, we will go through all 50 videos. Just in case the newest video got stuck on position 5 or 6 or something. Should the newest video get stuck on place 51 or lower, it wont get picked up at all. If a playlist is sorted from old to new, instead of new to old,  new videos above position 51 will not get picked up at all.
            dev.log('Playlist is up to date in the library. Already have '+settings.find('lastvideoId').text+' in the library. Since Youtube does not always have the correct order, every video on this page will still be checked if it exists, and if not, will be created')
            break #Skip this video, since we already created this video
        #Check if we created this episode already
        #if 
        #Check if this video is private or deleted. Deleted or private videos should not be added
        if vid['snippet']['title'] == 'Private video' or vid['snippet']['title'] == 'Deleted Video':
            continue #Skip this video
        #Check if the filters in the settings prevent this video from being added
        if settings.find('onlyinclude').text is not '' and settings.find('onlyinclude').text is not None:
            found = False
            #Check if there are | ,if so we should loop through each onlyinclude word
            if '|' in settings.find('onlyinclude').text:
                strip = settings.find('onlyinclude').text.split('|')
            else:
                strip = []
                strip.append(settings.find('onlyinclude').text)
            for s in strip:
                if s in vid['snippet']['title']:
                    found = True
                    break #We found one of the words in the title, so this one is safe to add
            #Check if the word has been found, cause if not, we should not add this video to the library
            if found == False:
                continue #Skip this video
        #Check if the filters in the settings prevent this video from being added
        if settings.find('excludewords').text is not '' and settings.find('excludewords').text is not None:
            found = False
            #Check if there are | ,if so we should loop through each onlyinclude word
            if '|' in settings.find('excludewords').text:
                strip = settings.find('excludewords').text.split('|')
            else:
                strip = []
                strip.append(settings.find('excludewords').text)
            for s in strip:
                if s in vid['snippet']['title']:
                    found = True
                    break #We found one of the words in the title, so this one should not be added
            #Check if the word has been found, cause if so, we should not add this video to the library
            if found == True:
                continue #Skip this video
        #See if this video is smaller or larger than the min-/maxlength specified in the settings
        if minlength is not None:
            if int(minlength) > int(duration[vid['contentDetails']['videoId']]):
                continue #Skip this video
        if maxlength is not None:
            if int(maxlength) < int(duration[vid['contentDetails']['videoId']]):
                continue #Skip this video
                
        
                
        #Grab the correct season and episode number from this vid
        se = generators.episode_season(vid, settings, resp['pageInfo']['totalResults'])
        season = se[0]
        episode = se[1]
        filename = 's'+season+'e'+episode+' - '+vid['snippet']['title'] #Create the filename for the .strm & .nfo file
        
        generators.write_strm(filename, folder, vid['contentDetails']['videoId'], show=settings.find('title').text, episode=episode, season=season) #Write the strm file for this episode
        if settings.find('writenfo').text != 'no':
            generators.write_nfo(filename, folder, vid, settings, season = season, episode = episode, duration = duration[vid['contentDetails']['videoId']]) #Write the nfo file for this episode
    
    #If there is a nextPagetoken there are more videos to parse, call this function again so it can parse them to
    if 'nextPageToken' in resp and lastvid is not True:
        update_playlist_vids(id, folder, settings, resp['nextPageToken'], firstvid)
    else:
        if firstvid != False:
            m_xml.xml_update_playlist_setting(id, 'lastvideoId', firstvid) #Set the lastvideoId to this videoId so the playlist remembers the last video it has. This will save on API calls, since it will quit when it comes across a video that already has been set
        dev.log('Done ripping videos from playlist '+settings.find('title').text+' (ID: '+id+') firstvid id: '+firstvid)
