######################################
### Kodi Addon : Youtube Library
### Adds youtube channels as tv shows in the library
###
### Author: M. Roffel (c) 2015
######################################
import os, shutil
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import urllib
import urllib2
import re
import urlparse
import httplib
#For ripping youtube information & url's
import pafy 
#For XML Reading & Writing
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
# For prettyfing the XML
from xml.dom import minidom
#For youtube api
import httplib2
import six
from apiclient.discovery import build
import sys
#from googleapiclient.discovery import build

#Kodi Settings
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

#####Settings######
#Log prefix
LPREF = 'MICHS YoutubeLibrary:::::::: '
#Tell the log that our addon is running
xbmc.log(LPREF+'Running')
#Run the Addon in Debug mode?
DEBUGMODE = True
#The link that should be written in the strm file, so the videoaddon can play
ADDONLINK= 'plugin://plugin.video.youtube/play/?video_id='
#Set the type of content view
xbmcplugin.setContent(addon_handle, 'episodes')

# Set API_KEY to the "API key" value from the "Access" tab of the
# Google APIs Console http://code.google.com/apis/console#access
# Please ensure that you have enabled the YouTube Data API and Freebase API
# for your project.
API_KEY = "AIzaSyBtO0Bl38DJKCuPh9e4mRW3-1UcGPPnQfs"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
#Set the youtube api key for pafy to
pafy.set_api_key(API_KEY)

##NONCONFIGURABLE
#Paths
addonPath = xbmcaddon.Addon().getAddonInfo("path")
IMG_DIR = os.path.join(addonPath,'resources/media')
gearArt = os.path.join(addonPath,'resources/media/gear.png')
settingsPath = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.youtubelibrary/Settings'), '')
#Addonname and icon
__addonname__ = xbmcaddon.Addon().getAddonInfo('name')
__icon__ = xbmcaddon.Addon().getAddonInfo('icon')

##Grab the addon settings
__settings__ = xbmcaddon.Addon("plugin.video.youtubelibrary")
service_interval = __settings__.getSetting("service_interval") #The interval at which the service will run & update
#Convert service interval back to an integer
if service_interval == '':
    service_interval = 12 #Default service_interval
else:
    service_interval = int(service_interval)
tv_folder_path = xbmc.translatePath(__settings__.getSetting("tv_folder"))
tv_folder = os.path.join(tv_folder_path, '') #The directory where all the tv-shows .strm & nfo files will be added
update_videolibrary = __settings__.getSetting("update_videolibrary") #Should we update the video library after updating all playlists?
















########## KODI DEV FUNCTIONS ############
#Log function
#Params
#   Message:  The message to display in the log
#   Debug: Also display this message if debugmode is off?
def log(message, debug=None):
    if debug is True:
        xbmc.log(LPREF+message)
    else:
        if DEBUGMODE == True:
            xbmc.log(LPREF+message)


#Construct a url to this plugin
# Params:
#    query: A dict with urls that will be transcoded to a plugin url 
#    Example:
#       {'mode' : 'folder', 'foldername' : 'channels'}
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)
    
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
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
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
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

#Build the thumbnail url from the resources/media dir
def media(img):
    log('grabbing media file: '+img)
    return os.path.join(IMG_DIR, img+".png")

    
#Asks the user for input
# Parameter :                                           #
#                                                       #
# name        sugested name for export                  #
#                                                       # 
# Returns   :                                           #
#                                                       #
# name        name of export excluding any extension    #
#                                                       #
def GUIEditExportName(name, title='Enter input'):

    kb = xbmc.Keyboard('default', 'heading')
    kb.setDefault(name) # optional
    kb.setHeading(title) # optional
    #kb.setHiddenInput(True) # optional
    kb.doModal()
    if (kb.isConfirmed()):
        text = kb.getText()
    return(text)
   
############################ XML SETTINGS #################################### 
#Loads the xml document        
def xml_get():
    log('XML_get')
    global document #Set the document variable as global, so every function can reach it
    document = ElementTree.parse( settingsPath+'settings.xml' )
    

# Converts the elementtree element to prettified xml and stores it in the settings.xml file
def write_xml(elem):
    xbmcvfs.mkdir(settingsPath) #Create the settings dir if it does not exist already
    #Write these settings to a .xml file in the addonfolder
    output_file = os.path.join(settingsPath, 'settings.xml') #Set the outputfile to settings.xml

    indent( elem ) #Prettify the xml so its not on one line
    tree = ElementTree.ElementTree( elem ) #Convert the xml back to an element
    tree.write(output_file, xml_declaration=True, encoding='utf-8', method="xml") #Save the XML in the settings file

#Pretty Print the xml    
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

    
# Creates the settings.xml file
def create_xml():
    log('Create_xml')
    
    #<playlists>
    root = Element('config')
    newxml = SubElement(root, 'playlists')
    
    example = {
        'id'    : 'PUTPLAYLISTIDHERE',
        'enabled'      : 'no',
        'settings'      : {
            'type'                  : 'TV',
            'title'                   : 'Exampleplaylist',
            'description'        : 'This is an example of a youtube playlist xml config for use with Youtube Library',
            'genre'                : 'Action/Comedy',
            'published'          : '2010',
            #Art
            'thumb'               : 'thumbimgurl',
            'fanart'                : 'fanarturl',
            'banner'              : 'bannerurl',
            'epsownfanart'    : 'No',
            # STRM & NFO Settings
            'writenfo'             : 'Yes',
            'delete'                : '168',
            'keepvideos'        : '500',
            'overwritefolder'   : 'Z:/MEDIA/TV Shows/Example show',
            #Filters
            'minlength'         : '12:00',
            'maxlength'         : '25:00',
            'excludewords'    : 'trailer|commercial',
            'onlyinclude'       : 'review',
            #Strip Stuff from NFO information
            'striptitle'            : 'Brought to you by',
            'removetitle'       : 'Example Youtube Channels|Always annoying part of title',
            'stripdescription' : 'See our other channels|Subscribe to our channel',
            'removedescription' : 'Brought to you by our sponsors',
            #Scan Settings
            'lastvideoId'       : 'Wixi28loswo',
            'scansince'        : '29 jun 2015 18:23:21'
        }
    }

    
    playlist = xml_create_playlist(example)
    #Append this playlist to the new created xml file
    #newxml.append(playlist)
    #Write this new xml to the settings.xml file
    write_xml(root)
    log('Create_xml: Created new settings.xml file')

    
#Deletes a playlist from the xml and saves it
def xml_remove_playlist(id):
    log('XML_remove_playlist('+id+')')
    pl = xml_get_elem('playlists/playlist', 'playlist', {'id': id})
    if pl is not None:
        log('Found the playlist to delete')
        
        root = document.getroot()
        parent = root.find('playlists')
        parent.remove(pl)
        write_xml(root)
        log('XML_remove_playlist: Removed playlist '+id)
        return True
    else:
        return False
       
    
