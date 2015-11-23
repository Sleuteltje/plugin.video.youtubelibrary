#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions to play a youtube video
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
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcplugin
import sys

from resources.lib import vars
from resources.lib import dev
from resources.lib import bookmarks


##### PLAY VIDEO 
#Plays a youtube video by id
def playYoutubeVid(id, meta=None, poster=None):
    from resources.lib import pafy
    pafy.set_api_key(vars.API_KEY)
    #Resolve the youtube video url for ourselves
    v = pafy.new(id)
    if meta is None:
        #Create an empty meta, so we can fill it with the information grabbed from youtube
        meta = {}
    if 'title' not in meta:
        meta['title'] = v.title #Store the youtube title in the meta  
    if poster is None:
        poster = 'Default.png'
    
    
    #xbmc.Player().play(v.getbest().url) #Play this video
    liz = xbmcgui.ListItem(meta['title'], iconImage=poster, thumbnailImage=poster)
    liz.setInfo( type="Video", infoLabels=meta )
    liz.setPath(v.getbest().url)
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
            
#Plays the requested Youtube Video
def playVid(id, filename=None, season = None, episode = None, show = None):    
    import time
    import json
    
    #Check if its PseudoTV that's playing this file, if so, we shouldn't do anything else than play the video
    if xbmcgui.Window(10000).getProperty('PseudoTVRunning') == 'True':
        dev.log('PseudoTV is running, so just play the video')
        return playYoutubeVid(id)


    #Prepare the information
    loadingTime = time.time()
    totalTime = 0 ; currentTime = 0
    folderPath = xbmc.getInfoLabel('Container.FolderPath')
    name = filename
    filename = filename + '.strm'
    filename = filename.translate(None, '\/:*?"<>|').strip('.')

    #Grab the metadata of this episode
    meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["title", "season", "episode", "showtitle", "firstaired", "runtime", "rating", "director", "writer", "plot", "thumbnail", "file"]}, "id": 1}' % (season, episode))
    meta = unicode(meta, 'utf-8', errors='ignore')
    if 'episodes' in json.loads(meta)['result']:  
        meta = json.loads(meta)['result']['episodes']
        for i in meta:
            dev.log('Meta: '+i['file'].encode('utf8'))
            dev.log('Looking for :'+filename)
            if i['file'].endswith(filename):
                dev.log('Found the episode we are looking for')
                meta = i
                break
        DBID = meta['episodeid'] ; thumb = meta['thumbnail'] ; showtitle = meta['showtitle']

        meta = {'title': meta['title'], 'season' : meta['season'], 'episode': meta['episode'], 'tvshowtitle': meta['showtitle'], 'premiered' : meta['firstaired'], 'duration' : meta['runtime'], 'rating': meta['rating'], 'director': str(' / '.join(meta['director'])), 'writer': str(' / '.join(meta['writer'])), 'plot': meta['plot']}

        poster = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter": {"field": "title", "operator": "is", "value": "%s"}, "properties": ["thumbnail"]}, "id": 1}' % showtitle)
        poster = unicode(poster, 'utf-8', errors='ignore')
        poster = json.loads(poster)['result']['tvshows'][0]['thumbnail']

        #If resume playback is set in the settings, display a resume menu
        try:
            if xbmcaddon.Addon().getSetting('resume_playback') == 'true':
                dev.log('Resume Playback is turned on. Grab resume point..')
                offset = bookmarks.getBookmark(name)
                dev.log('Offset is %s' % offset)
                if offset == '0': raise Exception()
                dev.log('Grabbing minutes and seconds')
                minutes, seconds = divmod(float(offset), 60) ; hours, minutes = divmod(minutes, 60)
                dev.log('Showing yesno. Minutes: %s, seconds: %s' % (minutes, seconds))
                #yes = yesnoDialog('%s %02d:%02d:%02d' % ('Resume from ', hours, minutes, seconds), '', '', self.name, 'Resume', 'Start From Beginning')
                yes = xbmcgui.Dialog().yesno('Resume', '%s %02d:%02d:%02d' % ('Resume from ', hours, minutes, seconds), nolabel = 'Resume', yeslabel = 'Start From Beginning')
                dev.log('Chose option: %s' % yes)
                if yes: offset = '0'
        except:
            pass

    
        #Play the youtube video with the meta data just acquired
        playYoutubeVid(id, meta, poster)
    else:
        dev.log('Error: Could not retrieve meta information from the database!', True)
        return playYoutubeVid(id) #Just play the video, since we could not retrieve meta information

    
    
    #Check if the video is still playing and store the time it is currently playing
    for i in range(0, 300):
        if xbmc.Player().isPlayingVideo():
            #Set the offset of the video
            try:
                if offset == '0': raise Exception()
                xbmc.Player().seekTime(float(offset))
            except:
                pass
            break
        xbmc.sleep(100)
    while xbmc.Player().isPlayingVideo():
        try: totalTime = xbmc.Player().getTotalTime()
        except: pass
        try: currentTime = xbmc.Player().getTime()
        except: pass
        xbmc.sleep(1000)
    
    diff = currentTime / totalTime #Calculate how much of the video has been watced
    #The video has stopped playing
    dev.log('Ended Video Playback (%s) @ %s (percentage: %s)' % (totalTime, currentTime, diff))
    
    #Delete the previous bookmark where we were and store the new one
    try:
        bookmarks.deleteBookmark(name) #Delete the previous saved bookmark
        dev.log('Deleted the previous bookmark')
        ok = int(currentTime) > 60 and (currentTime / totalTime) <= .9 #Has the video been playing long enough and is it viewed less then 90%?
        if ok:
            bookmarks.addBookmark(currentTime, name) #Add the new bookmark
            dev.log('Added new bookmark @ %s' % currentTime)
    except:
        pass
    
    #Mark the episode as watched if enough was watched
    ok = diff >= .9 #Did the episode get watched for 90% or more?
    if ok:
        dev.log('Episode has been watched for %s, mark as watched' % diff)
        bookmarks.mark_as_watched(DBID, folderPath) #Mark the episode as watched
    else:
        dev.log('Episode has been watched for %s, dont mark as watched' % diff)
