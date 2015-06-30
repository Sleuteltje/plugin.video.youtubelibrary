import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import urllib
import urllib2
import re
import urlparse
import httplib
import pafy 


addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addonId = addon.getAddonInfo('id')

pluginhandle = int(sys.argv[1])

#Set this to episodes view
xbmcplugin.setContent(pluginhandle, 'episodes')

#Log prefix
LPREF = 'MICHS YoutubeLibrary:::::::: '

#Tell the log that our addon is running
xbmc.log(LPREF+'Running')




#Get the title from the youtube title
v = pafy.new("sdBLSTSN1HI")
#print(v.title)
#print(v.duration)
#print(v.rating)
#print(v.author)
#print(v.length)
#print(v.keywords)
#print(v.thumb)
#print(v.videoid)
#print(v.viewcount)

xbmc.log(LPREF+'Grabbed Vid Info: '+v.title)
xbmc.log(LPREF+'Sys arguments: '+sys.argv[0]+', '+sys.argv[1]+', '+sys.argv[2])

#Routes
#if mode == "channel":
#    channel(url)
#else:
#    index()

    
def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict
    
#Play the youtube video
def playVideo(url):
    addLink('Should have playd', url, "playVideo", 'https://cdn2.iconfinder.com/data/icons/faceavatars/PNG/D04.png', 'Play this test video')
    xbmcplugin.endOfDirectory(pluginhandle)
    #xbmc.RunPlugin(plugin://plugin.video.youtube/play/?video_id=url)
    #xbmcplugin.endOfDirectory(pluginhandle)


#Creates a .strm file
def library_movie_strm(i):
    xbmc.log('MICHS::::::: strm maker started')
    #movieLibrary        = os.path.join(xbmc.translatePath(getSetting("movie_library")),'')
    #movieLibrary  = os.path.join('E:/', "")
    movieLibrary = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.youtubelibrary/Streams'), '')
    try:
        name = i
        sysname = urllib.quote_plus(name)

        content = '%s?action=play&name=%s' % ( sys.argv[0], sysname)

        xbmcvfs.mkdir(movieLibrary)
        xbmc.log('MICHS:::::: strm generated')

        enc_name = name.translate(None, '\/:*?"<>|').strip('.')
        folder = os.path.join(movieLibrary, enc_name)
        xbmcvfs.mkdir(folder)

        stream = os.path.join(folder, enc_name + '.strm')
        file = xbmcvfs.File(stream, 'w')
        file.write(str(content))
        file.close()
    except:
        pass




    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))


if mode == "playVideo":
    xbmc.log(LPREF+'!!!!!!!::::::: Mode is playVideo')
    #xbmc.executebuiltin('XBMC.RunPlugin(
    #playVideo(url)
    test('should have played')
else:
    xbmc.log(LPREF+'!!!!!!!:::::::: Mode is Index')
    index(v)
    library_movie_strm(v.videoid)