#Adds the playlist to the xml if it does not exist yet, and retrieves information about the playlist
def xml_add_playlist(id):
    log('XML_add_playlist('+id+')')
    #Check if this playlist isnt in the xml file yet
    if xml_get_elem('playlists/playlist', 'playlist', {'id' : id}) is None:
        #Playlist does not yet exist, grab the channel id by this playlist id
        response = yt_get_playlist_info(id)
        #Save relevant information in res
        res = response['items'][0]['snippet']
        #channelid = res['channelId']
        
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
        
        
        #Grab the channel information 
        response = yt_get_channel_info(res['channelId'])
        snippet = response['items'][0]['snippet']
        brand = response['items'][0]['brandingSettings']
        #Check if we should do a better thumbnail
        if thumbnail is False:
            if 'thumbnails' in snippet:
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
        if thumbnail is False:
            thumbnail = ''

            
        #Check what the better description is
        if len(res['description']) > 0:
            description = res['description']
        else:
            description = snippet['description']
            
        #Check what the best title is
        if res['title'] == 'Uploads from '+snippet['title']:
            #Set title to just the channelname
            title = snippet['title']
        else:
            #Prefix the playlistname with the channelname
            title = snippet['title']+' - '+res['title']
        
        
        
        #Build the playlist
        playlist = {
            'id'    : id,
            'enabled'      : 'no',
            'settings'      : {
                'type'                  : 'TV',
                'title'                   : title,
                'channel'            : snippet['title'],
                'description'        : description,
                'genre'                : 'Youtube',
                'published'          : snippet['publishedAt'],
                #Art
                'thumb'               : thumbnail,
                'fanart'                : brand['image']['bannerTvImageUrl'],
                'banner'              : brand['image']['bannerImageUrl'],
                'epsownfanart'    : 'No',
                # STRM & NFO Settings
                'writenfo'             : 'Yes',
                'delete'                : '',
                'keepvideos'        : '',
                'overwritefolder'   : '',
                #Filters
                'minlength'         : '',
                'maxlength'         : '',
                'excludewords'    : '',
                'onlyinclude'       : '',
                #NFO information
                'season'            : 'year',
                'episode'           : 'monthday',
                'striptitle'            : '',
                'removetitle'       : '',
                'stripdescription' : '',
                'removedescription' : '',
                #Scan Settings
                'lastvideoId'       : '',
                'scansince'        : ''
            }
        }
        pl = xml_create_playlist(playlist)
        root = document.getroot()
        root[0].insert(0, pl)
        write_xml(root)
        log('Added the playlist '+id+' to the settings.xml')
    else:
        log('XML_add_playlist: not added playlist '+id+' since the playlist already exists')    
    
# Builds and returns an playlist element that can be added to the playlist element
def xml_create_playlist(options):    
    #       <playlist id="">
    attr = { 'id' : options['id'], 'enabled' : options['enabled'] }
    elem = Element('playlist', attr)
    
    #               <settingname>setting</settingname>
    # Loop through all settings and set them accordingly
    for key, value in options['settings'].iteritems():
        SubElement(elem, key).text = value
    
    return elem #Return this element


# Updates a playlist that already exists
def xml_update_playlist_attr(id, attr, val):
    log('XML: Updating playlist id '+id+' with attr '+attr+' : '+val)
    
    #Grab this playlist from the xml file
    playlist = xml_get_elem('playlists/playlist', 'playlist', {'id' : id})
    
    #Check if we have succesfully retrieved the playlist
    if playlist == None:
        log('XML_update_playlist: could not find playlist '+id)
    else:
        log('XML_update_playlist_: found playlist '+id)
        
        
        #Update this attribute to the new val
        del playlist.attrib[attr]  
        playlist.attrib[attr] = val
        #playlist.set(attr, val)
        #Write this to the xml
        root = document.getroot()
        write_xml(root)
        log('XML_update_playlist_attr: written XML')
        
# Updates a playlist setting (like <age>)
def xml_update_playlist_setting(id, tag, newsetting):
    log('XML_update_playlist_setting ('+id+', '+tag+', '+newsetting+')')
    
    #Grab this playlist from the xml file
    elem = xml_get_elem('playlists/playlist', 'playlist', {'id' : id})
    
    #Check if we have succesfully retrieved the playlist
    if elem == None:
        log('XML_update_playlist_setting: could not find playlist '+id)
        return False
    else:
        log('XML_update_playlist_setting: found playlist '+id)
        
        #Find the setting that needs to be changed
        setting = elem.find(tag)
        if setting == None:
            #Could not find setting
            log('XML_update_playlist_setting: could not find setting '+tag+' of '+id)
            return False
        else:
            #Change the setting to its new setting
            setting.text = newsetting
            #Write this to the xml
            root = document.getroot()
            write_xml(root)
            log('XML_update_playlist_setting: Updated xml setting '+tag+' of '+id+' to '+newsetting)
            return True


        
# xml_get_elem
    # Grabs the element you are looking from the xml file and returns it
                        # Example: 
                        # <users>
                        #   <user name="someuser">sometext</user>  <--- This you would like to update
                        #   <user name="leavethisbe">Dont want to update this</user>
                        
        # path: Path to the xml element you would like to parse. (In the examples case: 'users/user')
        # tag:  The tag that should be found (In the examples case: user)
        # whereAttrib: The element that should be found should contain the following attribute at the following value. (In the examples case: {name: someuser}
        # whereTxt: The element that should be found should contain this text. (In the examples case: 'sometext' would find the correct user       
def xml_get_elem(path, tag, whereAttrib=False, whereTxt=False):    
    log('XML_get_elem')
    xml_get() # Grab the xml file
    
    for child in document.findall(path):
        check = True # Use this var to check if this element meets all requirements. Set it by default to true, so it can be set to False if it fails some requirement
        #Check if this element has the tag we are looking for
        if child.tag == tag:
            #Should we also check that the element has a certain attribute with a certain value?
            if whereAttrib != False:
                # Check if this element meets all the requirements of the attributes
                for key, value in whereAttrib.iteritems():
                    if child.attrib[key] != value:
                        #This element does not meet all requirements, so quit this for loop, since checking for others ones has no use, since it already does meet this requirement
                        check = False
                        break
            
            if check == False: #It has already failed to meet a requirement, so skip to the next xml element
                continue
            
            #Should we check if the element has the given text?
            if whereTxt != False:
                # Check if this element has the same text as required
                if child.text != whereTxt:
                    #This XML element does not meet te requirement of holding the same text, so we will skip to the next xml element
                    continue
            
            #If check is still true, we have found the correct element, so return this element
            return child
            break
    
    #If the code has made it here, that means it has failed to find the xml element, so return None
    return None   
   
   
   

    



    

