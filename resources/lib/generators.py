# -*- coding: utf-8 -*-
#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions to write NFO & Strm files
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
import re
import xbmcvfs
import os
import urllib

from resources.lib import dev
from resources.lib import vars
from resources.lib import ytube

################## Generators ####################
#Does a regex expression from the settings.xml. Will return None if it fails, the match otherwise    
def reg(se, txt):
    if se[:6] == 'regex(':
        #match = re.match(se, 'regex\((.*)\)')
        ma = se[6:]
        ma = ma[:-1]
        if ma is not None:
            m = re.search( ma, txt)
            #m = re.search( r'(\d+)', txt)
            if m:
                #Found the thing we were looking for with the given user regex
                dev.log('Regex '+ma+' found its match: '+m.group(0).encode('UTF-8')+' , '+m.group(1).encode('UTF-8'))
                return m.group(1)
            else:
                #Regex not found, return None
                dev.log('Regex given by user has not found anything: '+ma+' on '+txt.encode('UTF-8'), True)
                return None #Return the fallback
        else:
            dev.log('Regex given by user in settings.xml is not valid!'+se, True)
            return None
    else:
        return None #This is not a regex setting
    
#Generates the season and episode number
    #Vid: The video response from the youtube api
    #settings: The elementtree element containing the playlist settings
    #totalresults = The total results of the playlist, so that the episode can be calculated if the episode recognisition is set to pos
    #playlist = the id of the playlist we are checking episode numbers for
def episode_season(vid, settings, totalresults = False, playlist = False):
    ep = settings.find('episode').text #Grab the episode settings from the xml
    se = settings.find('season').text
    #dev.log('episode_season('+playlist+','+se+','+ep+')')
    found = False
    
    ##See if there should be standard season/episode recognisition for the season
    if se == 's02e12':
        regex = "s(eason)?\s*(\d+)\s*ep?(isode)?\s*(\d+)"
        m = re.search( regex, vid['snippet']['title'])
        if m:
            #Found the sxxexx
            dev.log('s2e12 '+regex+' found its match: '+m.group(0).encode('UTF-8')+' , '+m.group(1).encode('UTF-8')+' , '+m.group(2).encode('UTF-8'))
            #Try to replace the s01e01 in the title
            vid['snippet']['title'] = re.sub(regex, '', vid['snippet']['title'], 1)
            return m.group(2), m.group(4), vid
            
        #Regex not found, return None
        dev.log('s02e12 recognizition has not found anything: '+regex+' on '+vid['snippet']['title'].encode('UTF-8'), True)
        return '0', '0', vid

    if se == '02x12':
        regex = "(\d+)\s?x\s?(\d+)"
        m = re.search( regex, vid['snippet']['title'])
        if m:
            #Found the sxxexx
            dev.log('2x12 '+regex+' found its match: '+m.group(0).encode('UTF-8')+' , '+m.group(1).encode('UTF-8')+' , '+m.group(2).encode('UTF-8'))
            #Try to replace the s01e01 in the title
            vid['snippet']['title'] = re.sub(regex, '', vid['snippet']['title'], 1)
            return m.group(1), m.group(2), vid
            
        #Regex not found, return None
        dev.log('02x12 recognizition has not found anything: '+regex+' on '+vid['snippet']['title'].encode('UTF-8'), True)
        return '0', '0', vid
    
    ##Normal recongizitions
    #See if there should be a regex search for the season
    if se[:6] == 'regex(':
        match = reg(se, vid['snippet']['title'])
        if match != None:
            season = match[0]
            found = True
    if found == False: #If the episode has not been found yet, either it is not regex, or regex failed
        if se == 'year': #We want to save the season of the video as the year it is published
            d = ytube.convert_published(vid['snippet']['publishedAt'])
            season = d['year']
        elif se.isdigit(): #If the season is set to a hardcoded number
            season = str(se)
        else:
            dev.log('Error: invalid season tag in settings.xml: '+se+', set season to 0', True)
            season = '0'
        
    found = False
    #See if there should be a regex search for the episode
    if ep[:6] == 'regex(':
        match = reg(ep, vid['snippet']['title'])
        if match != None:
            episode = match
            found = True
    
    if found == False:
        if ep == 'default':
            if playlist == False:
                dev.log('episode_season: Error: episode recognisition set to default, but no playlist id given')
                return [season, '0']
            #Get the current episode number from episodes.xml
            from resources.lib import m_xml
            episode = m_xml.number_of_episodes(playlist, season)
            if episode == None:
                episode = 0
            #dev.log('Default Eprec: '+str(episode))
            episode = str(episode + 1)
            #dev.log('Default Eprec after +1: '+episode)
        elif ep == 'monthday': #We want the episode to be the month number + day number
            d = ytube.convert_published(vid['snippet']['publishedAt'])
            episode = d['month']+d['day']
        elif ep == 'monthdayhour': #month number + day number + hour number
            d = ytube.convert_published(vid['snippet']['publishedAt'])
            episode = d['month']+d['day']+d['hour']
        elif ep == 'monthdayhourminute': #month + day + hour + minute numbers
            d = ytube.convert_published(vid['snippet']['publishedAt'])
            episode = d['month']+d['day']+d['hour']+d['minute']
        elif ep == 'pos': #The position in the playlist as episode number
            episode = str(int(totalresults) - int(vid['snippet']['position']))
        elif ep.isdigit(): #A hardcoded number as episode number
            episode = str(ep)
        else:
            dev.log('Invalid episode setting in settings.xml! '+ep)
            episode = '0'
            
    return season, episode, vid


    


