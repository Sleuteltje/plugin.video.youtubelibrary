# -*- coding: utf-8 -*-
#    Kodi Addon: Youtube Library
#    Copyright 2015-2017 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Some functions that will ease up basic kodi functions
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
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import urllib2
import os
from resources.lib import vars


#Log function
#   Params
#       Message:  The message to display in the log
#       Debug: Also display this message if debugmode is off?
def log(message, debug=None):
    if str(type(message)) == "<type 'unicode'>":
        message = message.encode('utf-8')
    if debug is not None:
        xbmc.log(vars.LPREF+message)
    else:
        if vars.__settings__.getSetting("debugmode") == 'true':
            xbmc.log(vars.LPREF+message)

#Returns a legal filename (without characters the OS wont accept)
def legal_filename(filename):
    import re
    #return re.sub('[^\w\-_\. ]', '_', filename)
    #return slugify(filename) #Use the slugify function to get a valid filename (with utf8 characters)
    return re.sub(r'[/\\:*?"<>|&]', '', filename)
    
#Construct a url to this plugin
# Params:
#    query: A dict with urls that will be transcoded to a plugin url 
#    Example:
#       {'mode' : 'folder', 'foldername' : 'channels'}
def build_url(query):
    return vars.base_url + '?' + urllib.urlencode(query)

#Add Directory to Kodi
#Params:
#   name: The name of the directory
#   url     : The url the directory should point to
#   thumb: The link to the thumbnail image
#   fanart: The fanart to display
#   description: The description of the directory
#   context: List containing the contextmenu items
def adddir(name, url, thumb='DefaultFolder.png', fanart = None, description = '', context = False):
    li = xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage = thumb)
    #Set type to video and give a description and such
    li.setInfo( type="Video", infoLabels={ "Title": name,"Plot":description} )
    if fanart is None:
        fanart = vars.__fanart__
    li.setProperty('fanart_image', fanart)
    if context != False:
        li.addContextMenuItems( context )
    xbmcplugin.addDirectoryItem(handle=vars.addon_handle, url=url,
                                listitem=li, isFolder=True)
                                
#Add Item to Kodi
#Params:
#   name: The name of the menu item
#   url     : The url the menuitem should point to
#   thumb: The link to the thumbnail image
def additem(name, url, thumb='DefaultVideo.png', fanart = None):
    li = xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage = thumb)
    if fanart is not None:
        li.setProperty('fanart_image',fanart)
    xbmcplugin.addDirectoryItem(handle=vars.addon_handle, url=url, listitem=li)
    
#Build the thumbnail url from the resources/media dir
def media(img):
    log('grabbing media file: '+img)
    return os.path.join(vars.IMG_DIR, img+".png")

#Asks the user for input
# Parameter :                                           #
#                                                       #
# name        sugested name for export                  #
#                                                       # 
# Returns   :                                           #
#                                                       #
# name        name of export excluding any extension    #
#                                                       #
def user_input(name, title='Enter input'):
    kb = xbmc.Keyboard('default', 'heading')
    kb.setDefault(name) # optional
    kb.setHeading(title) # optional
    #kb.setHiddenInput(True) # optional
    kb.doModal()
    if (kb.isConfirmed()):
        text = kb.getText()
    return(text)

#Displays a yes/no dialog    
def yesnoDialog(line1, line2, line3, heading=xbmcaddon.Addon().getAddonInfo('name'), nolabel='', yeslabel=''):
    return xbmcgui.Dialog().yesno(heading, line1, line2, line3, nolabel, yeslabel)
    
#Returns a string from strings.xml
def lang(id):
    return xbmcaddon.Addon().getLocalizedString(id)
    
#Replacement for .total_seconds() for python 2.6
def timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

#Converts secs to hms
def convert_sec_to_hms(seconds):
    import time
    time.strftime('%H:%M:%S', time.gmtime(int(seconds)))
        
#Grab an Addon Setting
def getAddonSetting(setting, default='niks'):
    val = xbmcaddon.Addon("plugin.video.youtubelibrary").getSetting(setting)
    if default != 'niks':
        if val is None or val is '':
            val = default
    return val
    
#Converts type link to a nice naming
def typeName(type):
    type_name = ''
    if(type == ''):
        type_name = 'TV Shows'
    elif(type == 'musicvideo'):
        type_name = 'Music Videos'
    elif(type == 'music'):
        type_name = 'Music'
    elif(type == 'movies'):
        type_name = 'Movies'
    return type_name
    
