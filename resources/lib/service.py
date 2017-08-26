# -*- coding: utf-8 -*-
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
import xbmc, xbmcgui, xbmcaddon

from resources.lib import vars
from resources.lib import dev
from resources.lib import m_xml
from resources.lib import generators
from resources.lib import ytube
from resources.lib import play


#Outputs the updatevery setting in normal 
def updateevery_normal(t, time, scansince, update_gmt):
    import datetime
    if time is None:
        hour = 23
        minute = 59
    else:
        hour = int(time[:2])
        minute = int(time[3:5])
        
    if t == 'every 4 hours':
        return scansince + datetime.timedelta(hours=4)
    if t == 'every 8 hours':
        return scansince + datetime.timedelta(hours=8)
    if t == 'every 12 hours':
        dev.log('12 hours since last scan is: '+str(scansince + datetime.timedelta(hours=12)))
        return scansince + datetime.timedelta(hours=12)
    if t == 'every 24 hours':
        return scansince + datetime.timedelta(hours=24)
    if t == 'every 168 hours':
        return scansince + datetime.timedelta(hours=168)
    
    
    dev.log('t is '+t)
    today = datetime.datetime.now()
    weekday = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
    
    y = today
    if t == 'every sunday':
        if weekday is not 0:
            y = today - datetime.timedelta(7+weekday)
    if t == 'every monday':
        if weekday is not 1:
            y = today - datetime.timedelta(7+weekday-1)
    if t == 'every tuesday':
        if weekday is not 2:
            y = today - datetime.timedelta(7+weekday-2)
    if t == 'every wednesday':
        if weekday is not 3:
            y = today - datetime.timedelta(7+weekday-3)
    if t == 'every thursday':
        if weekday is not 4:
            y = today - datetime.timedelta(7+weekday-4)
    if t == 'every friday':
        if weekday is not 5:
            y = today - datetime.timedelta(7+weekday-5)
    if t == 'every saturday':
        if weekday is not 6:
            y = today - datetime.timedelta(7+weekday-6)
    
    if t == 'every day':
        #See if the playlist has been scanned since yesterday
        y = today - datetime.timedelta(days=1)
        y = y.replace(hour=hour, minute=minute)
        
        if dev.timedelta_total_seconds(y-scansince) < 0:
            dev.log('The time of yesterday is already scanned, so we will send the date&time of today')
            y = today
    
    y = y.replace(hour=hour, minute=minute)
    dev.log(t+' ago is: '+str(y))
    
    

    if update_gmt is not None and update_gmt is not 99 and update_gmt is not 98:   
        y = y + datetime.timedelta(hours = update_gmt) #Offset the time according to the current system timezone and which timezone it should be updated to
        dev.log('with gmt offset ('+str(update_gmt)+'): '+str(y))

    return y