##Music Videos - songinfo
#Finds the genre, artist, song, album, plot and year
def get_songinfo(vid, settings, duration):
    artist = False
    featured = False
    song = False
    album = False
    tracknr = ''
    year = False
    genre = False
    studio = ''
    plot = False
    tags = []
    
    vid_title = vid['snippet']['title']
    vid_description = vid['snippet']['description']
    vid_id = vid['contentDetails']['videoId']
    vid_kind = 'song'
    
    dev.log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    dev.log('get_songinfo('+vid_title+'['+vid_id+'])')
    
    setting_genre = settings.find('genre').text #Grab the episode settings from the xml
    setting_genre_fallback = settings.find('genre_fallback').text 
    setting_genre_hardcoded = settings.find('genre_hardcoded').text 
    
    setting_artist = settings.find('artist').text
    setting_artist_fallback = settings.find('artist_fallback').text 
    setting_artist_hardcoded = settings.find('artist_hardcoded').text 
    
    setting_song_fallback = settings.find('song_fallback').text 
    
    
    setting_album = settings.find('album').text 
    setting_album_fallback = settings.find('album_fallback').text 
    setting_album_hardcoded = settings.find('album_hardcoded').text 
    
    setting_plot = settings.find('plot').text 
    setting_plot_fallback = settings.find('plot_fallback').text 
    setting_plot_hardcoded = settings.find('plot_hardcoded').text 
    
    setting_year = settings.find('year').text 
    setting_year_fallback = settings.find('year_fallback').text 
    setting_year_hardcoded = settings.find('year_hardcoded').text 
    
    setting_skip_audio = settings.find('skip_audio').text
    setting_skip_lyrics = settings.find('skip_lyrics').text
    setting_skip_live = settings.find('skip_live').text
    setting_skip_albums = settings.find('skip_albums').text
    dev.log('loaded settings')
    vid_title = vid_title.strip(' \t\n\r')
    
        

    
    ##Strip complete album from the title
    new_title = strip_album(vid_title)
    dev.log('New title after strip_album: '+new_title)
    if new_title != vid_title:
        vid_kind = 'album'
    vid_title = new_title
    dev.log('Vid title after strip_album: '+vid_title)
    
    ##Guess what kind of video this is (song, live song, album or concert)
    if int(duration) < 600:
        vid_kind = 'song'
        #Song is shorter than 10 minutes, so it must be a song / live song
        '''
        if 'live' in vid_title.lower() or 'tour' in vid_title.lower():
            #It must be a live song
            vid_kind = 'live'
            tags.append('live')
        elif 'lyrics' in vid_title.lower():
            vid_kind = 'lyrics'
            tags.append('lyrics')
        elif 'audio' in vid_title.lower():
            vid_kind = 'audio'
            tags.append('audio')
        '''
    else:
        #Song is longer than 10 minutes, so it must be an album / concert
        vid_kind = 'album'
        if ' live ' in vid_title.lower() or ' live ' in vid_description.lower():
            vid_kind = 'concert'
            tags.append('concert')
        else:
            tags.append('album')

    
    dev.log('(o.o) - Video Kind: '+vid_kind)
        
    ##Remove stuff between () [] or - - (like quality indicators, official video and such) from the title
    vid_title = strip_quality(vid_title)
    dev.log('Vid title after stripping quality: '+vid_title)
    new_title = strip_lyrics(vid_title)
    if vid_title != new_title:
        dev.log('Tagged as Lyrics video')
        vid_kind = 'lyrics'
        tags.append('lyrics')
        new_title += ' (Lyrics Video)'
    vid_title = new_title
    dev.log('Vid title after stripping lyrics: '+vid_title)
    new_title = strip_live(vid_title)
    if vid_title != new_title:
        dev.log('Tagged as Live Video')
        vid_kind = 'live'
        tags.append('live')
        new_title += '(Live)'
    vid_title = new_title
    dev.log('Vid title after stripping live: '+vid_title)
    new_title = strip_audio(vid_title)
    if vid_title != new_title:
        dev.log('Tagged as Audio video: '+new_title)
        vid_kind = 'audio'
        tags.append('audio')
        new_title += '(Audio)'
    vid_title = new_title
    dev.log('Vid title after stripping audio: '+vid_title+' ('+new_title+')')
    if setting_skip_audio == 'true' and vid_kind == 'audio':
        dev.log('Skip_audio is on, and video '+vid_title+' is an audio video', 1)
        return False
    if setting_skip_lyrics == 'true' and vid_kind == 'lyrics':
        dev.log('Skip_lyrics is on, and video '+vid_title+' is a lyric video', 1)
        return False
    if setting_skip_albums == 'true' and vid_kind == 'album':
        dev.log('Skip_albums is on, and video '+vid_title+' is an album video', 1)
        return False
    if setting_skip_live == 'true':
        if vid_kind == 'live' or vid_kind == 'concert':
            dev.log('Skip_live is on, and video '+vid_title+' is a live or concert video', 1)
            return False
        

    ##Try to find a tracknr
    m = re.search("\(?\[?(\d{1,2})\s\)\]\s?\.", vid_title)
    if m:
        tracknr = m.group(1)
        vid_title = vid_title.replace(m.group(0), '')
        dev.log('Vid title after stripping tracknr '+tracknr+': '+vid_title)
        
    ##Determine feautered artists
    featured, vid_title = get_featured(vid_title)


    ##Determine the Year    
    year, vid_title = get_year(vid_title, vid_description, 'year', settings, vid)
    if year == False:
        year, vid_title = get_year(vid_title, vid_description, 'year_fallback', settings, vid)
        if year == False:
            #Year recognizition has failed / the fallback was do not add. So do not add this video
            dev.log('Year not found! Fallback was '+setting_year_fallback+' Video not added: '+vid_title+' ('+vid_id+')', 1)
            return False


    
    ##Try to determine the album from the title
    album, vid_title = get_album(vid_title, vid_description, 'album', settings, vid)
    if album == False:
        album, vid_title = get_album(vid_title, vid_description, 'album_fallback', settings, vid)
    
    
    ##Determine the artist & song
    #If the setting artist is hardcoded & the song recognisition is set to video title, we should leave it at that
    if setting_artist == 'hardcoded' and setting_song_fallback == 'video title' or setting_artist == 'hardcoded' and setting_song_fallback == 'video title (original)':
        dev.log('Artist is hardcoded and song is set to video title, leave it at that: '+setting_artist_hardcoded)
        artist = setting_artist_hardcoded
        song = vid_title
        featured = ''
    else:
        artist, song = get_artist_song(vid_title, vid_description, 'artist', settings, vid)
        if artist == False:
            artist = get_hardcoded('artist_fallback', settings, vid)
            if artist == False:
                dev.log('Artist not found! Fallback was '+setting_artist_fallback+', video: '+vid_title+' ('+vid_id+') not added')
                return False
        else:
            ft = get_multiple_artists(artist)
            if ft != False:
                artist = ft.pop(0) #Assume the first artist is the main artist
                featured = ft
        artist = strip_audio(artist) #Strip (audio) and such from the name
        artist = strip_live(artist) #Strip live and such from the artist
        artist = strip_lyrics(artist) #Strip lyrics and such from the artist
        if song == False:
            song = get_hardcoded('song_fallback', settings, vid)
            if song == False:
                dev.log('Song not found! Fallback was '+setting_song_fallback+', video: '+vid_title+' ('+vid_id+') not added')
                return False
    
    ##If the video kind is an album, the album is the song title
    if album == False:
        if vid_kind == 'album':
            album = song
        if album == False:
            dev.log('Album not found! Fallback was '+setting_album_fallback+', video: '+vid_title+' ('+vid_id+') not added')
            return False
    
    ##Determine the plot
    plot = get_plot(vid_description, 'plot', settings, vid)
    if plot == False:
        plot = get_plot(vid_description, 'plot_fallback', settings, vid)
        if plot == False:
            dev.log('Plot not found! Fallback was '+setting_plot_fallback+', video: '+vid_title+' ('+vid_id+') not added')
            return False
            
    ##Determine the genre
    genre = setting_genre_hardcoded
    
    if setting_song_fallback == 'video title (original)':
        song = vid['snippet']['title']
    
    vid_info = {
        'title': song,
        'artist': artist,
        'album': album,
        'genre': genre,
        #'runtime': ?,
        'plot': plot,
        'year': year,
        'track': tracknr,
        'tracknr': tracknr,
        'studio': studio,
        'tags': tags,
        'featured': featured,
    }
    
    return vid_info


