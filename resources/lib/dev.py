#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
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
    if debug is True:
        xbmc.log(vars.LPREF+message)
    else:
        if vars.__settings__.getSetting("debugmode") == 'true':
            xbmc.log(vars.LPREF+message)

#Returns a legal filename (without characters the OS wont accept)
def legal_filename(filename):
    import re
    return re.sub('[^\w\-_\. ]', '_', filename)
    
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
def adddir(name, url, thumb='DefaultFolder.png', fanart = None, description = ''):
    li = xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage = thumb)
    #Set type to video and give a description and such
    li.setInfo( type="Video", infoLabels={ "Title": name,"Plot":description} )
    if fanart is not None:
        li.setProperty('fanart_image', fanart)
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