#Writes the nfo & strm files for all playlists
def update_playlists(type=''):
    #xbmcgui.Dialog().notification(vars.__addonname__, 'Updating Youtube '+dev.typeName(type)+' Playlists...', vars.__icon__, 3000)
    dev.log('Updating All '+type+' Youtube Playlists')
    #scan_interval = 'service_interval'
    #if type == 'musicvideo':
    #    scan_interval = 'service_interval_musicvideo'
    m_xml.xml_get(type=type)
    pl = m_xml.document.findall('playlists/playlist')
    if pl is not None: 
        for child in pl: #Loop through each playlist
            if child.attrib['enabled'] == 'yes': #Playlist has to be enabled
                dev.log('SERVICE: Checking if playlist '+child.find('title').text+' should be updated...')
                #Grab the settings from this playlist
                #Loads the correct information from the settings.xml
                #settings = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type)
                #Get the current GMT offset and consider this when updating
                import datetime      
                import time

                
                #Grab when this playlist should be updated
                updateat = '23:59'
                update_gmt = 99
                if child.find('updateevery') is None:
                    dev.log('NOTICE: Playlist should have an instruction when to be updated!. Asssumed default (12 hours) for now', 1)
                    updateevery = 'every 12 hours'
                else:
                    updateevery = child.find('updateevery').text
                    if child.find('updateat') is not None:
                        updateat = child.find('updateat').text
                        if child.find('update_gmt') is not None:
                            if child.find('update_gmt').text is not '':
                                update_gmt = dev.timezones(child.find('update_gmt').text)
                            
             
                
                
                
                #Check when this playlist was last updated, and if it is time for this playlist to be updated again
                
                try:
                    s = child.attrib['scansince']
                    scansince = datetime.datetime.strptime(s,"%d/%m/%Y %H:%M:%S")
                except:
                    scansince = datetime.datetime.now() - datetime.timedelta(days=3*365)
                timenow = datetime.datetime.now()
                dev.log('Playlist last scanned on: '+str(scansince)+', now: '+str(timenow), 1)
                if update_gmt is not None and update_gmt is not 99 and update_gmt is not 98: #If update_gmt is set to any other then the own timezone, consider this when calculating when the playlist should update
                    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
                    offset = offset / 60 / 60 * -1
                    timenow = timenow + datetime.timedelta(hours = offset)
                    scansince = scansince + datetime.timedelta(hours = offset)
                    dev.log('UCT timecorrection (because update_gmt is set): '+str(scansince)+', now: '+str(timenow), 1)
                #diff = (timenow-scansince).total_seconds()
                
                
                #diff = dev.timedelta_total_seconds(timenow-scansince)
                #dev.log('Difference from last scan is '+str(diff))
                
                #Get when this playlist should have last been updated
                should_update = updateevery_normal(updateevery, updateat, scansince, update_gmt)
                
                #dev.log('The difference between should_update & scansince: '+str(dev.timedelta_total_seconds(should_update-scansince)))
                if dev.timedelta_total_seconds(should_update-scansince) > 0:
                    #The last scan was earlier than when this playlist should have last been updated!
                    if dev.timedelta_total_seconds(timenow-should_update) > 0:
                        #The time for updating lies in the past, so update this playlist
                        dev.log('This playlist should be updated')
                        if xbmcaddon.Addon("plugin.video.youtubelibrary").getSetting('notify_update'):
                            xbmcgui.Dialog().notification(vars.__addonname__, 'Updating Playlist: '+child.find('title').text+'... ', vars.__icon__, 3000)
                    else:
                        dev.log('Its not time yet to update this playlist')
                        continue
                else:
                    dev.log('Last update was after the time this playlist should have been updated')
                    continue
                
                #WITH OLD SCAN INTERVAL:
                #if diff < (int(vars.__settings__.getSetting(scan_interval)) * 60 * 60):
                #    dev.log('Difference '+str(diff)+' was not enough, '+str(int(vars.__settings__.getSetting("service_interval")) * 60 * 60)+' seconds needed. This Playlist will not be updated now.')
                #    continue
                
            
                update_playlist(child.attrib['id'], type=type) #Update the nfo & strm files for this playlist
                if xbmcaddon.Addon("plugin.video.youtubelibrary").getSetting('notify_update'):
                    xbmcgui.Dialog().notification(vars.__addonname__, 'Done updating Playlist: '+child.find('title').text+'! ', vars.__icon__, 3000)
                
    #xbmcgui.Dialog().notification(vars.__addonname__, 'Done Updating Youtube '+dev.typeName(type)+' Playlists', vars.__icon__, 3000)
    #Should we also update the video library?
    if vars.update_videolibrary == "true" and type=='':
        update_dir = vars.tv_folder_path
        if type == 'musicvideo':
            update_dir = vars.musicvideo_folder_path
        elif type == 'movies':
            update_dir = vars.movies_folder_path
        dev.log('Updating video library is enabled. Updating '+type+' librarys directory %s' % update_dir, True)
        xbmc.executebuiltin('xbmc.updatelibrary(Video,'+update_dir+')')
        
#Writes the nfo & strm files for the given playlist
def update_playlist(id, type=''):
    settings = m_xml.xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type) #Grab the xml settings for this playlist
    if settings is None:
        dev.log('Could not find playlist '+id+' in the '+dev.typeXml(type)+' file', True)
        return False
    else:
        dev.log('Updating playlist %s (Id: %s)' % (settings.find('title').text.encode('utf-8'), id))
        #Check in which folder the show should be added
        folder = settings.find('overwritefolder').text
        if folder is None or folder == '':
            folder = dev.legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
        else:
            folder = dev.legal_filename(folder)
        
        #Create the tvshow.nfo
        writenfo = settings.find('writenfo').text
        if writenfo != 'no':
            if type == '' or type == 'tv':
                generators.write_tvshow_nfo(folder, settings)
            elif type == 'musicvideo':
                generators.write_artist_nfo(folder, settings)
        
        if update_playlist_vids(id, folder, settings, type=type) == False:
            return False #something failed while updating the videos of the playlist
        
        #Save the time this playlist got updated in the xml
        import datetime
        d=datetime.datetime.now()
        m_xml.xml_update_playlist_attr(id, 'scansince', d.strftime("%d/%m/%Y %H:%M:%S"), type=type)
    
        return True