#Strip unwanted text from the text
def strip_album(text):
    album = ['complete album', 'full album'] 
    text = strip_from_text(text, album)
    return remove_extra_spaces(text)
def strip_audio(text):
    audio = ['audio only', 'audio'] 
    text = strip_from_text(text, audio)
    return remove_extra_spaces(text)
def strip_lyrics(text):
    lyrics = ['Lyrics on screen', 'with lyrics', 'w/ lyrics', 'lyric video', 'lyrics video', 'lyrics', 'lyric'] 
    text = strip_from_text(text, lyrics)
    return remove_extra_spaces(text)
def strip_live(text):
    live = ['live'] 
    text = strip_from_text(text, live)
    return remove_extra_spaces(text)
def strip_artist(text):
    artists = ['the music group', 'the band', 'the group']
    text = strip_from_text(text, artists)
    return remove_extra_spaces(text)
def strip_quality(text):
    hooks = ['original video with subtitles', 'original video', 'Official Music Video', 'official video hd', 'Official Video','Videoclip', 'Video Clip', 'video', 'clip officiel', 'clip', 'official', 'officiel']
    text = strip_from_text(text, hooks)
    qualitys = ['hd 1080p', 'hd 720p', '1080p hd', '720p hd', '1080p quality', '720p quality', 'dvd quality', 'hd quality', 'high quality', '1080p', '720p', 'hd', 'hq']
    text = strip_from_text(text, qualitys)
    return remove_extra_spaces(text)
    
#Strips a list of words from the text, first checking ()[]-- and then -, and then just the word
#text: The text to replace in
#checks: List of words to replace in the text
def strip_from_text(text, checks):    
    for check in checks:
        #dev.log('Replacing '+check)
        #First check if for it between () or [] or - - 
        regex = re.compile("(\(|\[|-)\s*"+re.escape(check)+"\s*(\)|\]|-)", re.IGNORECASE)
        #dev.log('Regex: '+ regex.pattern )
        text = re.sub(regex, '', text)
        #Then check for them from the beginning of the string with a - behind it
        regex = re.compile("^\s*"+re.escape(check)+"\s*-\s*", re.IGNORECASE)
        text = re.sub(regex, '', text)
        #Then check for them with just in the text
        regex = re.compile(re.escape(check), re.IGNORECASE)
        text = re.sub(regex, '', text)
    return text