##### YOUTUBE API FUNCTIONS #########
#Grabs the Channel information by the playlist ID 
#Returns the channel id 
def yt_get_playlist_info(id):
    #Connect to youtube API
    youtube = build(
      YOUTUBE_API_SERVICE_NAME, 
      YOUTUBE_API_VERSION, 
      developerKey=API_KEY
    )
    #Retrieve the information from the youtube API
    response = youtube.playlists().list(
      part="contentDetails,id,snippet",
      id=id,
      maxResults=50
    ).execute()
    
    return response
    
    videos = []
    
    #Grab the playlists from the response
    playlists = search_response['items'][0]['contentDetails']['relatedPlaylists']
    
    # Go through each playlist and display the playlist
    for key, value in playlists.iteritems():
      #videos.append(search_result)
      url = build_url({'mode': 'addPlaylist', 'id': value})
      adddir(key, url, search_response['items'][0]['snippet']['thumbnails']['default']['url'])
      

#Grabs the playlists that the given channelid has created
def yt_get_playlists_by_channel(id):
    #Connect to youtube API
    youtube = build(
      YOUTUBE_API_SERVICE_NAME, 
      YOUTUBE_API_VERSION, 
      developerKey=API_KEY
    )
    #Retrieve the information from the youtube API
    response = youtube.playlists().list(
      part="contentDetails,snippet",
      channelId=id,
      maxResults=50
    ).execute()
    
    return response['items']
      


#Grabs playlists & channel information by id
# Params:
    # ChannelId : The id of the channel we want to retrieve
def yt_get_channel_info(Channelid):
    #Connect to youtube API
    youtube = build(
      YOUTUBE_API_SERVICE_NAME, 
      YOUTUBE_API_VERSION, 
      developerKey=API_KEY
    )
    #Search for the channels with the following parameters
    search_response = youtube.channels().list(
      part="brandingSettings,snippet,contentDetails",
      id=Channelid,
      maxResults=50
    ).execute()
    
    return search_response
      
      
#Searches for channels by keyword
# Params:
    # keyword : The keyword we want to use to search for channels
def search_channel(keyword):
    youtube = build(
      YOUTUBE_API_SERVICE_NAME, 
      YOUTUBE_API_VERSION, 
      developerKey=API_KEY
    )
    search_response = youtube.search().list(
      q=keyword,
      part="id,snippet",
      maxResults=50,
      type = "channel"
    ).execute()
    
    videos = []

    for search_result in search_response.get("items", []):
      #videos.append(search_result)
      url = build_url({'mode': 'pickedChannel', 'id': search_result['id']['channelId']})
      adddir(search_result['snippet']['title'], url, search_result['snippet']['thumbnails']['default']['url'])

      
#Searches for Youtube videos by a given keyword
# Params:
    # keyword: The keyword to search for
def search_by_keyword(keyword):
    youtube = build(
      YOUTUBE_API_SERVICE_NAME, 
      YOUTUBE_API_VERSION, 
      developerKey=API_KEY
    )
    search_response = youtube.search().list(
      q=keyword,
      part="id,snippet",
      maxResults=50
    ).execute()
    
    for search_result in search_response.get("items", []):
      #videos.append(search_result)
      additem(search_result['snippet']['title'], 'http://somevid.mkv', search_result['snippet']['thumbnails']['default']['url'])

#Grabs the videos from a playlist by playlistId
# Params: 
    # id: The id of the playlist which videos you want to retrieve
    #nextpage: The nextpage token. Default: false. If set it will retrieve the page. That allows all videos to be parsed, instead of the 50 limit
def vids_by_playlist(id, nextpage = False):
    youtube = build(
      YOUTUBE_API_SERVICE_NAME, 
      YOUTUBE_API_VERSION, 
      developerKey=API_KEY
    )
    if nextpage == False:
        search_response = youtube.playlistItems().list(
          part="snippet,contentDetails",
          maxResults=50,
          playlistId=id
        ).execute()
    else:
        search_response = youtube.playlistItems().list(
          part="snippet,contentDetails",
          maxResults=50,
          playlistId=id,
          pageToken=nextpage
        ).execute()
    
    return search_response

    # for search_result in search_response.get("items", []):
      # additem(search_result['snippet']['title'], 'http://somevid.mkv', search_result['snippet']['thumbnails']['default']['url'])

#Grabs the duration of a list of youtube video IDs (you can add a max of 50 videoIDs to each call)
def get_duration_vids(vid_ids):
    log('Grabbing duration of youtube videos')
    
    #Create a seperated string of vid_ids to give to the API
    idlist = ''
    for id in vid_ids:
        idlist += id+','
    idlist = idlist[:-1]
    
    youtube = build(
      YOUTUBE_API_SERVICE_NAME, 
      YOUTUBE_API_VERSION, 
      developerKey=API_KEY
    )
    search_response = youtube.videos().list(
      part="contentDetails",
      maxResults=50,
      id=idlist
    ).execute()

    #Get the duration of each video in the response
    durations = {}
    for vid in search_response.get("items", []):      
        dur = vid['contentDetails']['duration']
        dur = dur[2:] #Strip PT from the duration
        log('Duration of video: '+dur)
        
        seconds = hms_to_sec(dur)

        log('Which makes the video %s seconds long' % seconds)
        vidid = vid['id']
        durations[vidid] = seconds
        #except Exception as e:
            #log("Couldnt extract time: %s" % e)
            #pass
    
    return durations

################## Generators ####################
def legal_filename(filename):
    import re
    return re.sub('[^\w\-_\. ]', '_', filename)

#Converts youtube publishedAt date to list containing year, month, day, hour, minutes, seconds
def convert_published(date):
    d = {}
    d['year'] = date[:4]
    d['month'] = date[5:7]
    d['day'] = date[8:10]
    d['hour'] = date[11:13]
    d['minute'] = date[14:16]
    d['second'] = date[17:19]
    return d
    
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
                log('Regex '+ma+' found its match: '+m.group(0).encode('UTF-8')+' , '+m.group(1).encode('UTF-8'))
                return m.group(1)
            else:
                #Regex not found, return None
                log('Regex given by user has not found anything: '+ma+' on '+txt.encode('UTF-8'), True)
                return None #Return the fallback
        else:
            log('Regex given by user in settings.xml is not valid!'+se, True)
            return None
    else:
        return None #This is not a regex setting
    
#Generates the season and episode number
    #Vid: The video response from the youtube api
    #settings: The elementtree element containing the playlist settings
    #totalresults = The total results of the playlist, so that the episode can be calculated if the episode recognisition is set to pos
