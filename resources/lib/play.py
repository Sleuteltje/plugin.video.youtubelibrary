# -*- coding: utf-8 -*-
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
from __future__ import division
from __future__ import unicode_literals

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcplugin, xbmcvfs
import sys
import os
import urllib

from resources.lib import vars
from resources.lib import dev
from resources.lib import bookmarks

import YDStreamExtractor
import YDStreamUtils

import youtube_dl


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        dev.log('Error while downloading: '+msg)


def my_hook(d):
    if d['status'] == 'finished':
        dev.log('Done downloading, now converting ...')


# Returns the filename (without .strm)
def downloadYoutubeVid(name, fold, videoid, settings, type='', season=None):
	#youtube-dl command to download best quality: -f bestvideo[ext!=webm]‌​+bestaudio[ext!=webm]‌​/best[ext!=webm]
	#YDStreamExtractor.disableDASHVideo(True)
	
	movieLibrary = vars.tv_folder #The path we should save in is the vars.tv_folder setting from the addon settings
	if type=='musicvideo':
		movieLibrary = vars.musicvideo_folder
	if type=='movies':
		movieLibrary = vars.movies_folder
	
	folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
	enc_name = dev.legal_filename(name) #Encode the filename to a legal filename
	
	xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exist yet
	xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet
    
	xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet
	if type == '' or type == 'tv':
		folder = os.path.join(folder, 'Season '+season) #Set the folder to the maindir/dir
		xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet

	full_file_path = os.path.join(folder, enc_name) #Set the file to maindir/name/name
	
	dev.log('Downloading '+videoid, 1)
	#vid = YDStreamExtractor.getVideoInfo(videoid,quality=1)
	path = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
	
	
	#url = "https://www.youtube.com/watch?v=YKSU82afy1w" #ducktales intro to test
	url = "https://www.youtube.com/watch?v="+videoid
	vid = YDStreamExtractor.getVideoInfo(url,quality=1)
	
	if vid == None:
		dev.log('Failed to retrieve video from url: '+url)
		return False
	
	if settings.find('download_videos').text  == '720p':
		dev.log('%%%%%%% QUALITY: 720p quality selected')
		format = 'bestvideo[height<=?720]+bestaudio/best[height<=?720]'
	elif settings.find('download_videos').text == '1080p':
		dev.log('%%%%%%% QUALITY: 1080p quality selected')
		format = 'bestvideo[height<=?1080]+bestaudio/best[height<=?1080]'
	else:
		dev.log('%%%%%%% QUALITY: best quality selected')
		format = 'bestvideo+bestaudio/best'
	
	ydl_opts = {
    'format': format,
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
	'outtmpl' : full_file_path+'.%(ext)s',
	#'-o' : enc_name+'.%(ext)s',
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		return ydl.download(['https://www.youtube.com/watch?v='+videoid])
	
	"""
	try:
		#YDStreamExtractor.setOutputCallback(prog)
		#result = YDStreamExtractor.downloadVideo(vid,folder)
		#result = YDStreamExtractor.handleDownload(vid, bg=True, path=folder)
		result = YDStreamExtractor.download(vid, folder, template=enc_name+'.%(ext)s')
		if result:
			#success
			#full_path_to_file = result.filepath
			dev.log('Success when downloading '+folder+enc_name, 1)
		elif result.status != 'canceled':
			#download failed
			error_message = result.message
	finally:
		#YDStreamExtractor.setOutputCallback(None)
		dev.log('Done downloading '+folder+enc_name, 1)
		
	try:
		dev.log('Done downloading '+result.filepath, 1)
		return True
	except:
		dev.log('Download failed for '+url)
		return False"""





##### PLAY VIDEO 
#Plays a youtube video by id
def playYoutubeVid(id, meta=None, poster=None):
    dev.log('poster: '+poster)
    #Poster URL that hickups the addon: image://C%3a%5cKodi%5cportable_data%5cuserdata%5caddon_data%5cplugin.video.youtubelibrary%5cStreams%5cTV%5cSleuteltje%20-%20Bios%20Intros%5cfolder.jpg/
    #poster = None
    if meta is None:
        #Create an empty meta, so we can fill it with the information grabbed from youtube
        meta = {}
    if poster is None:
        poster = 'Default.png'
    elif poster.startswith('image://'):
        poster = poster[8:-1]
        poster = urllib.unquote(urllib.unquote(poster))
        dev.log('poster cleaned: '+poster)
    
    
	#YDStreamExtractor.disableDASHVideo(True) #Kodi (XBMC) only plays the video for DASH streams, so you don't want these normally. Of course these are the only 1080p streams on YouTube
	
	try:
		#url = id #a youtube ID will work as well and of course you could pass the url of another site
		vid = YDStreamExtractor.getVideoInfo(id,quality=1) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
		stream_url = vid.streamURL() #This is what Kodi (XBMC) will play
	except:
		dev.log('Failed to get a valid stream_url!')
		return False #Failed to grab a video title
	
	if 'title' not in meta:
		meta['title'] = vid.title #Store the youtube title in the meta  
	
	
	#xbmc.Player().play(v.getbest().url) #Play this video
	liz = xbmcgui.ListItem(meta['title'], iconImage=poster, thumbnailImage=poster)
	liz.setInfo( type="Video", infoLabels=meta )
	liz.setPath(stream_url)
	return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
            

#Plays the requested Youtube Music Video
def playMusicVid(id, filename=None, artist = None, song = None):
    poster = 'Default.png'
    meta = {};
    meta['title'] = artist+' - '+song
    
    return playYoutubeVid(id, meta, poster)
            
#Plays the requested Youtube Video
def playVid(id, filename=None, season = None, episode = None, show = None, folder = None, type=''):    
    import time
    import json
    diff = 0
	
    #return playYoutubeVid(id)
    
    #Check if its PseudoTV that's playing this file, if so, we shouldn't do anything else than play the video
    if xbmcgui.Window(10000).getProperty('PseudoTVRunning') == 'True':
        dev.log('PseudoTV is running, so just play the video')
        return playYoutubeVid(id)


	if str(type(filename)) == "<type 'unicode'>":
		filename = filename.encode('utf-8')
    filename = filename.decode('utf-8') 
    
    #Prepare the information
    loadingTime = time.time()
    totalTime = 0 ; currentTime = 0
    folderPath = xbmc.getInfoLabel('Container.FolderPath')
    name = filename
    dev.log('filename:')
    dev.log(filename)
    filename = filename + '.strm'
    try:
        filename = filename.translate(None, '\/:*?"<>|').strip('.')
    except:
		filename = filename.translate('\/:*?"<>|').strip('.')
		
    #Grab the metadata of this episode
    if type == 'movies':
        #meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"field": "studio", "operator": "is", "value": "Youtube"}, "properties": ["title", "runtime", "rating", "director", "writer", "plot", "thumbnail", "file"]}, "id": 1}' % (filename))
        query = '{"jsonrpc": "2.0", "params": {"sort": {"order": "ascending", "method": "title"}, "filter": {"operator": "contains", "field": "path", "value": "%s"}, "properties": ["title", "art", "file", "thumbnail", "runtime", "rating", "plot"]}, "method": "VideoLibrary.GetMovies", "id": "libMovies"}' % (folder)
        dev.log('trying meta query now: '+query)
        meta = xbmc.executeJSONRPC(query)
    
    else:
        meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["title", "season", "episode", "showtitle", "firstaired", "runtime", "rating", "director", "writer", "plot", "thumbnail", "file"]}, "id": 1}' % (season, episode))
    meta = unicode(meta, 'utf-8', errors='ignore')
    dev.log('Meta: '+meta)
    if 'episodes' in json.loads(meta)['result'] or 'movies' in json.loads(meta)['result']:  
        if type == 'movies':
            meta = json.loads(meta)['result']['movies']
        else:
            meta = json.loads(meta)['result']['episodes']
        for i in meta:
            i['file'] = i['file'].encode('utf8')
            i['file'] = i['file'].decode('utf8')
            #dev.log('Meta: '+i['file'].encode('utf8'))
            dev.log('Meta: '+i['file'])
            dev.log('Looking for :'+filename)
            dev.log('File :'+i['file'])
            #i['file'] = i['file'].encode('utf-8')
            if i['file'].endswith(filename):
                dev.log('Found the episode we are looking for')
                meta = i
                break
                
        if type == 'movies':
            DBID = meta['movieid'] ; thumb = meta['thumbnail'] ;
            
            meta = {'title': meta['title'].encode('utf-8'), 'duration' : meta['runtime'], 'rating': meta['rating'], 'plot': meta['plot'].encode('utf-8')}
            poster = 'Default.png'
            #poster = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter": {"field": "title", "operator": "is", "value": "%s"}, "properties": ["thumbnail"]}, "id": 1}' % showtitle.encode('utf-8'))
            #poster = unicode(poster, 'utf-8', errors='ignore')
            #poster = json.loads(poster)['result']['tvshows'][0]['thumbnail']
        else:
            DBID = meta['episodeid'] ; thumb = meta['thumbnail'] ; showtitle = meta['showtitle']
            
            meta = {'title': meta['title'].encode('utf-8'), 'season' : meta['season'], 'episode': meta['episode'], 'tvshowtitle': meta['showtitle'].encode('utf-8'), 'premiered' : meta['firstaired'].encode('utf-8'), 'duration' : meta['runtime'], 'rating': meta['rating'], 'director': str(' / '.join(meta['director']).encode('utf-8')), 'writer': str(' / '.join(meta['writer']).encode('utf-8')), 'plot': meta['plot'].encode('utf-8')}

            poster = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter": {"field": "title", "operator": "is", "value": "%s"}, "properties": ["thumbnail"]}, "id": 1}' % showtitle.encode('utf-8'))
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
    
	if currentTime != 0 and totalTime != 0:
		diff = currentTime / totalTime #Calculate how much of the video has been watched
    #The video has stopped playing
    dev.log('Ended Video Playback (%s) @ %s (percentage: %s)' % (totalTime, currentTime, diff))
    
    #Delete the previous bookmark where we were and store the new one
    try:
        bookmarks.deleteBookmark(name) #Delete the previous saved bookmark
        dev.log('Deleted the previous bookmark')
        ok = int(currentTime) > 120 and (currentTime / totalTime) <= .9 #Has the video been playing long enough and is it viewed less then 90%?
        if ok:
            bookmarks.addBookmark(currentTime, name) #Add the new bookmark
            dev.log('Added new bookmark @ %s' % currentTime)
    except:
        pass
    
    #Mark the episode as watched if enough was watched
    ok = diff >= .9 #Did the episode get watched for 90% or more?
    if int(currentTime) < 120:
        ok = diff >= .75 #Since the runtime is very short, we'll accept a view through as 75%
    if ok:
        dev.log('Episode has been watched for %s, mark as watched' % diff)
        bookmarks.mark_as_watched(DBID, folderPath) #Mark the episode as watched
    else:
        dev.log('Episode has been watched for %s, dont mark as watched' % diff)