#Removes spaces that are to much from the text, also strips spaces, tabs, returns, newlines & quotes from both ends of text
def remove_extra_spaces(text):
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text.strip(' \t\n\r"\'')
        
    
def get_hardcoded(setting, settings, vid):
    if settings.find(setting).text == 'hardcoded':
        setting = setting.replace('_fallback', '')
        return dev.get_setting(setting+'_hardcoded', settings)
    if settings.find(setting).text == 'playlist channelname':
        return settings.find('channel').text
    if settings.find(setting).text == 'video channelname':
        return vid['snippet']['channelTitle']
    if settings.find(setting).text == 'published year':
        return ytube.convert_published(vid['snippet']['publishedAt'])['year']
    if settings.find(setting).text == 'playlist description':
        return settings.find('description').text
    if settings.find(setting).text == 'video description':
        return vid['snippet']['description']
    return False
    

def get_featured(text):
    text = strip_audio(text)
    text = strip_lyrics(text)
    text = strip_live(text)
    regex = "(ft|vs|featuring|with|w\/)\s*\.?\:?\s*([^-\n\r]+)"
    m = re.search(regex, text, re.IGNORECASE)
    if m:
        ft = get_multiple_artists(m.group(2))
        if ft == False:
            return [m.group(2)], text
        #Replace the found string in the text
        text = text.replace(m.group(0), '')
        return ft, text
    return False, text

def get_multiple_artists(text):
    text = strip_audio(text)
    text = strip_lyrics(text)
    text = strip_live(text)
    splits = [',', '&', 'and', '/']
    for spl in splits:
        #Found featuring artist in the text, see if it are more than one.
        if spl in text:
            #Split all artist up by the ,
            return text.split(spl)
    return False

    
def get_album(vid_title, vid_description, setting, settings, vid):
    album = get_hardcoded(setting, settings, vid)
    if album != False:
        #The album was hardcoded
        return album, vid_title
    
    if settings.find(setting).text == 'video title and description':
        #First try to get the album from the description.
        regex = '(the album|as featured on)\s*:?\s*"?([^-\.\n\r"]+)'
        m = re.search(regex, vid_description)
        if m:
            #Album found!
            return remove_extra_spaces(m.group(2)), vid_title
    
    return False, vid_title

def get_artist_song(vid_title, vid_description, setting, settings, vid):
    artist = get_hardcoded(setting, settings, vid)
    if artist != False:
        #The artist was hardcoded
        a, song = find_artist_song(vid_title, artist)
        if song == False:
            a, song = find_artist_song_description(vid_description)
        return artist, song
    
    if settings.find(setting).text == 'video title and description':
        #Try to grab the information
        #First try to get the artist and title from the video title. Like a normal title
        artist, song = find_artist_song(vid_title, dev.get_setting('artist_hardcoded', settings))
        if artist != False and song != False:
            #Succesfull
            return artist, song
        #Artist - song lookup failed, more drastic lookups are needed
        artist, song = find_artist_song_description(vid_description)
        if artist != False and song != False:
            #Succesfull
            return artist, song
    return False, False
def find_artist_song(text, hardcoded_artist):
    regex = "^([^-\n]+)(-|by|\|)\s*([^-:\n]+)$"
    m = re.search(regex, text, re.IGNORECASE)
    if m:
        dev.log('find_artist_song() Found Artist - Song: '+str(m.group(1).encode('UTF-8'))+' - '+str(m.group(3).encode('UTF-8')))
        artist = remove_extra_spaces(m.group(1))
        song = remove_extra_spaces(m.group(3))
        if m.group(2) == 'by' or artist.lower() == hardcoded_artist.lower():
            #Turn artist and song around
            artist = m.group(3)
            song = m.group(1)
        if '(' in artist and ')' not in artist or ')' in artist and '(' not in artist:
            return False, False
        return artist, song
    return False, False
def find_artist_song_description(text):
    regex = "([^\n\r]+)('s|')\s*(official)?\s*(music)?\s*video\s*for\s*([^\.\n\r]*)"
    m = re.search(regex, text, re.IGNORECASE)
    if m:
        dev.log('find_artist_song_description() 1st: Found Artist - Song: '+str(m.group(1)).encode('utf-8')+' - '+str(m.group(5)).encode('utf-8'))
        #found the artist and song
        artist = m.group(1)
        song = m.group(5)
        return artist, song
    regex = "(official)?\s*(music)?\s*video\s*for\s*(.*?)('|’)?s[^'\"‘]*('|\"|‘)(.*)('|\"|’)"
    m = re.search(regex, text, re.IGNORECASE)
    if m:
        dev.log('find_artist_song_desription() 5th: Found Artist - Song: '+str(m.group(3)).encode('utf-8')+' - '+str(m.group(6)).encode('utf-8'))
        #Found the artist and song
        return m.group(3), m.group(6)
    if m:
        dev.log('find_artist_song_description() 1st: Found Artist - Song: '+str(m.group(1)).encode('utf-8')+' - '+str(m.group(5)).encode('utf-8'))
        #found the artist and song
        artist = m.group(1)
        song = m.group(5)
        return artist, song
    regex = "(.*?)\s*(by|from|performing|\|)\s*(?:([^,\n\r-]*?)\s*(by|from|performing))?\s*([^,\.\n\r-]*)"
    #regex_complex = "(.*?)\s*(?:is a song)?\s*(-|by|from(?! their album)|performing|\|)\s*(?:([^,\n\r]*?)\s*(-|by|from(?! their album)|performing))?\s*([^,\.\n\r]*)"
    m = re.search(regex, text, re.IGNORECASE)
    if m:
        #found the artist and song
        if m.group(4) == 'performing':
            dev.log('find_artist_song_description() Found Artist - Song 2nd: '+str(m.group(3)).encode('utf-8')+' - '+str(m.group(5)).encode('utf-8'))
            artist = m.group(3)
            song = m.group(5)
            return artist, song
        artist = m.group(1)
        song = m.group(3)
        if song is None:
            regex = re.compile(re.escape("\s*(official\s*)?(music\s*)?video\s*for\s*"), re.IGNORECASE)
            artist = regex.sub('', artist) #Replace official music video for in the artist, since it could be left over
            song = m.group(5)
        if m.group(2) == 'by' or m.group(2) == 'from':
            dev.log('find_artist_song_description() Found Artist - Song 3th: '+str(song.encode('UTF-8'))+' - '+str(m.group(1).encode('UTF-8')))
            artist = song
            song = m.group(1)
            return artist, song
        dev.log('find_artist_song_description() Found Artist - Song 4th: '+str(artist.encode('utf-8'))+' - '+str(song.encode('utf-8')))
        dev.log('Description: '+text)
        return artist, song

    return False, False