def episode_season(vid, settings, totalresults = False):
    ep = settings.find('episode').text #Grab the episode settings from the xml
    se = settings.find('season').text
    
    found = False
    #See if there should be a regex search for the season
    if se[:6] == 'regex(':
        match = reg(se, vid['snippet']['title'])
        if match != None:
            season = match[0]
            found = True

    if found == False: #If the episode has not been found yet, either it is not regex, or regex failed
        if se == 'year': #We want to save the season of the video as the year it is published
            d = convert_published(vid['snippet']['publishedAt'])
            season = d['year']
        elif se.isdigit(): #If the season is set to a hardcoded number
            season = str(se)
        else:
            log('Error: invalid season tag in settings.xml: '+se+', set season to 0', True)
            season = '0'
        
    found = False
    #See if there should be a regex search for the season
    if ep[:6] == 'regex(':
        match = reg(ep, vid['snippet']['title'])
        if match != None:
            episode = match
            found = True
    
    if found == False:
        if ep == 'monthday': #We want the episode to be the month number + day number
            d = convert_published(vid['snippet']['publishedAt'])
            episode = d['month']+d['day']
        elif ep == 'monthdayhour': #month number + day number + hour number
            d = convert_published(vid['snippet']['publishedAt'])
            episode = d['month']+d['day']+d['hour']
        elif ep == 'monthdayhourminute': #month + day + hour + minute numbers
            d = convert_published(vid['snippet']['publishedAt'])
            episode = d['month']+d['day']+d['hour']+d['minute']
        elif ep == 'pos': #The position in the playlist as episode number
            episode = str(int(totalresults) - int(vid['snippet']['position']))
        elif ep.isdigit(): #A hardcoded number as episode number
            episode = str(ep)
        else:
            log('Invalid episode setting in settings.xml! '+ep)
            episode = '0'
            
    return [season, episode]

    
        
    

###### STRM GENERATOR ##############
#Creates a .strm file
# Name : The name of the strm file
# folder:   The name of the folder the strm file should be written in (Not the mainfolder, but the name of the show, so the strms get in that subdir)
# videoid:  The videoid of the youtube video we want to make a strm off
def write_strm(name, fold, videoid):
    #log('strm('+name+', '+fold+', '+videoid+')')
    #movieLibrary = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.youtubelibrary/Streams'), '')
    movieLibrary = tv_folder #The path we should save in is the tv_folder setting from the addon settings
    
    sysname = urllib.quote_plus(videoid) #Escape strings in the videoid if needed

    content = ADDONLINK+'%s' % ( sysname) #Set the content of the strm file

    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    

    #enc_name = name.translate('\/:*?"<>|').strip('.') #Escape special characters in the name
    enc_name = legal_filename(name)
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet

    stream = os.path.join(folder, enc_name + '.strm') #Set the file to maindir/name/name.strm
    file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    file.write(str(content)) #Write the content in the file
    file.close() #Close the file
    log('write_strm: Written strm file: '+fold+'/'+enc_name+'.strm')
    #except:
        #pass          
        

        