#Converts type to its settings.xml
def typeXml(type):
    if(type == 'musicvideo'):
        return 'settings_musicvideo.xml'
    elif(type == 'music'):
        return 'settings_music.xml'
    elif(type == 'movies'):
        return 'settings_movies.xml'
    else:
        return 'settings.xml'
        
#Converts the type to the epnr directory
def typeEpnr(type):
    if type == 'musicvideo':
        return 'musicvideo'
    elif type == 'music':
        return 'music'
    elif type == 'movies':
        return 'movies'
    else:
        return 'episodenr'
        
#Gets the setting from the xml safely
def get_setting(setting, settings):
    setting = settings.find(setting).text
    if setting is None:
        setting = ''
    return setting
	
	
	
#Slugifies a string (thus also making it a valid filename) (borrowed from Django framework, All credits to Django)
def slugify(value):
    import re
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
    
    
#Arrays containing all timezons as string or as integers as hours
def timezones(convert = False):
    timezones = [
        'Default',
        'Systems Timezone',
        'GMT (UTC)',
        'GMT+1:00',
        'GMT+2:00',
        'GMT+3:00',
        'GMT+3:30',
        'GMT+4:00',
        'GMT+5:00',
        'GMT+5:30',
        'GMT+6:00',
        'GMT+7:00',
        'GMT+8:00',
        'GMT+9:00',
        'GMT+9:30',
        'GMT+10:00',
        'GMT+11:00',
        'GMT+12:00',
        'GMT-11:00',
        'GMT-10:00',
        'GMT-9:00',
        'GMT-8:00',
        'GMT-7:00',
        'GMT-6:00',
        'GMT-5:00',
        'GMT-4:00',
        'GMT-3:30',
        'GMT-3:00',
        'GMT-2:00',
        'GMT-1:00'
    ]    
    timezones_as_numbers = [
        98,
        99,
        0,
        1,
        2,
        3,
        3.5,
        4,
        5,
        5.3,
        6,
        7,
        8,
        9,
        9.5,
        10,
        11,
        12,
        -11,
        -10,
        -9,
        -8,
        -7,
        -6,
        -5,
        -4,
        -3.5,
        -3,
        -2,
        -1
    ]
    
    if convert == False:
        return timezones
    return timezones_as_numbers[timezones.index(convert)]
    
#Puts a string to maximum length
def cap(s, l):
    return s if len(s)<=l else s[0:l-3]+'...'
	
	


	
#Grabs the highest possible thumbnail, and if not found will try to fail gracefully
#    default – playlist item or search result – is 120px wide and 90px tall. The default thumbnail for a channel is 88px wide and 88px tall.
#    medium – 320px wide and 180px tall. For a channel, this image is 240px wide and 240px tall.
#    high – 480px wide and 360px tall. For a channel, this image is 800px wide and 800px tall.
#    standard – 640px wide and 480px tall.
#   maxres – The highest resolution version of the thumbnail image. 1280px wide and 720px tall.
def playlist_highest_thumbnail(playlist):
	pl = playlist['snippet']['thumbnails']
	if 'maxres' in pl:
		return pl['maxres']['url']
	elif 'standard' in pl:
		return pl['standard']['url']
	elif 'high' in pl:
		return pl['high']['url']
	elif 'medium' in pl:
		return pl['medium']['url']
	elif 'default' in pl:
		return pl['default']['url']
	else:
		return ''#seems no thumbnail is found

#determines the best thumbnail from the youtube response
def best_thumbnail(res):    
    thumbnail = False
    #If this playlist has a thumbnail, use the best possible thumbnail for this playlist
    if 'thumbnails' in res:
        #if 'maxres' in res['thumbnails']:
        #    thumbnail = res['thumbnails']['maxres']
        if 'standard' in res['thumbnails']:
            thumbnail = res['thumbnails']['standard']['url']
        elif 'high' in res['thumbnails']:
            thumbnail = res['thumbnails']['high']['url']
        elif 'medium' in res['thumbnails']:
            thumbnail = res['thumbnails']['medium']['url']
        elif 'default' in res['thumbnails']:
            thumbnail = res['thumbnails']['default']['url']
        log('The thumbnail: '+thumbnail)
    return thumbnail