def get_year(vid_title, vid_description, setting, settings, vid):
    year = get_hardcoded(setting, settings, vid)
    if year != False:
        return year, vid_title
    if settings.find(setting).text == 'video title and description':
        year, vid_title = find_year(vid_title)
        if year != False:
            return year, vid_title
            year, vid_description = find_year(vid_description)
            if year != False:
                return year, vid_title
        
    return False, vid_title
def find_year(text):
    regex = "(\(?()c(opyright)?\)?)?\s*(\d{4})"
    m = re.search(regex, text, re.IGNORECASE)
    if m:
        if len(m.group(4)) == 4:
            #Found a year!
            dev.log(u'Found a year!: '+m.group(4)+ ' Whole match: '+m.group(0))
            text = text.replace(m.group(0), '') #Remove the copyright / year notice from the title
            return m.group(4), text
    return False, text
    
def get_plot(vid_description, setting, settings, vid):
    plot = get_hardcoded(setting, settings, vid)
    if plot != False:
        return plot
    if settings.find(setting).text == 'lyrics in video description':
        regex = "lyrics\s*:?(?:\n|\r|\s)*((?:\n|\r|.)*)"
        m = re.search(regex, vid_description)
        if m:
            if len(m.group(1)) > 1:
                return m.group(1)
    return False


###### STRM GENERATOR ##############
#Creates a .strm file
# Name : The name of the strm file
# folder:   The name of the folder the strm file should be written in (Not the mainfolder, but the name of the show, so the strms get in that subdir)
# videoid:  The videoid of the youtube video we want to make a strm off
# startpoint: The startpoint of the video (for starters, if you want it to start at 10:00 minutes in the video)
# endpoint: The endpoint of the video (if you want to stop the video at 20:00 minutes)
#
# show: The name of the show (needed for a .strm file to this addon)
# season: The season of this episode
# episode: The episode number of this episode
#
# type: tv (''), musicvideo, music, movies
#
# artist: The artist
# song: The song
# album: The album
# year: The year
#
# Returns the filename (without .strm)
def write_strm(name, fold, videoid, show=None, season=None, episode=None, startpoint = None, endpoint = None, artist='', album='', song='', year='', type=''):
    #dev.log('strm('+name+', '+fold+', '+videoid+')')
    movieLibrary = vars.tv_folder #The path we should save in is the vars.tv_folder setting from the addon settings
    if type=='musicvideo':
        movieLibrary = vars.musicvideo_folder
    sysname = urllib.quote_plus(videoid) #Escape strings in the videoid if needed
    enc_name = dev.legal_filename(name) #Encode the filename to a legal filename
    
    if vars.__settings__.getSetting("strm_link") == "Youtube Library":
        if type == 'musicvideo':
            content = 'plugin://plugin.video.youtubelibrary/?mode=playmusicvideo'
            if startpoint != None:
                content += '&startpoint='+startpoint
            if endpoint != None:
                content += '&endpoint='+endpoint
            content += '&id=%s&artist=%s&song=%s&album=%s&year=%s&filename=%s' % (sysname, artist, song, album, year, enc_name) #Set the content of the strm file with a link back to this addon for playing the video 
        else:
            content = 'plugin://plugin.video.youtubelibrary/?mode=play&id=%s&show=%s&season=%s&episode=%s&filename=%s' % (sysname, show, season, episode, enc_name) #Set the content of the strm file with a link back to this addon for playing the video
    else:
        content = vars.KODI_ADDONLINK+'%s' % ( sysname) #Set the content of the strm file with a link to the official Kodi Youtube Addon

    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet
    if type == '' or type == 'tv':
        folder = os.path.join(folder, 'Season '+season) #Set the folder to the maindir/dir
        xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet

    stream = os.path.join(folder, enc_name + '.strm') #Set the file to maindir/name/name.strm
    file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    file.write(str(content.encode('UTF-8'))) #Write the content in the file
    file.close() #Close the file
    dev.log('write_strm: Written strm file: '+fold+'/'+enc_name+'.strm')
    return enc_name
        

        
