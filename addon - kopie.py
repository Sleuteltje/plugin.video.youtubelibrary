import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import urllib
import urllib2
import re
import urlparse
import httplib
import pafy 

#Log prefix
LPREF = 'MICHS YoutubeLibrary:::::::: '

#Tell the log that our addon is running
xbmc.log(LPREF+'Running')


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)
    
#Add Directory to Kodi
def adddir(name, url):
    li = xbmcgui.ListItem('Folder One', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'Folder Two'})
    li = xbmcgui.ListItem('Folder Two', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)    
    

mode = args.get('mode', None)

if mode is None:
    url = build_url({'mode': 'folder', 'foldername': 'Folder One'})


    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'folder':
    foldername = args['foldername'][0]
    url = 'http://localhost/some_video.mkv'
    li = xbmcgui.ListItem(foldername + ' Video', iconImage='DefaultVideo.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)













# addon       = xbmcaddon.Addon()
# addonname   = addon.getAddonInfo('name')
# addonId = addon.getAddonInfo('id')

# pluginhandle = int(sys.argv[1])

#Set this to episodes view
#xbmcplugin.setContent(pluginhandle, 'episodes')