#Updates the videos of a playlist
    #the id of the playlist
    #the folder where the strm & nfo files should go
    #the elementtree element containing the playlist xml settings
    #the id of the fist videoId, so it can save that one in the xml if it parsed all videos. Since the newest is the video it should be stopping the next time.
def update_playlist_vids(id, folder, settings, nextpage=False, firstvid = False, type=type):
    onlygrab = 100 #grab max 100 pages by default
    
    ##Get all Youtube Videos belonging to this playlist
    #resp = ytube.vids_by_playlist(id, nextpage) #Grab the videos belonging to this playlist
    #vids = resp.get("items", [])
    if settings.find('onlygrab') is not None:
        onlygrab = int(settings.find('onlygrab').text) / 50 #Get the maximum number of pages we should gather
    all_vids = []
    duration = {}
    #First we are going to collect all youtube videos until we come across a list containing a videoId we already got
    uptodate = False
    times = 0 #keep track how many times we grabbed yt videos
    reverse = '0'
    if settings.find('reverse') is not None:
        reverse = settings.find('reverse').text
        total_last_time = settings.find('lastvideoId').text
        if total_last_time == '' or total_last_time == None:
            total_last_time = '0'
        total_last_time = int(total_last_time)
            

    
    while uptodate == False:
        all_vidids = []
        
        resp = ytube.vids_by_playlist(id, nextpage) #Grab the videos belonging to this playlist
        if resp == False:
            return False #Something failed while retrieving the playlist
        amount = int(resp['pageInfo']['totalResults'])
        vids = resp.get("items", [])
        
        if reverse == '1' and times == 0:
            m_xml.xml_update_playlist_setting(id, 'lastvideoId', str(amount), type=type) #Update the amount of videos to the current one
            if total_last_time < amount: #There are more videos in the playlist now, so time to update
                dev.log('Reversed is enabled and there are more videos ('+str(amount)+' vs '+str(total_last_time)+') then last time.')
            else:
                dev.log('Reversed is enabled, but there are no more videos ('+str(amount)+' vs '+str(total_last_time)+') then last time.')
                return amount #No more videos then last time, so leave it at this
            if amount > 5000:
                dev.log('This playlist is way to big (more then 5000 videos) to be reversed')
                return amount
        
        if onlygrab <= times:
            #We have grabbed as many videos as allowed by the setting onlygrab
            uptodate = True
            break#quit updating the list
            
        
        for vid in vids:
            if m_xml.episode_exists(id, vid['contentDetails']['videoId'], type=type):
                if reverse != '1':
                    #This list contains a videoId we already got, assume we are up to date
                    uptodate = True
                continue #continue to the next video in the list
            
            if vid['snippet']['title'].lower() != 'private video' and vid['snippet']['title'].lower() != 'deleted video' and vid['snippet']['description'].lower() != 'this video is unavailable.':
                all_vidids.append(vid['contentDetails']['videoId']) #Collect all videoids in one list
                all_vids.append(vid) #Append this video to the all_vids list
            
        ##Grab the duration of the videos. We will need it for the minlength and maxlength filters, and for the duration tag in the .nfo file
        #We are gonna grab the duration of all 50 videos, saving on youtube api calls.
        dev.log('Grabbing duration of videos')
        duration.update(ytube.get_duration_vids(all_vidids)) #Get all the duration of the videos

        
        #If there is a nextPagetoken there are more videos to parse, call this function again so it can parse them to
        if 'nextPageToken' in resp:
            if uptodate is not True:
                nextpage = resp['nextPageToken']
        else:
            uptodate = True #Since there are no more pages, we are uptodate
            #update_playlist_vids(id, folder, settings, resp['nextPageToken'], firstvid)
        times = times+1
    
    dev.log('')
    dev.log('')
    dev.log('( ._.)~~~~~~~~~~ DONE GRABBING VIDS FROM YOUTUBE FOR :'+settings.find('title').text+' ~~~~~~~~~~(._. )')
    dev.log('')
    dev.log('')
    ##Grab settings from the settings.xml for this playlist
    minlength = settings.find('minlength').text
    maxlength = settings.find('maxlength').text
    if minlength is not '' and minlength is not None and minlength is not '00:00' and minlength is not '0:00':
        #Recalculate minlength
        dev.log('minlength is turned on: '+minlength)
        minlength = ytube.hms_to_sec(minlength)
        dev.log('minlength in seconds: '+str(minlength))
    else:
        minlength = None
    if maxlength is not '' and maxlength is not None and maxlength is not '00:00' and maxlength is not '0:00':
        #Recalculate maxlength
        dev.log('maxlength is turned on: '+maxlength)
        maxlength = ytube.hms_to_sec(maxlength)
        dev.log('maxlength in seconds: '+str(maxlength))
    else:
        maxlength = None    

    
    if reverse == '1':
        all_vids = list(reversed(all_vids))
    
    ##Loop through all vids and check with filters if we should add it
    for vid in reversed(all_vids): 
        dev.log('')
        #Check if we already had this video, if so we should skip it
        if m_xml.episode_exists(id, vid['contentDetails']['videoId'], type=type):
            dev.log('Episode '+vid['contentDetails']['videoId']+' is already scanned into the library')
            continue
        ##Check if the filters in the settings prevent this video from being added
        #Check if the word has been found, cause if not, we should not add this video to the library
        if onlyinclude(vid, settings) == False:
            continue #Skip this video
            #Check if the word has been found, cause if so, we should not add this video to the library
        if excludewords(vid, settings) == False:
            continue #Skip this video
        #See if this video is smaller or larger than the min-/maxlength specified in the settings
        if minlength is not None:
            if int(minlength) > int(duration[vid['contentDetails']['videoId']]):
                dev.log('Does not match minlength ('+str(minlength)+'): '+vid['snippet']['title']+' (id: '+vid['contentDetails']['videoId']+')')
                continue #Skip this video
            dev.log('Matches minlength: '+vid['snippet']['title']+' (id: '+vid['contentDetails']['videoId']+')')
        if maxlength is not None:
            if int(maxlength) < int(duration[vid['contentDetails']['videoId']]):
                dev.log('Does not match maxlength: '+vid['snippet']['title']+' (id: '+vid['contentDetails']['videoId']+')')
                continue #Skip this video
                
        #dev.log('TEST duration '+str(duration[vid['contentDetails']['videoId']]))
        
        downloadSuccess = True
        if type == '' or type == 'tv':
            #Grab the correct season and episode number from this vid
            season, episode, vid = generators.episode_season(vid, settings, resp['pageInfo']['totalResults'], id)
            filename = 's'+season+'e'+episode+' - '+vid['snippet']['title'] #Create the filename for the .strm & .nfo file
            
            if settings.find('download_videos') != None and settings.find('download_videos').text != 'off':
                downloadSuccess = play.downloadYoutubeVid(filename, folder, vid['contentDetails']['videoId'], settings, season=season) #Download the video for episode
                if downloadSuccess == False:
                    dev.log('Skip this video, since the download has failed')
                    continue #Skip this video, since it should have downloaded and failed
            else:
                generators.write_strm(filename, folder, vid['contentDetails']['videoId'], show=settings.find('title').text, episode=episode, season=season) #Write the strm file for this episode            
            
            if settings.find('writenfo').text != 'no':
                generators.write_nfo(filename, folder, vid, settings, season = season, episode = episode, duration = duration[vid['contentDetails']['videoId']]) #Write the nfo file for this episode
        ##Musicvideo
        elif type == 'musicvideo':
            #Grab the musicvideo information from the generator
            musicvideo_info = generators.get_songinfo(vid, settings, duration = duration[vid['contentDetails']['videoId']])
            if musicvideo_info == False:
                continue #Skip this video, it did not make it past the musicvideo filters
            
            filename = vid['snippet']['title'] #Create the filename for the .strm & .nfo file
            
            if settings.find('download_videos') != None and settings.find('download_videos').text != 'off':
                downloadSuccess = play.downloadYoutubeVid(filename, folder, vid['contentDetails']['videoId'], settings, type='musicvideo') #Download the video for episode
                if downloadSuccess == False:
                    dev.log('Skip this video, since the download has failed')
                    continue #Skip this video, since it should have downloaded and failed
            else:
                generators.write_strm(filename, folder, vid['contentDetails']['videoId'], artist=musicvideo_info['artist'], song=musicvideo_info['title'], album=musicvideo_info['album'], year=musicvideo_info['year'], type=type) #Write the strm file for this episode
            
            if settings.find('writenfo').text != 'no':
                generators.write_nfo(filename, folder, vid, settings, musicvideo=musicvideo_info, duration = duration[vid['contentDetails']['videoId']], type=type) #Write the nfo file for this episode
            season = musicvideo_info['album']
            if season == '':
                season = musicvideo_info['artist']
        ##Movies
        elif type == 'movies':
            #Prepare the title as best as we can for the imdb search and stuff
            #title = vid['snippet']['title']
            #description = vid['snippet']['description']
            #title = removetitle(title, settings.find('removetitle').text)
            #title = striptitle(title, settings.find('striptitle').text)
            
            #if settings.find('smart_search') == '2':
                #title, description = generators.smart_search(title, description, vid, settings)
            
            filename = vid['snippet']['title'] #Create the filename for the .strm & .nfo file
            
            if settings.find('writenfo').text != 'no':
                create_strm = generators.write_nfo(filename, folder, vid, settings, duration = duration[vid['contentDetails']['videoId']], type=type) #Write the nfo file for this episode
                if create_strm is False:
                    m_xml.playlist_add_episode(id, '1', vid['contentDetails']['videoId'], type=type) #Add it to the episode list, so it doesnt get picked up again
                    continue #Skip this video, it did not make it past the filters
            
            if settings.find('download_videos') != None and settings.find('download_videos').text != 'off':
                downloadSuccess = play.downloadYoutubeVid(filename, folder, vid['contentDetails']['videoId'], settings, type='movies') #Download the video for episode
                if downloadSuccess == False:
                    dev.log('Skip this video, since the download has failed')
                    continue #Skip this video, since it should have downloaded and failed
            else:
                generators.write_strm(filename, folder, vid['contentDetails']['videoId'], type=type) #Write the strm file for this episode
            
            season = '1'
            
            
        #Add this episode to the episodenr/playlist.xml file so we can remember we scanned this episode already
        m_xml.playlist_add_episode(id, season, vid['contentDetails']['videoId'], type=type)
        
    #If there is a nextPagetoken there are more videos to parse, call this function again so it can parse them to
    '''
    if 'nextPageToken' in resp and lastvid is not True:
        #update_playlist_vids(id, folder, settings, resp['nextPageToken'], firstvid)
    else:
        if firstvid != False:
            m_xml.xml_update_playlist_setting(id, 'lastvideoId', firstvid) #Set the lastvideoId to this videoId so the playlist remembers the last video it has. This will save on API calls, since it will quit when it comes across a video that already has been set
    '''
    dev.log('( ._.)========== Done ripping videos from playlist '+settings.find('title').text+' (ID: '+id+') ==========(._. )')
    dev.log('\n\n\n\n')
    return amount
    