###### NFO GENERATOR ##############
#Creates a .nfo file
# Name : The name of the nfo file
# folder:   The name of the folder the nfo file should be written in (Not the mainfolder, but the name of the show, so the nfo get in that subdir)
# vid: THe video youtube response we want to add
# settings:  The elementtree containing the settings from the playlist
# season: The season of the episode
#episode: The episode number
#duration: The duration of the video
#overwrite_title: If you want to use another title than the vid['snippet']['title']
#overwrite_description: Same as above, but for description
#type: tv (''), musicvideo, music, movies
def write_nfo(name, fold, vid, settings, season='', episode='', duration='0', overwrite_title=None, overwrite_description=None, musicvideo=None, type=''):
    #dev.log('write_nfo('+name+', '+fold+')')
    movieLibrary = vars.tv_folder #Use the directory from the addon settings
    if type=='musicvideo':
        movieLibrary = vars.musicvideo_folder
    snippet = vid['snippet']
    
    
    #See if we should do something to the title according to the settings
    title = snippet['title']
    if overwrite_title != None:
        title = overwrite_title
    removetitle = settings.find('removetitle').text
    if removetitle == None:
        removetitle = ''
    if len(removetitle) > 0:
        #See if there are multiple lines
        if '|' in removetitle:
            strip = removetitle.split('|')
            for s in strip:
                #Check if we should do regex
                r = reg(s, title)
                if r is not None:
                    s = r
                if s in title:
                    title = title.replace(s, '') #Remove this line from the title
        else:
            #Check if this is a regex var of what should be removed
            rem = reg(removetitle, title)
            if rem is not None:
                removetitle = rem #Regex was succesfull, set removetitle to the found string so it can be removed as normal
            title = re.sub(removetitle, '', title, flags=re.IGNORECASE)
            #if removetitle in title:
                #title = title.replace(removetitle, '')
    #See if we should do something to the title according to the settings
    striptitle = settings.find('striptitle').text
    if striptitle == None:
        striptitle = ''
    if len(striptitle) > 0:
        #See if there are multiple lines
        if '|' in striptitle:
            strip = striptitle.split('|')
            for s in strip:
                if s in title:
                    title = title[:title.index(s)] #Strip everything to the point where the line was found
        else:
            #Check if this is a regex var of what should be removed
            rem = reg(title, striptitle)
            if rem is not None:
                striptitle = rem #Regex was succesfull, set striptitle to the found string so it can be stripped as normal
            if striptitle in title:
                title = title[:title.index(striptitle)] #Strip everything to the point where the line was found
                
                
    #See if we should do something to the description according to the settings
    description = snippet['description']
    if overwrite_description != None:
        description = overwrite_description
    removedescription = settings.find('removedescription').text
    if removedescription == None:
        removedescription = ''
    if len(removedescription) > 0:
        #See if there are multiple lines
        if '|' in removedescription:
            strip = removedescription.split('|')
            for s in strip:
                if s in description:
                    description = description.replace(s, '') #Remove this line from the description
        else:
            #Check if this is a regex var of what should be removed
            rem = reg(description, removedescription)
            if rem is not None:
                removedescription = rem #Regex was succesfull, set removedescription to the found string so it can be removed as normal
            if removedescription in description:
                description = description.replace(removedescription, '')
    #See if we should do something to the description according to the settings
    stripdescription = settings.find('stripdescription').text
    if stripdescription == None:
        stripdescription = ''
    if len(stripdescription) > 0:
        #See if there are multiple lines
        if '|' in stripdescription:
            strip = stripdescription.split('|')
            for s in strip:
                if s in description:
                    description = description[:description.index(s)] #Strip everything to the point where the line was found
        else:
            #Check if this is a regex var of what should be removed
            rem = reg(description, stripdescription)
            if rem is not None:
                stripdescription = rem #Regex was succesfull, set stripdescription to the found string so it can be stripped as normal
            if stripdescription in description:
                description = description[:description.index(stripdescription)] #Strip everything to the point where the line was found
   
   
    #Grab the best possible thumbnail
    #if 'maxres' in snippet['thumbnails']:
    #    thumbnail = snippet['thumbnails']['maxres']
    if 'standard' in snippet['thumbnails']:
        thumbnail = snippet['thumbnails']['standard']['url']
    elif 'high' in snippet['thumbnails']:
        thumbnail = snippet['thumbnails']['high']['url']
    elif 'medium' in snippet['thumbnails']:
        thumbnail = snippet['thumbnails']['medium']['url']
    elif 'default' in snippet['thumbnails']:
        thumbnail = snippet['thumbnails']['default']['url']
    else:
        thumbnail = settings.find('thumbnail').text
    
    #Grab the published date and convert it to a normal date
    d = ytube.convert_published(snippet['publishedAt'])
    normaldate = d['year']+'/'+d['month']+'/'+d['day']
    
    #Convert the duration (seconds) in number of minutes
    durationminutes = int(int(duration) / 60)
    
    durationhms = dev.convert_sec_to_hms(duration)
    
    if type == 'musicvideo':
        if musicvideo == None:
            return False
        #Grab the featured artists and convert them to xml
        featured_xml = ''
        if musicvideo['featured'] != False:
            for artist in musicvideo['featured']:
                featured_xml += '<artist>'+artist.strip(' \t\n\r')+'</artist>'
        #Grab the tags and convert them to xml
        tags_xml = ''
        if musicvideo['tags'] != False:
            for tag in musicvideo['tags']:
                tags_xml += '<tag>'+tag.strip(' \t\n\r')+'</tag>'
        tags = settings.find('tags')
        if tags is not None:
            tags = settings.find('tags').text
            if '/' in tags:
                multi_tags = tags.split('/')
                for tag in multi_tags:
                    tags_xml += '<tag>'+tag.strip(' \t\n\r')+'</tag>'
            elif tags.strip(' \t\n\r') is not '':
                tags_xml += '<tag>'+tags.strip(' \t\n\r')+'</tag>'
        
        genre = musicvideo['genre']
        if genre is None:
            genre = ''
        #Create the contents of the xml file
        content = """
<musicvideo>
    <title>%(title)s</title>
    <artist>%(artist)s</artist>
    %(featured)s
    <album>%(album)s</album>
    <genre>%(genre)s</genre>
    <runtime>%(durationminutes)s</runtime>
    <plot>%(plot)s</plot>
    <year>%(year)s</year>
    <director></director>
    <studio>%(studio)s</studio>
    <track>%(tracknr)s</track>
    <thumb>%(thumb)s</thumb>
    <fanart>
        <thumb>%(fanart)s</thumb>
    </fanart>
    <fileinfo>
        <streamdetails>
            <durationinseconds>%(duration)s</durationinseconds>
        </streamdetails>
    </fileinfo>
    %(tags)s
</musicvideo>
        """ % {
            'title': musicvideo['title'].strip(' \t\n\r'),
            'artist': musicvideo['artist'].strip(' \t\n\r'),
            'featured': featured_xml,
            'album': musicvideo['album'].strip(' \t\n\r'),
            'genre': genre.strip(' \t\n\r'),
            'plot': musicvideo['plot'].strip(' \t\n\r'),
            'year': musicvideo['year'].strip(' \t\n\r'),
            'studio': musicvideo['studio'].strip(' \t\n\r'),
            'thumb': thumbnail,
            'durationhms': durationhms,
            'tracknr': musicvideo['tracknr'].strip(' \t\n\r'),
            'fanart': settings.find('fanart').text,
            'tags': tags_xml,
            'durationminutes': durationminutes,
            'duration': duration
        }
    else:
        ##TV
        #Create the contents of the xml file
        content = """
<episodedetails>
    <title>%(title)s</title>
    <season>%(season)s</season>
    <episode>%(episode)s</episode>
    <plot>%(plot)s</plot>
    <thumb>%(thumb)s</thumb>
    <credits>%(channel)s</credits>
    <director>%(channel)s</director>
    <aired>%(date)s</aired>
    <premiered>%(date)s</premiered>
    <studio>Youtube</studio>
    <runtime>%(durationminutes)s</runtime>
    <fileinfo>
        <streamdetails>
            <durationinseconds>%(duration)s</durationinseconds>
        </streamdetails>
    </fileinfo>
</episodedetails>
        """ % {
            'title': title.strip(' \t\n\r'),
            'plot': description.strip(' \t\n\r'),
            'channel': settings.find('channel').text,
            'thumb': thumbnail,
            'date': normaldate,
            'season': season,
            'episode': episode,
            'durationminutes': durationminutes,
            'duration': duration
        }
    
    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    

    #enc_name = name.translate('\/:*?"<>|').strip('.') #Escape special characters in the name
    enc_name = dev.legal_filename(name)
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet
    if type == '' or type == 'tv':
        folder = os.path.join(folder, 'Season '+season) #Set the folder to the maindir/dir
        xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet

    stream = os.path.join(folder, enc_name + '.nfo') #Set the file to maindir/name/name.strm
    file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    file.write(str(content.encode("utf-8"))) #Write the content in the file
    file.close() #Close the file
    dev.log('write_nfo: Written nfo file: '+fold+'/'+enc_name+'.nfo')

        
        
        