###### NFO GENERATOR ##############
#Creates a .nfo file
# Name : The name of the nfo file
# folder:   The name of the folder the nfo file should be written in (Not the mainfolder, but the name of the show, so the nfo get in that subdir)
# vid: THe video youtube response we want to add
# settings:  The elementtree containing the settings from the playlist
# season: The season of the episode
#episode: The episode number
def write_nfo(name, fold, vid, settings, season, episode):
    #log('write_nfo('+name+', '+fold+')')
    #movieLibrary = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.youtubelibrary/Streams'), '')
    movieLibrary = tv_folder #Use the directory from the addon settings

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
            if removetitle in title:
                title = title.replace(removetitle, '')
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
                    title = title[:title.needle(s)] #Strip everything to the point where the line was found
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
                    description = description[:description.needle(s)] #Strip everything to the point where the line was found
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
    d = convert_published(snippet['publishedAt'])
    normaldate = d['year']+'/'+d['month']+'/'+d['day']
    
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
        </episodedetails>
    """ % {
        'title': title,
        'plot': description,
        'channel': settings.find('channel').text,
        'thumb': thumbnail,
        'date': normaldate,
        'season': season,
        'episode': episode
    }
    
    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    

    #enc_name = name.translate('\/:*?"<>|').strip('.') #Escape special characters in the name
    enc_name = legal_filename(name)
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet

    stream = os.path.join(folder, enc_name + '.nfo') #Set the file to maindir/name/name.strm
    file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    file.write(str(content.encode("utf-8"))) #Write the content in the file
    file.close() #Close the file
    log('write_nfo: Written nfo file: '+fold+'/'+enc_name+'.nfo')
    #except:
        #pass          
        
        
        
#Writes the NFO for the tvshow
    #fold: The folder the nfo should be written to
    #settings: The elementtree element containing the playlist xml settings
def write_tvshow_nfo(fold, settings):
    log('write_tvshow_nfo('+fold+')')
    name = 'tvshow'
    movieLibrary = tv_folder #Use the directory from the addon settings

    #Grab the published date and convert it to a normal date
    d = convert_published(settings.find('published').text)
    normaldate = d['year']+'-'+d['month']+'-'+d['day']
    
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
    }
    
    xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    enc_name = legal_filename(name) #Set the filename to a legal filename
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
    log('write_tvshow_nfo: Written tvshow.nfo file: '+fold+'/'+enc_name+'.nfo')
    #except:
        #pass          
      
      
      
      
      
########## ROUTES FUNCTIONS ##############
def index():      
    url = build_url({'mode': 'folder', 'foldername': 'managePlaylists'})
    adddir('Manage Playlists', url)    
    # url = build_url({'mode': 'folder', 'foldername': 'Folder One'})
    # adddir('Folder one', url)    
    # url = build_url({'mode': 'folder', 'foldername': 'Youtube Plugin Test'})
    # adddir('Youtube Plugin Test', url)    
    # url = build_url({'mode': 'folder', 'foldername': 'See All'})
    # adddir('See All', url)
    # url = build_url({'mode': 'folder', 'foldername': 'Cat'})
    # adddir('Search for cat', url)
    # url = build_url({'mode': 'folder', 'foldername': 'StukTV'})
    # adddir('StukTV', url)
    # url = build_url({'mode': 'folder', 'foldername': 'readsettings'})
    # adddir('readsettings', url)
    # url = build_url({'mode': 'folder', 'foldername': 'displaychannels'})
    # adddir('Display Channels', url)
    # url = build_url({'mode': 'folder', 'foldername': 'search'})
    # adddir('Search', url)
    url = build_url({'mode': 'folder', 'foldername': 'searchchannel'})
    adddir('Search Channel', url)
    url = build_url({'mode': 'xmlcreate', 'foldername': 'xmlcreate'})
    adddir('XML Create Test', url)
    url = build_url({'mode': 'strmtest', 'id': 'UUSc16oMxxlcJSb9SXkjwMjA'})
    adddir('STRM Test', url)
    url = build_url({'mode': 'strmtest', 'id': 'PLV8Q_exbQpnYuouifDyV93_a_PlcwNM1l'})
    adddir('STRM StukTV Opdrachten Test', url)
    url = build_url({'mode': 'updateplaylists'})
    adddir('Update All Playlists (can take a while)', url, description='If playlists are never scanned before, expect a long wait.')
    url = build_url({'mode': 'deletetest'})
    adddir('Deletetest', url, description='Test the deleting of an entire directory')
    # url = build_url({'mode': 'xmlupdate', 'foldername': 'xmlupdate'})
    # adddir('XML Update Test', url)
    # url = build_url({'mode': 'xmlnew', 'foldername': 'xmlcreate'})
    # adddir('XML New Test', url)

        ##Route: Manage Playlists
def manage_playlists():
    log('manage_playlists()')
    #pl = xml_get_elem('playlists', 'playlists') #Grab <playlists>
    xml_get()
    pl = document.findall('playlists/playlist')
    if pl is not None: 
        for child in pl: #Loop through each playlist
            url = build_url({'mode': 'editPlaylist', 'id': child.attrib['id']})
            adddir(child.find('title').text, url, child.find('thumb').text, child.find('fanart').text, child.find('description').text)
            
    
        ##Route: show_playlists_by_channel
def show_playlists_by_channel(Channelid):
    search_response = yt_get_channel_info(Channelid)
    
    #Grab the playlists from the response
    playlists = search_response['items'][0]['contentDetails']['relatedPlaylists']
    
    # Go through each playlist and display the playlist
    for key, value in playlists.iteritems():
      #Grab the number of videos to
      pl = yt_get_playlist_info(value)
      number_vids = str(pl['items'][0]['contentDetails']['itemCount'])
      #videos.append(search_result)
      url = build_url({'mode': 'addPlaylist', 'id': value})
      adddir(key.capitalize()+' ('+number_vids+')', url, search_response['items'][0]['snippet']['thumbnails']['default']['url'])
    
    # Grab other playlists this user has created to
    response = yt_get_playlists_by_channel(Channelid)
    
    if isinstance(response, list):
        # Go through each playlist and display the playlist
        for playlist in response:
          #videos.append(search_result)
          title = playlist['snippet']['title']+' ('+str(playlist['contentDetails']['itemCount'])+')'
          url = build_url({'mode': 'addPlaylist', 'id': playlist['id']})
          adddir(title, url, playlist['snippet']['thumbnails']['default']['url'])
    
    
    

    
    
        ##Route: editPlaylist
        #Displays the editplaylist list item
def disp_setting(setting, title, description):
    #build url
    if elem.find(setting) != None:
        val = elem.find(setting).text
    if val == None or val == 'None':
        val = ''
    url = build_url({'mode': 'editPlaylist', 'id': plid, 'set': setting})
    adddir('[COLOR blue]'+title+':[/COLOR] '+val, url, gear, fanart, description)
        
        #Displays the settings from the settings.xml file and gives the option to edit the functions
def editPlaylist(id):
    global plid #Make the plid global so disp_setting can reach it without calling it
    global elem #Make the elem global so disp_setting can reach it without calling it
    global fanart #Make fanart global so disp_setting can reach it without calling it
    global gear #Make gear global so disp_setting can reach it without calling it
    plid = id
    log('editPlaylist('+id+')')
    #Loads the correct information from the settings.xml
    elem = xml_get_elem('playlists/playlist', 'playlist', {'id': id})
    if elem is None:
        #We could not find this playlist to edit!
        log('Could not find playlist '+id+' to edit!')
        return False
    else:
        '''
            Build the edit Playlist form
        '''
        #Grab all art to be used with this playlist edit
        thumb = elem.find('thumb').text
        fanart = elem.find('fanart').text
        gear = media('gear')
        
        #Return to home button
        url = build_url({'home': 'home'})
        adddir('[COLOR white]Return to Main Menu[/COLOR]', url, media('home'), fanart)
        #Edit playlist info
        url = build_url({'mode': 'editPlaylist', 'id': id})
        adddir('[COLOR white]Editing Settings for playlist '+id+'[/COLOR]', url, thumb, fanart, 'This is the edit page for the playlist settings. Set this to your taste to have more control over things as which videos will be included or excluded')
        #Delete playlist
        url = build_url({'mode': 'deletePlaylist', 'id': id})
        adddir('[COLOR red]Delete playlist[/COLOR]', url, media('delete'), fanart, '<!> Careful! <!> This will delete all the settings from this playlist & this playlist will not be scanned into your library anymore')
        #Refresh playlist
        url = build_url({'mode': 'refreshPlaylist', 'id': id})
        adddir('[COLOR red]Refresh playlist[/COLOR]', url, media('delete'), fanart, '<!> Careful! <!> This will refresh all the episodes from this playlist. Only use this if previous episodes are not scanned properly due to wrong playlist settings.')
        
        #Build the Playlist enable/disable button depending on current state
        if elem.attrib['enabled'] == 'yes':
            url = build_url({'mode': 'editPlaylist', 'id': id, 'set': 'enable'})
            adddir('[COLOR green]Playlist is enabled[/COLOR]', url, thumb, fanart, 'The playlist is enabled. Disable it to stop the videos to be scanned into the Kodi Library')
        else:
            url = build_url({'mode': 'editPlaylist', 'id': id, 'set': 'enable'})
            adddir('[COLOR red]Playlist is disabled![/COLOR]', url, thumb, fanart, 'The playlist is disabled, so you can change your settings before scanning into your Kodi Library. When youre done setting up this playlist, enable it so its gets scanned into the Kodi Library.')
        
        #Title
        disp_setting('title', 'Title', 'The title as it will be displayed in Kodi and this Addon')
        #Description
        disp_setting('description', 'Description', 'The description as it will be displayed in Kodi and this Addon')
        #Genres
        disp_setting('genre', 'Genre', 'Settings as displayed in Kodi. For multiple genres use genre1/genre2/genre3')
        #WriteNFO
        url = build_url({'mode': 'editPlaylist', 'id': id, 'set': 'writenfo'})
        adddir('[COLOR blue]Write NFO:[/COLOR] '+elem.find('writenfo').text, url, gear, fanart, 'NFO Files are needed for Kodi to recognise the youtube episodes as episodes, so it can scan it in its library. If you only want strm files, set this to No')
        
        #Filters
        #Only include
        disp_setting('onlyinclude', 'Only Include', 'Only include videos containing the following text in the title. Placing words in between | will create an or. So review|trailer will only pick up videos with either review or trailer in its title')
        #Exclude words
        disp_setting('excludewords', 'Exclude', 'Excludes videos containing the following text in the title. Placing words in between | will create an or. So review|trailer will refuse videos with either review or trailer in its title')
        #Min Length
        disp_setting('minlength', 'Min length', 'Only include videos with this minimum length')
        #Max Length
        disp_setting('maxlength', 'Max length', 'Only include videos under this maximum length')
        
        #NFO Options
        #Season recognisition setting
        disp_setting('season', 'Season recognisition', 'Set to year to have the episode year upload date as its season. Set to a number to have a hardcoded season for every episode. To find a season from the video title using a regex. Please use regex(yourregexhere). If your regex fails to recognise a season it will fallback on calling it 0.')
        #Episode recognisition setting
        disp_setting('episode', 'Episode recognisition', 'Set to monthday to have the episode month & day upload date as its episode number. Set to pos to have it use its playlist position as its episode number (Know that when videos are removed from the playlist, episode numbering may not be correct for episodes already scanned into the library). Set to a number to have a hardcoded episode for every episode. To find a episode from the video title using a regex. Please use regex(yourregexhere). If your regex fails to recognise a episode it will fallback on calling it 0.')
        #Stripdescription
        disp_setting('stripdescription', 'Strip Description', 'Deletes every text in the description from and including the text filled in here. For instance, if a channel always has a long text in its description thats always the same, like: Check out our website (..). You fill that line in here, and only the part before that line will be included in the description of episodes. For multiple lines to scan for put them between |')
        #removedescription
        disp_setting('removedescription', 'Remove Description', 'Removes this line from the description of episodes.')
        #Striptitle
        disp_setting('striptitle', 'Strip Title', 'Same as stripdescription but for the title')
        #Removetitle
        disp_setting('removetitle', 'Remove Title', 'Same as removedescription but for the title')

        #Overwritefolder
        disp_setting('overwritefolder', 'Folder', 'Use this directory to write the strm & nfo files to. If this is not filled in it will use the title as it will be displayed in the Addon and the Kodi Library')

        
        #Not used (yet)
        #Type
        disp_setting('type', 'Type', '(NOT USED YET) What kind of playlist is this? Possible choices: tv/music/music videos')
        #Delete
        disp_setting('delete', 'Delete older', '(NOT USED YET) Removes videos older then this many hours.')
        #Scansince
        disp_setting('scansince', 'From date', '(NOT USED YET) Skip videos published under this date. But doesnt remove the nfo & strm files like Delete older')
 

        
            #Displays and saves the user input if something from editplaylist should be set
def setEditPlaylist(id, set):
    if set == 'enable':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("Enable", "Would you like to enable this playlist?")
        if i == 0:
            xml_update_playlist_attr(id, 'enabled', 'no')
            #dialog.ok("Set to disabled", "Playlist is disabled.")
        else:
            xml_update_playlist_attr(id, 'enabled', 'yes')
            #dialog.ok("Set to enabled", "Playlist will now be picked up by the scanner")
    elif set == 'writenfo':
        #Display a yes/no dialog to enable / disable
        i = xbmcgui.Dialog().yesno("WriteNFO", "Write NFO files for this playlist?")
        if i == 0:
            xml_update_playlist_setting(id, 'writenfo', 'no')
        else:
            xml_update_playlist_setting(id, 'writenfo', 'Yes')
    else:
        #Its another setting, so its normal text
        elem = xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Find this playlist so we can grab the value of the settings
        setting = str(elem.find(set).text) #Convert the setting to a string so we can input it safely
        if setting == None or setting == 'None':
            setting = ''
        result = GUIEditExportName(setting, 'Change setting '+set) #Ask the user to put in the new setting
        xml_update_playlist_setting(id, set, result) #Save the new setting





    
        ##Route: addPlaylist calls this function

#Recalculates 00h00m00s back to number of seconds
def hms_to_sec(hms):
    m = re.search(r'(?i)((\d+)h)?((\d+)m)?((\d+)s)?', hms)
    if m:
        hours = m.group(2)
        minutes = m.group(4)
        seconds = m.group(6)
        if seconds is None:
            seconds = '0' #Seconds was not set in the setting, so we start with 0 seconds
        seconds = int(seconds)
        log('Seconds is '+str(seconds))
        if minutes is not None: #If minutes are specified
            log('minutes is '+minutes)
            sm = int(minutes) * 60
            seconds = seconds + sm
        if hours is not None:
            log('hours is '+hours)
            sh = int(seconds) * 60 * 60
            seconds = seconds + sh
        return seconds
    else:
        log('Could not extract seconds from hms format: '+hms, True)
        return None

#Writes the nfo & strm files for all playlists
def update_playlists():
    xbmcgui.Dialog().notification(__addonname__, 'Updating Youtube Playlists...', __icon__, 3000)
    xml_get()
    pl = document.findall('playlists/playlist')
    if pl is not None: 
        for child in pl: #Loop through each playlist
            if child.attrib['enabled'] == 'yes': #Playlist has to be enabled
                update_playlist(child.attrib['id']) #Update the nfo & strm files for this playlist
    xbmcgui.Dialog().notification(__addonname__, 'Done Updating Youtube Playlists', __icon__, 3000)
    #Should we also update the video library?
    if update_videolibrary == "true":
        log('Updating video library is enabled. Updating librarys directory %s' % tv_folder_path, True)
        xbmc.executebuiltin('xbmc.updatelibrary(Video,'+tv_folder_path+')')
        
#Writes the nfo & strm files for the given playlist
def update_playlist(id):
    settings = xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Grab the xml settings for this playlist
    if settings is None:
        log('Could not find playlist '+id+' in the settings.xml file', True)
        return False
    else:
        #Check in which folder the show should be added
        folder = settings.find('overwritefolder').text
        if folder is None or folder == '':
            folder = legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
        else:
            folder = legal_filename(folder)
        
        #Create the tvshow.nfo
        writenfo = settings.find('writenfo').text
        if writenfo != 'no':
            write_tvshow_nfo(folder, settings)
        
        update_playlist_vids(id, folder, settings)
    
        return True

#Updates the videos of a playlist
    #the id of the playlist
    #the folder where the strm & nfo files should go
    #the elementtree element containing the playlist xml settings
    #the id of the fist videoId, so it can save that one in the xml if it parsed all videos. Since the newest is the video it should be stopping the next time.
def update_playlist_vids(id, folder, settings, nextpage=False, firstvid = False):
    resp = vids_by_playlist(id, nextpage) #Grab the videos belonging to this playlist
    vids = resp.get("items", [])
    if firstvid == False:
        #Save the first videoId for later reference
        for vid in vids:
            firstvid = vid['contentDetails']['videoId']
            break #we only want the first item
            
    lastvid = False
    
    #Grab settings from the settings.xml for this playlist
    minlength = settings.find('minlength').text
    maxlength = settings.find('maxlength').text
    
    if minlength is not '' and minlength is not None:
        #Recalculate minlength
        minlength = hms_to_sec(minlength)
    else:
        minlength = None
    if maxlength is not '' and maxlength is not None:
        #Recalculate maxlength
        maxlength = hms_to_sec(maxlength)
    else:
        maxlength = None
    
        
    
    #If the minlength and maxlength options are set for this playlist, we should also know extra information about this videos
    if minlength is not None or maxlength is not None:
        log('minlength or maxlength is set in playlist settings. Will grab duration length of videos')
        all_vidids = []
        for vid in vids:
            if vid['snippet']['title'] != 'Private video' and vid['snippet']['title'] != 'Deleted Video':
                all_vidids.append(vid['contentDetails']['videoId']) #Collect all videoids in one list
        duration = get_duration_vids(all_vidids) #Get all the duration of the videos
    
    for vid in vids:
        #Check if we already had this video, if so we should skip it
        if vid['contentDetails']['videoId'] == settings.find('lastvideoId').text:
            lastvid = True
            log('Playlist is up to date in the library. Already have '+settings.find('lastvideoId').text+' in the library. So quitting scanner now')
            break
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
        se = episode_season(vid, settings, resp['pageInfo']['totalResults'])
        season = se[0]
        episode = se[1]
        filename = 's'+season+'e'+episode+' - '+vid['snippet']['title'] #Create the filename for the .strm & .nfo file
        
        write_strm(filename, folder, vid['contentDetails']['videoId']) #Write the strm file for this episode
        if settings.find('writenfo').text != 'no':
            write_nfo(filename, folder, vid, settings, season = season, episode = episode) #Write the nfo file for this episode
    
    #If there is a nextPagetoken there are more videos to parse, call this function again so it can parse them to
    if 'nextPageToken' in resp and lastvid is not True:
        update_playlist_vids(id, folder, settings, resp['nextPageToken'], firstvid)
    else:
        if firstvid != False:
            xml_update_playlist_setting(id, 'lastvideoId', firstvid) #Set the lastvideoId to this videoId so the playlist remembers the last video it has. This will save on API calls, since it will quit when it comes across a video that already has been set
        log('Done ripping videos from playlist: '+id+' firstvid id: '+firstvid)

        
#Deletes a playlist and has an option to remove the directory containing the file to
def delete_playlist(id):
    #Grab the settings from this playlist
    settings = xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Grab the xml settings for this playlist
    if settings is None:
        log('deletePlaylist: Could not find playlist '+id+' in the settings.xml file', True)
        return False
    else:         
        i = xbmcgui.Dialog().yesno("Delete Playlist", "Are you sure you want to delete this playlist?")
        if i == 0:
            editPlaylist(id)
        else:
            if xml_remove_playlist(id) is True:
                xbmcgui.Dialog().ok('Removed Playlist', 'Succesfully removed playlist '+id)
                i = xbmcgui.Dialog().yesno('Delete from library', 'Do you also want to delete the episodes from your library?')
                if i != 0:
                    #Check in which folder the show resides
                    folder = settings.find('overwritefolder').text
                    if folder is None or folder == '':
                        folder = legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
                    else:
                        folder = legal_filename(folder)
                    movieLibrary = tv_folder #Use the directory from the addon settings
                    dir = os.path.join(movieLibrary, folder) #Set the folder to the maindir/dir
                    
                    success = shutil.rmtree(dir, ignore_errors=True) #Remove the directory
                    xbmcgui.Dialog().ok('Removed from library', 'Deleted this show from your library (You should clean your library, otherwise they will still show in your library)')
            index() #Load the index view
    
#Refresh a playlist and has an option to remove the directory containing the file to
def refresh_playlist(id):
    #Grab the settings from this playlist
    settings = xml_get_elem('playlists/playlist', 'playlist', {'id': id}) #Grab the xml settings for this playlist
    if settings is None:
        log('refreshPlaylist: Could not find playlist '+id+' in the settings.xml file', True)
        return False
    else:         
        i = xbmcgui.Dialog().yesno("Refresh Playlist", "Are you sure you want to refresh this playlist?")
        if i != 0:
            xml_update_playlist_setting(id, 'lastvideoId', '')
            xbmcgui.Dialog().ok('Refreshed Playlist', 'Succesfully refreshed playlist '+id)
            i = xbmcgui.Dialog().yesno('Delete from library', 'Do you also want to delete the previous episodes from your library?')
            if i != 0:
                #Check in which folder the show resides
                folder = settings.find('overwritefolder').text
                if folder is None or folder == '':
                    folder = legal_filename(settings.find('title').text) #Overwrite folder is not set in settings.xml, so set the folder to the title of the show
                else:
                    folder = legal_filename(folder)
                movieLibrary = tv_folder #Use the directory from the addon settings
                dir = os.path.join(movieLibrary, folder) #Set the folder to the maindir/dir
                
                success = shutil.rmtree(dir, ignore_errors=True) #Remove the directory
                xbmcgui.Dialog().ok('Removed from library', 'Deleted the previous episodes from your library (You should clean your library, otherwise they will still show in your library)')
            editPlaylist(id) #Load the editplaylist view

    
      
########## ROUTES ##############      
#Check if this is the first run of the addon
if xbmcvfs.exists(os.path.join(settingsPath,"settings.xml")) == False: #If the settings.xml file can't be found, this is the first addon run
    xbmcgui.Dialog().ok('First Run', 'Please read the online instructions how to use this addon. See online how you can help this project. Have fun!')
    create_xml()
    
#Grab which mode the plugin is in    
mode = args.get('mode', None)

##Index
if mode is None:
    log('Mode is Index', True)
    index()
    xbmcplugin.endOfDirectory(addon_handle)

##Folder
elif mode[0] == 'folder':
    foldername = args['foldername'][0]
    #Which folder should be loaded?
    ## managePlaylists
    if foldername == 'managePlaylists':
        manage_playlists()
        xbmcplugin.endOfDirectory(addon_handle)
    ## Search Channel
    elif foldername == 'searchchannel':
        result = GUIEditExportName('', 'Search for Channel')
        if len(result) > 0:
            search_channel(result)
        xbmcplugin.endOfDirectory(addon_handle)
        
## Channels
elif mode[0] == "pickedChannel":
    log('Picked a channel')
    #Display the videos by their channel ID
    id = args['id'][0]
    show_playlists_by_channel(id)
    xbmcplugin.endOfDirectory(addon_handle)
## AddPlaylist
elif mode[0] == "addPlaylist":
    log('Mode is addPlaylist')
    #Display the videos of this playlistID
    id = args['id'][0]
    xml_add_playlist(id)
    editPlaylist(id) #Load the view to edit this playlist
    xbmcplugin.endOfDirectory(addon_handle)
## RemovePlaylist
elif mode[0] == "deletePlaylist":
    log('Mode is deletePlaylist')
    #Remove this playlist
    id = args['id'][0]
    delete_playlist(id) #Remove this playlist
    xbmcplugin.endOfDirectory(addon_handle)
## RefreshPlaylist
elif mode[0] == "refreshPlaylist":
    log('Mode is refreshPlaylist')
    #Refresh this playlist
    id = args['id'][0]
    refresh_playlist(id) #Remove this playlist
    xbmcplugin.endOfDirectory(addon_handle)
## editPlaylist
elif mode[0] == "editPlaylist":
    log('Mode is editPlaylist')
    #Check if we should set a value to..
    id = args['id'][0]
    set = args.get('set', None)
    if set != None:
        set = set[0]
        #We should set a value
        setEditPlaylist(id, set)
    #Display the videos of this playlistID
    editPlaylist(id)
    xbmcplugin.endOfDirectory(addon_handle)


## Update all playlists
elif mode[0] == 'updateplaylists':
    log('Mode is updateplaylists')
    update_playlists() #Update all playlists
    
    url = build_url({'home': 'home'})
    adddir('All playlists are now up to date', url, description = 'All playlists have been updated. Press this button to return home')
    xbmcplugin.endOfDirectory(addon_handle)    
    
## STRM TEST
elif mode[0] == "strmtest":
    log('Mode is strm test')
    id = args['id'][0] #Grab the playlist id which we should be updating
    update_playlist(id) #Update the nfo & strm files for this playlist
        
    url = build_url({'home': 'home'})
    adddir('Done building strms', url, description = 'Done building all strm files. Press this button to return home')
    xbmcplugin.endOfDirectory(addon_handle)

## SERVICE
elif mode[0] == "service":
    log('SERVICE started updates again in % hours' % service_interval)
    import time

    update_playlists()
    
    monitor = xbmc.Monitor()
    #service_interval = xbmcplugin.getSetting(addon_handle, 'service_interval')
    xbmcgui.Dialog().ok('Service started', 'Service started will run again in %s hours' % service_interval)
    
    while True:
        # Sleep/wait for abort for number of hours that is set in the addon settings
        if monitor.waitForAbort(service_interval*60*60):
        #if monitor.waitForAbort(5*60):
            # Abort was requested while waiting. We should exit
            break
        log("SERVICE is running..! will update again in %s hours" % service_interval)
        update_playlists()
    log("Kodi not running anymore, Service terminated")
    
    
    
    
## XML TESTS
elif mode[0] == "xmlcreate":
    log('Mode is xmlcreate')
    #Test the lxml module for writing xml and stuff
    create_xml()
    url = build_url({'mode': 'xmlcreate', 'foldername': 'xmlcreate'})
    adddir('XML Create Test', url)
    xbmcplugin.endOfDirectory(addon_handle)
    
    
## DELETE TESTS
elif mode[0] == "deletetest":
    #success = xbmcvfs.rmdir('C:/Users/Mich/AppData/Roaming/Kodi/userdata/addon_data/plugin.video.youtubelibrary/Streams/R_mi GAILLARD') #Remove the directory
    #success = xbmcvfs.rmtree('C:/Users/Mich/AppData/Roaming/Kodi/userdata/addon_data/plugin.video.youtubelibrary/Streams/R_mi GAILLARD/') #Remove the directory
    success = shutil.rmtree('C:/Users/Mich/AppData/Roaming/Kodi/userdata/addon_data/plugin.video.youtubelibrary/Streams/R_mi GAILLARD/', ignore_errors=True) #Remove the directory
    if success:
        xbmcgui.Dialog().ok('Removed from library', 'Deleted this show from your library')
    url = build_url({'mode': 'deletetest', 'foldername': 'deletetest'})
    adddir('Delete test', url)
    xbmcplugin.endOfDirectory(addon_handle)
  
    
    
    
    
    
    
    
        # ## Folder One
    # if foldername == 'Folder One':
        # #Grab Video Info
        # v = pafy.new("sdBLSTSN1HI")
        
        # #foldername = args['foldername'][0]
        # #url = 'plugin://plugin.video.youtube/play/?video_id=sdBLSTSN1HI'
        # url = v.getbest().url
        # additem(v.title, url, v.thumb)
        # xbmcplugin.endOfDirectory(addon_handle)
    # #Which folder should be loaded?
    # ## Youtube Plugin Test
    # elif foldername == 'Youtube Plugin Test':
        
        # xbmc.log(LPREF+'Running Youtube Plugin')
        # xbmc.executebuiltin('RunPlugin(plugin://plugin.video.youtube/?id=sdBLSTSN1HI)')
    # ## See All
    # elif foldername == 'See All':
        # #Show all videos from the youtube playlist
        # plurl = "https://youtu.be/hyZnd_2JYuM?list=UUSc16oMxxlcJSb9SXkjwMjA"
        # plurl = "https://www.youtube.com/watch?v=mOYZaiDZ7BM&list=RD0rNa8EObKJ0&index=2&spfreload=1"
        # playlist = pafy.get_playlist(plurl)
        
        # playlist['title']
        
        # for item in playlist['items']:
            # i = item['pafy']
            # additem(i.title, 'http://somevid.mkv', i.thumb)
        
        # xbmcplugin.endOfDirectory(addon_handle)
    # ## Cat
    # elif foldername == 'Cat':
        # search_by_keyword('cat')
        # xbmcplugin.endOfDirectory(addon_handle)
    # ## StukTV
    # elif foldername == 'StukTV':
        # library_movie_strm('Testing', 'Test', 'IDTEST')
        # write_settings()
        # vids_by_playlist('UUK5Fn7Z6-iFMdxEye2FsKXg')
        # xbmcplugin.endOfDirectory(addon_handle)
    # ## Readsettings
    # elif foldername == 'readsettings':
        # #read_settings()
        # update_settings()
    # ## DisplayChannels
    # elif foldername == 'displaychannels':
        # display_channels()
    # ## Search
    # elif foldername == 'search':
        # result = GUIEditExportName('YourMovieSucksDotOrg')
        # if len(result) > 0:
            # search_by_keyword(result)
        # xbmcplugin.endOfDirectory(addon_handle)