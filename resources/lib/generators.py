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
            episode = str(episode + 1)
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



###### STRM GENERATOR ##############
#Creates a .strm file
# Name : The name of the strm file
# folder:   The name of the folder the strm file should be written in (Not the mainfolder, but the name of the show, so the strms get in that subdir)
# videoid:  The videoid of the youtube video we want to make a strm off
# show: The name of the show (needed for a .strm file to this addon)
# season: The season of this episode
# episode: The episode number of this episode
#
# Returns the filename (without .strm)
def write_strm(name, fold, videoid, show=None, season=None, episode=None):
    #dev.log('strm('+name+', '+fold+', '+videoid+')')
    movieLibrary = vars.tv_folder #The path we should save in is the vars.tv_folder setting from the addon settings
    sysname = urllib.quote_plus(videoid) #Escape strings in the videoid if needed
    enc_name = dev.legal_filename(name) #Encode the filename to a legal filename
    
    if vars.__settings__.getSetting("strm_link") == "Youtube Library":
        content = 'plugin://plugin.video.youtubelibrary/?mode=play&id=%s&show=%s&season=%s&episode=%s&filename=%s' % (sysname, show, season, episode, enc_name) #Set the content of the strm file with a link back to this addon for playing the video
    else:
        content = vars.KODI_ADDONLINK+'%s' % ( sysname) #Set the content of the strm file with a link to the official Kodi Youtube Addon

    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet

    stream = os.path.join(folder, enc_name + '.strm') #Set the file to maindir/name/name.strm
    file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    file.write(str(content)) #Write the content in the file
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
def write_nfo(name, fold, vid, settings, season, episode, duration='0'):
    #dev.log('write_nfo('+name+', '+fold+')')
    movieLibrary = vars.tv_folder #Use the directory from the addon settings

    snippet = vid['snippet']
    
    
    #See if we should do something to the title according to the settings
    title = snippet['title']
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
    with codecs.open(stream,'w',encoding='utf8') as f:
        f.write(content)
        f.close()
    #file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    #file.write(str(content)) #Write the content in the file
    #file.close() #Close the file
    dev.log('write_tvshow_nfo: Written tvshow.nfo file: '+fold+'/'+enc_name+'.nfo')
    
    #If the setting download_images is true, we should also download the images as actual files into the directory
    if vars.__settings__.getSetting("download_images") == "true":
        dev.log('download_images enabled, so downloading images to '+folder)
        urllib.urlretrieve(settings.find('thumb').text, folder+"/folder.jpg")
        urllib.urlretrieve(settings.find('banner').text, folder+"/banner.jpg")
        urllib.urlretrieve(settings.find('fanart').text, folder+"/fanart.jpg")