#Writes the NFO for the tvshow
    #fold: The folder the nfo should be written to
    #settings: The elementtree element containing the playlist xml settings
def write_tvshow_nfo(fold, settings):
    dev.log('write_tvshow_nfo('+fold+')')
    name = 'tvshow'
    movieLibrary = vars.tv_folder #Use the directory from the addon settings

    #Grab the published date and convert it to a normal date
    d = ytube.convert_published(settings.find('published').text)
    normaldate = d['year']+'-'+d['month']+'-'+d['day']
    
    #Grab the tags and convert them to xml
    tags = settings.find('tags')
    tags_xml = ''
    if tags is not None:
        tags = settings.find('tags').text
        if '/' in tags:
            multi_tags = tags.split('/')
            tags_xml = ''
            for tag in multi_tags:
                tags_xml += '<tag>'+tag.strip(' \t\n\r')+'</tag>'
        elif tags.strip(' \t\n\r') is not '':
            tags_xml = '<tag>'+tags.strip(' \t\n\r')+'</tag>'
    
    #Create the contents of the xml file
    content = u"""
            <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
            <tvshow>
                <title>%(title)s</title>
                <showtitle>%(title)s</showtitle>
                <year>%(year)s</year>
                <plot>%(plot)s</plot>
                <genre>%(genre)s</genre>
                <premiered>%(date)s</premiered>
                <aired>%(date)s</aired>
                <studio>%(studio)s</studio>
                <thumb>%(thumb)s</thumb>
                <thumb aspect="poster">%(thumb)s</thumb>
                <thumb aspect="banner">%(banner)s</thumb>
                <fanart>
                    <thumb>%(fanart)s</thumb>
                </fanart>
                %(tags)s
            </tvshow>
    """ % {
        'title': settings.find('title').text,
        'plot': settings.find('description').text,
        'year': d['year'],
        'genre': settings.find('genre').text,
        'studio': settings.find('channel').text,
        'thumb': settings.find('thumb').text,
        'banner': settings.find('banner').text,
        'fanart': settings.find('fanart').text,
        'date': normaldate,
        'tags': tags_xml,
    }
    
    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    enc_name = dev.legal_filename(name) #Set the filename to a legal filename
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet
    stream = os.path.join(folder, enc_name + '.nfo') #Set the file to maindir/name/name.strm
    
    import codecs
    # process Unicode text
    #with codecs.open(stream,'w',encoding='utf8') as f:
    #    f.write(content)
    #    f.close()
    file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    file.write(str(content.encode("utf-8"))) #Write the content in the file
    file.close() #Close the file
    dev.log('write_tvshow_nfo: Written tvshow.nfo file: '+fold+'/'+enc_name+'.nfo')
    
    #If the setting download_images is true, we should also download the images as actual files into the directory
    if vars.__settings__.getSetting("download_images") == "true":
        extrafanart = os.path.join(folder, 'extrafanart') #Set to extrafanart
        xbmcvfs.mkdir(extrafanart) #Create this subfolder if it does not exist yet
        
        dev.log('download_images enabled, so downloading images to '+folder)
        download_img(settings.find('thumb').text, folder+"/folder.jpg")
        download_img(settings.find('banner').text, folder+"/banner.jpg")
        download_img(settings.find('fanart').text, folder+"/fanart.jpg")
        download_img(settings.find('fanart').text, extrafanart+"/fanart.jpg")

        