##Helper Functions to check requirements of a youtube video according to the playlist settings
#Check onlyinclude
    #vid : The vid from the youtube response its about
    #settings: The element containing the playlist settings.xml
def onlyinclude(vid, settings):
    if settings.find('onlyinclude').text is not '' and settings.find('onlyinclude').text is not None:
        #Check if there are | ,if so we should loop through each onlyinclude word
        if '|' in settings.find('onlyinclude').text:
            strip = settings.find('onlyinclude').text.split('|')
        else:
            strip = []
            strip.append(settings.find('onlyinclude').text)
        for s in strip:
            if s in vid['snippet']['title']:
                return True #We found one of the words in the title, so this one is safe to add
        return False #If the code made it this far, it didnt find one of the required words
    else:
        return True #onlyinclude is not enabled, so return true
        
#Checks for excludewords, returns True if check passed, False if check fails
def excludewords(vid, settings):
    if settings.find('excludewords').text is not '' and settings.find('excludewords').text is not None:
        #Check if there are | ,if so we should loop through each onlyinclude word
        if '|' in settings.find('excludewords').text:
            strip = settings.find('excludewords').text.split('|')
        else:
            strip = []
            strip.append(settings.find('excludewords').text)
        for s in strip:
            if s.lower() in vid['snippet']['title'].lower() or s.lower() in vid['snippet']['description']:
                return False #We found one of the words in the title, so this one should not be added
        return True
    else:
        return True