#Writes the NFO for the artist
    #fold: The folder the nfo should be written to
    #settings: The elementtree element containing the playlist xml settings
def write_artist_nfo(fold, settings):
    dev.log('write_artist_nfo('+fold+')')
    name = 'artist'
    movieLibrary = vars.musicvideo_folder #Use the directory from the addon settings

    #Grab the published date and convert it to a normal date
    d = ytube.convert_published(settings.find('published').text)
    normaldate = d['year']+'-'+d['month']+'-'+d['day']
    
    #Grab the tags and convert them to xml
    tags = settings.find('tags')
    tags_xml = ''
    if tags is not None:
        tags = settings.find('tags').text
        if '/' in tags:
            multi_tags = tags.split('/')
            tags_xml = ''
            for tag in multi_tags:
                tags_xml += '<tag>'+tag.strip(' \t\n\r')+'</tag>'
        elif tags.strip(' \t\n\r') is not '':
            tags_xml = '<tag>'+tags.strip(' \t\n\r')+'</tag>'
    
    #Create the contents of the xml file
    content = u"""
        <artist>
          <name>%(title)s</name>
          <genre clear=true>%(genre)s</genre>
          <formed>%(date)s</formed>
          <thumb>%(thumb)s</thumb>
          <thumb aspect="poster">%(thumb)s</thumb>
          <thumb aspect="banner">%(banner)s</thumb>
          <fanart>
              <thumb>%(fanart)s</thumb>
          </fanart>    
          %(tags)s
        </artist>
    """ % {
        'title': settings.find('title').text,
        'genre': settings.find('genre').text,
        'thumb': settings.find('thumb').text,
        'banner': settings.find('banner').text,
        'fanart': settings.find('fanart').text,
        'date': normaldate,
        'tags': tags_xml,
    }
    
    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    enc_name = dev.legal_filename(name) #Set the filename to a legal filename
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet
    stream = os.path.join(folder, enc_name + '.nfo') #Set the file to maindir/name/name.strm
    
    import codecs
    # process Unicode text
    #with codecs.open(stream,'w',encoding='utf8') as f:
    #    f.write(content)
    #    f.close()
    file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    file.write(str(content.encode("utf-8"))) #Write the content in the file
    file.close() #Close the file
    dev.log('write_tvshow_nfo: Written artist.nfo file: '+fold+'/'+enc_name+'.nfo')
    
    #If the setting download_images is true, we should also download the images as actual files into the directory
    if vars.__settings__.getSetting("download_images") == "true":
        extrafanart = os.path.join(folder, 'extrafanart') #Set to extrafanart
        xbmcvfs.mkdir(extrafanart) #Create this subfolder if it does not exist yet
        
        dev.log('download_images enabled, so downloading images to '+folder)
        download_img(settings.find('thumb').text, folder+"/folder.jpg")
        download_img(settings.find('banner').text, folder+"/banner.jpg")
        download_img(settings.find('fanart').text, folder+"/fanart.jpg")
        download_img(settings.find('fanart').text, extrafanart+"/fanart.jpg")


def download_img(thumbUrl, filename, overwrite=False): 
    #import codecs
    #import zipfile
    #import time
    
    #import fnmatch   
    #import util, helper
    #from util import * 
    import urllib2
    import xbmcgui
    import os.path
    if os.path.isfile(filename) and overwrite is False:
        return False
    
    # fetch thumbnail and save to filepath
    try:					
        target = filename
        if(filename.startswith('smb://')):
            #download file to local folder and copy it to smb path with xbmcvfs
            target = os.path.join(os.path.getTempDir(), os.path.basename(filename))
                                
        req = urllib2.Request(thumbUrl)
        req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')
        f = open(target,'wb')
        f.write(urllib2.urlopen(req).read())
        f.close()
            
        if(filename.startswith('smb://')):	
            xbmcvfs.copy(target, filename)
            xbmcvfs.delete(target)
            
    except Exception, (exc):
        xbmcgui.Dialog().ok('ERROR', 'Could not create image!')
        dev.log("ERROR: Could not create file: '%s'. Error message: '%s'" %(str(filename), str(exc)))
        
"""def download_img(url, filename, overwrite=False):
    import os.path
    if os.path.isfile(filename) and overwrite is False:
        return False
    try:
        urllib.urlretrieve(url, filename)
    except IOError:
        #Replace the https with http
        try:
            urllib.urlretrieve(url.replace('https://', 'http://'), filename)
        except:
            dev.log('Could not download: '+url, 1)
    return True
    """        
        