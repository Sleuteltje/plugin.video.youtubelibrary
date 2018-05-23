#import xbmc, xbmcgui, xbmcaddon



import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement





def playlist_xml_get(playlist, type=''):
    #dev.log('playlist_XML_get('+type+')')
    #if xbmcvfs.exists(os.path.join(vars.settingsPath,dev.typeEpnr(type)+"/"+playlist+".xml")) == False: #If the episodes.xml file can't be found, we should create this file
    #    playlist_create_xml(playlist, type=type)
    
    settingsPath='C:\\Users\\Brian\\AppData\\Roaming\\kodi\\userdata\\addon_data\\plugin.video.youtubelibrary\\Settings\\episodenr\\'
    global playlistdocument #Set the document variable as global, so every function can reach it
    playlistdocument = ElementTree.parse( settingsPath+playlist+'.xml' )
    return playlistdocument

def typeXml(type):
    if(type == 'musicvideo'):
        return 'settings_musicvideo.xml'
    elif(type == 'music'):
        return 'settings_music.xml'
    elif(type == 'movies'):
        return 'settings_movies.xml'
    else:
        return 'settings.xml'

def xml_get(type=''):
    file=typeXml(type)
    settingsPath='C:\\Users\\Brian\\AppData\\Roaming\\kodi\\userdata\\addon_data\\plugin.video.youtubelibrary\\Settings\\'
    global document #Set the document variable as global, so every function can reach it
    try:
        document = ElementTree.parse( settingsPath+file )
    except Exception:
        raise ValueError(output_file+' got corrupted! Best to quit here')
        return False
    return document

def xml_get_elem(path, tag, whereAttrib=False, whereTxt=False, playlist=False, type=''):    
    if playlist == False:
        xml_get(type) # Grab the xml file
        doc = document
    else:
        doc = playlist_xml_get(playlist, type=type) #Grab the episodes.xml file of this playlist
    
    for child in doc.findall(path):
        check = True # Use this var to check if this element meets all requirements. Set it by default to true, so it can be set to False if it fails some requirement
        #Check if this element has the tag we are looking for
        if child.tag == tag:
            #Should we also check that the element has a certain attribute with a certain value?
            if whereAttrib != False:
                # Check if this element meets all the requirements of the attributes
                for key, value in whereAttrib.items():
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

def legal_filename(filename):
    import re
    #return re.sub('[^\w\-_\. ]', '_', filename)
    #return slugify(filename) #Use the slugify function to get a valid filename (with utf8 characters)
    return re.sub(r'[/\\:*?"<>|&]', '', filename)

#Gets the tags from the settings and converts it to xml for the .nfo file        
def get_tags_xml(settings):
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
    return tags_xml

def write_tvshow_nfo(fold, settings):
    name = 'tvshow'
    movieLibrary = "C:\\Users\\Brian\\AppData\\Roaming\\kodi\\userdata\\addon_data\\plugin.video.youtubelibrary\\Streams\\TV\\"

    #Grab the published date and convert it to a normal date
    #d = ytube.convert_published(settings.find('published').text)
    #normaldate = d['year']+'-'+d['month']+'-'+d['day']
    
    #Grab the tags and convert them to xml
    tags_xml = get_tags_xml(settings)
    
    #Create the contents of the xml file
    content = u"""
            <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
            <tvshow>
                <title>%(title)s</title>
                <showtitle>%(title)s</showtitle>
                <plot>%(plot)s</plot>
                <genre>%(genre)s</genre>
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
        'genre': settings.find('genre').text,
        'studio': settings.find('channel').text,
        'thumb': settings.find('thumb').text,
        'banner': settings.find('banner').text,
        'fanart': settings.find('fanart').text,
        'tags': tags_xml,
    }
    
    #xbmcvfs.mkdir(movieLibrary) #Create the maindirectory if it does not exists yet
    enc_name = legal_filename(name) #Set the filename to a legal filename
    folder = os.path.join(movieLibrary, fold) #Set the folder to the maindir/dir
    #xbmcvfs.mkdir(folder) #Create this subfolder if it does not exist yet
    stream = os.path.join(folder, enc_name + '.nfo') #Set the file to maindir/name/name.strm
    
    #import codecs
    # process Unicode text
    #with codecs.open(stream,'w',encoding='utf8') as f:
    #    f.write(content)
    #    f.close()
    #file = xbmcvfs.File(stream, 'w') #Open / create this file for writing
    #file.write(str(content.encode("utf-8"))) #Write the content in the file
    #file.close() #Close the file
    #dev.log('write_tvshow_nfo: Written tvshow.nfo file: '+fold+'/'+enc_name+'.nfo')
    
    #If the setting download_images is true, we should also download the images as actual files into the directory

#Writes the nfo & strm files for the given playlist
def update_playlist(id, type=''):
    
    validate_settings(id, type)
    
    #xbmc.log("TOFOF1 id:"+id+" type:"+type, level=xbmc.LOGNOTICE)
    settings = xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type) #Grab the xml settings for this playlist
    if settings is None:
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
            if type == '' or type == 'tv':
                write_tvshow_nfo(folder, settings)
        
        #if update_playlist_vids(id, folder, settings, type=type) == False:
        #    return False #something failed while updating the videos of the playlist

        settings.find('skipdescription').text

        return True

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
        
# Converts the elementtree element to prettified xml and stores it in the settings.xml file
def write_xml(elem, dir='', output='', type=''):
    if output == '':
        output = typeXml(type)
    
    settingsPath='C:\\Users\\Brian\\AppData\\Roaming\\kodi\\userdata\\addon_data\\plugin.video.youtubelibrary\\Settings\\'
    
    #Write these settings to a .xml file in the addonfolder
    output_file = os.path.join(settingsPath+dir, output) #Set the outputfile to settings.xml
    
    #Creating a backup of the .xml file (in case it gets corrupted)
    backupfile = os.path.join(settingsPath+dir, output+'.backup')
    
    
    indent( elem ) #Prettify the xml so its not on one line
    tree = ElementTree.ElementTree( elem ) #Convert the xml back to an element
    tree.write(output_file) #Save the XML in the settings file
    
        
def xml_update_playlist_setting(id, tag, newsetting, type=''):      
    #Grab this playlist from the xml file
    elem = xml_get_elem('playlists/playlist', 'playlist', {'id' : id}, type=type)    
    
    #Find the setting that needs to be changed
    setting = elem.find(tag)
    if setting == None:
        #Lets create it
        setting = Element(tag)
        setting.text = newsetting
        elem.append(setting)
        root = document.getroot()
        write_xml(root, type=type)
        return False
    else:
        setting.text = newsetting
        root = document.getroot()
        write_xml(root, type=type)
        return True   
   
# Builds and returns an playlist element that can be added to the playlist element
#options the options (attributes) of this playlist
def xml_create_playlist(options):    
    #       <playlist id="">
    attr = { 'id' : options['id'], 'enabled' : options['enabled'], 'scansince' : '' }
    elem = Element('playlist', attr)
    
    #               <settingname>setting</settingname>
    # Loop through all settings and set them accordingly
    for key, value in options['settings'].items():      #was iteritems py2, now items py3
        SubElement(elem, key).text = value
    
    return elem #Return this element

# DOING: Setting all the defaults, then making m_xml methods use them instead of hardcoding and copypasting.  --Tofof 2018-04    
def default_settings(type=''):
    default_settings = False
    # A default value of `None` means that the setting is ignored completely during validation
    # A default value of '' means that the setting will be handled during validation and will default to an empty element (<somesetting />)
    if type=='' or type=='tv':    
        default_settings = {
            'type'              : 'TV',    
            'title'             : None,
            'channel'           : None,
            'channelId'         : None,
            'description'       : None,
            'genre'             : dev.getAddonSetting("default_genre", ''),
            'tags'              : dev.getAddonSetting("default_tags", 'Youtube'),
            'published'         : None,
            #Art
            'thumb'             : None,
            'fanart'            : None,
            'banner'            : None,
            'epsownfanart'      : 'No',     #uppercase in m_xml    # QUESTION: Should this setting be removed, since it isn't actually used anywhere?  --Tofof 2018-04
            # STRM & NFO Settings
            'writenfo'          : "no" if dev.getAddonSetting("default_generate_nfo") == "false" else "Yes",    # QUESTION: Why is this converting between 'Yes/no' and 'true/false'? Also note mixed capitalizations. See original in m_xml.xml_build_new_playlist() --Tofof 2018-04
            'delete'            : '',
            'updateevery'       : dev.getAddonSetting("default_updateevery", 'every 12 hours'),
            'updateat'          : dev.getAddonSetting("default_updateat", '23:59'),
            'update_gmt'        : dev.getAddonSetting("default_update_gmt", '99'),
            'onlygrab'          : dev.getAddonSetting("default_onlygrab", ''),
            'keepvideos'        : '',
            'overwritefolder'   : '',
            #Filters      
            'minlength'         : dev.getAddonSetting("default_minlength", ''),    
            'maxlength'         : dev.getAddonSetting("default_maxlength", ''),
            'excludewords'      : dev.getAddonSetting("default_excludewords", ''),
            'onlyinclude'       : dev.getAddonSetting("default_onlyinclude", ''),
            #NFO information
            'season'            : dev.getAddonSetting("default_season", 'year'),
            'episode'           : dev.getAddonSetting("default_episode", 'default'),
            'striptitle'        : dev.getAddonSetting("default_striptitle", ''),
            'removetitle'       : dev.getAddonSetting("default_removetitle", ''),
            'skiptitle'         : dev.getAddonSetting("default_skiptitle", ''),
            'stripdescription'  : dev.getAddonSetting("default_stripdescription", ''),
            'removedescription' : dev.getAddonSetting("default_removedescription", ''),
            'skipdescription'   : dev.getAddonSetting("default_skipdescription", ''),
            #Scan Settings
            'lastvideoId'       : '',
            'reverse'           : '0',
            'download_videos'   : dev.getAddonSetting("default_download_videos", '0'),
        }
    elif type=='movies':
       default_settings = {
            'type'              : 'movies',    
            'title'             : None,
            'channel'           : None,
            'channelId'         : None,
            'description'       : None,
            'genre'             : dev.getAddonSetting("default_movies_genre", ''),
            'tags'              : dev.getAddonSetting("default_movies_tags", 'Youtube'),
            'set'               : dev.getAddonSetting("default_movies_set", ''),
            'published'         : None,
            #Art
            'thumb'             : None,
            'fanart'            : None,
            'banner'            : None,
            'epsownfanart'      : 'No',         # QUESTION: (As above) Should this be removed?  --Tofof 2018-05
            # STRM & NFO Settings
            'writenfo'          : "no" if dev.getAddonSetting("default_movies_generate_nfo") == "false" else "Yes",    # QUESTION: (as above) Why is this converting between 'yes/no' and 'true/false'? --Tofof 2018-05
            'delete'            : '',
            'updateevery'       : dev.getAddonSetting("default_movies_updateevery", 'every 12 hours'),
            'updateat'          : dev.getAddonSetting("default_movies_updateat", '23:59'),
            'update_gmt'        : dev.getAddonSetting("default_movies_update_gmt", '99'),
            'onlygrab'          : dev.getAddonSetting("default_movies_onlygrab", ''),
            'keepvideos'        : '',
            'overwritefolder'   : '',
            #Filters      
            'minlength'         : dev.getAddonSetting("default_movies_minlength", ''),    
            'maxlength'         : dev.getAddonSetting("default_movies_maxlength", ''),
            'excludewords'      : dev.getAddonSetting("default_movies_excludewords", ''),
            'onlyinclude'       : dev.getAddonSetting("default_movies_onlyinclude", ''),
            #NFO information
            'search_imdb'       : dev.getAddonSetting("default_movies_search_imdb", '2'),
            'imdb_match_cutoff' : dev.getAddonSetting("default_movies_imdb_match_cutoff", '0.75')
            'use_ytimage'       : dev.getAddonSetting("default_movies_use_ytimage", '0')
            'smart_search'      : dev.getAddonSetting("default_movies_smart_search", '1')
            'striptitle'        : dev.getAddonSetting("default_movies_striptitle", ''),
            'removetitle'       : dev.getAddonSetting("default_movies_removetitle", ''),
            'skiptitle'         : dev.getAddonSetting("default_movies_skiptitle", ''),
            'stripdescription'  : dev.getAddonSetting("default_movies_stripdescription", ''),
            'removedescription' : dev.getAddonSetting("default_movies_removedescription", ''),
            'skipdescription'   : dev.getAddonSetting("default_movies_skipdescription", ''),
            #Scan Settings
            'lastvideoId'       : '',
            'reverse'           : '0',
            'download_videos'   : dev.getAddonSetting("default_movies_download_videos", '0'),
            }
    elif type=='musicvideo':
        default_settings = {
            'type'              : 'MusicVideo',
            'title'             : None,
            'channel'           : None,
            'channelId'         : None,
            'description'       : None,
            'published'         : None,
            #Library Info
            'tags'              : dev.getAddonSetting("default_musicvideo_tags", 'Youtube'),
            'genre'             : dev.getAddonSetting("default_musicvideo_genre", '')
            'genre_fallback'    : dev.getAddonSetting("default_musicvideo_genre_fallback", ''),
            'genre_hardcoded'   : dev.getAddonSetting("default_musicvideo_genre_hardcoded", ''),
            'artist'            : dev.getAddonSetting("default_musicvideo_artist", ''),
            'artist_fallback'   : dev.getAddonSetting("default_musicvideo_artist_fallback", ''),
            'artist_hardcoded'  : dev.getAddonSetting("default_musicvideo_artist_hardcoded", ''),
            'song_fallback'     : dev.getAddonSetting("default_musicvideo_song_fallback", ''),
            'album'             : dev.getAddonSetting("default_musicvideo_album", ''),
            'album_fallback'    : dev.getAddonSetting("default_musicvideo_album_fallback", ''),
            'album_hardcoded'   : dev.getAddonSetting("default_musicvideo_album_hardcoded", ''),
            'plot'              : dev.getAddonSetting("default_musicvideo_plot", ''),
            'plot_fallback'     : dev.getAddonSetting("default_musicvideo_plot_fallback", ''),
            'plot_hardcoded'    : dev.getAddonSetting("default_musicvideo_plot_hardcoded", ''),
            'year'              : dev.getAddonSetting("default_musicvideo_year", '')
            'year_fallback'     : dev.getAddonSetting("default_musicvideo_year_fallback", ''),
            'year_hardcoded'    : dev.getAddonSetting("default_musicvideo_year_hardcoded", ''),
            #Art
            'thumb'             : None,
            'fanart'            : None,
            'banner'            : None,
            # STRM & NFO Settings
            'writenfo'          : "no" if dev.getAddonSetting("default_musicvideo_generate_nfo") == "false" else "Yes",    # QUESTION: (as above) Why is this converting between 'yes/no' and 'true/false'? --Tofof 2018-05
            'updateevery'       : dev.getAddonSetting("default_musicvideo_updateevery", 'every 12 hours'),
            'updateat'          : dev.getAddonSetting("default_musicvideo_updateat", '23:59'),
            'update_gmt'        : dev.getAddonSetting("default_musicvideo_update_gmt", '99'),
            'onlygrab'          : dev.getAddonSetting("default_musicvideo_onlygrab", ''),
            'delete'            : '',
            'keepvideos'        : '',
            'overwritefolder'   : '',
            #Filters
            'minlength'         : dev.getAddonSetting("default_musicvideo_minlength", ''),
            'maxlength'         : dev.getAddonSetting("default_musicvideo_maxlength", ''),
            'excludewords'      : dev.getAddonSetting("default_musicvideo_excludewords", ''),
            'onlyinclude'       : dev.getAddonSetting("default_musicvideo_onlyinclude", ''),
            #Skip
            'skip_audio'        : dev.getAddonSetting("default_musicvideo_skip_audio", 'false'),
            'skip_lyrics'       : dev.getAddonSetting("default_musicvideo_skip_lyrics", 'false'),
            'skip_live'         : dev.getAddonSetting("default_musicvideo_skip_live", 'false'),
            'skip_albums'       : dev.getAddonSetting("default_musicvideo_skip_albums", 'false'),
            #NFO information
            'striptitle'        : dev.getAddonSetting("default_musicvideo_striptitle", ''),
            'removetitle'       : dev.getAddonSetting("default_musicvideo_removetitle", ''),
            'skiptitle'         : dev.getAddonSetting("default_musicvideo_skiptitle", ''),
            'stripdescription'  : dev.getAddonSetting("default_musicvideo_stripdescription", ''),
            'removedescription' : dev.getAddonSetting("default_musicvideo_removedescription", ''),
            'skipdescription'   : dev.getAddonSetting("default_musicvideo_skipdescription", ''),
            #Scan Settings
            'lastvideoId'       : '',
            'reverse'           : '',           # QUESTION: Is there a reason this isn't '0' like the other two?  --Tofof 2018-05
            'download_videos'   : dev.getAddonSetting("default_musicvideo_download_videos", '0'),       # Note: Was 'default_download_videos' in m_xml, expect this was a copy/paste bug  --Tofof 2018-05
        }
    return default_settings

def validate_settings(id, type=''):
    settings = xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type) #Grab the xml settings for this playlist
    if settings is None:
        return False
    else:       
        for default_key, default_value in default_settings(type).items():      #was iteritems py2, now items py3
            setting = settings.find(default_key)
            if setting is None:
                if default_value is None:
                    #print("IGNORING", default_key)
                    pass
                else:
                    #print("UPDATING", default_key, "FROM", setting, "TO", "'"+default_value+"'", "FOR PLAYLIST ID", id)
                    xml_update_playlist_setting(id, default_key, default_value, type)
            else:
                #print(default_key+':', setting.text)
                pass
    return True
        
update_playlist('PLTur7oukosPFINuomVBIGR-UlHWpN5KIk')



"""
      <overwritefolder />
      <stripdescription>Join FIRST|merch:|Subscribe:|&#187;|Watch our other|bit.ly|pre-order|twitter|Hunter:|Play:|watch me|revolving cast|submit your own|http|Get your Achieve</stripdescription>
      <excludewords />
      <onlyinclude />
      <thumb>https://yt3.ggpht.com/--LriGZRRpiw/AAAAAAAAAAI/AAAAAAAAAAA/ttVIfJrhhSo/s800-c-k-no-mo-rj-c0xffffff/photo.jpg</thumb>
      <title>Achievement Hunter - Play Pals</title>
      <fanart>https://yt3.ggpht.com/-iSMcQT9uR3A/VYmqCtUQQzI/AAAAAAAAAGg/eReqhlJsh1A/w2120-fcrop64=1,00000000ffffffff-nd/ah_channel_header.jpg</fanart>
      <minlength />
      <removedescription />
      <writenfo>Yes</writenfo>
      <striptitle />
      <updateat>16:30</updateat>
      <channel>Achievement Hunter</channel>
      <description>Play Pals -- got two pals, playing games and having fun. Having a good time because they're pals. Thanks for watching Play Pals!</description>
      <tags>Youtube</tags>
      <season>year</season>
      <updateevery>every 24 hours</updateevery>
      <genre>gaming</genre>
      <banner>https://yt3.ggpht.com/-iSMcQT9uR3A/VYmqCtUQQzI/AAAAAAAAAGg/eReqhlJsh1A/w1060-fcrop64=1,00005a57ffffa5a8-nd/ah_channel_header.jpg</banner>
      <lastvideoId>101</lastvideoId>
      <episode>default</episode>
      <removetitle> \| Rooster Teeth</removetitle>
      <onlygrab>10000</onlygrab>
      <type>TV</type>
      <maxlength />
      <keepvideos />
      <delete />
      <epsownfanart>No</epsownfanart>
      <published>2008-04-18T15:52:09.000Z</published>
      <reverse>1</reverse>
      <skiptitle>Pals - </skiptitle>
"""


"""
<Element 'playlist' at 0x0542AEA0>
    <Element 'overwritefolder' at 0x0542AED0>
    <Element 'stripdescription' at 0x0537A0F0>
    <Element 'excludewords' at 0x0537A060>
    <Element 'onlyinclude' at 0x0537A090>
    <Element 'thumb' at 0x0537A030>
    <Element 'title' at 0x05412C90>
    <Element 'fanart' at 0x05412C30>
    <Element 'minlength' at 0x05383FC0>
    <Element 'removedescription' at 0x05383F30>
    <Element 'writenfo' at 0x05383F00>
    <Element 'striptitle' at 0x05383EA0>
    <Element 'updateat' at 0x05383E70>
    <Element 'channel' at 0x05383CC0>
    <Element 'description' at 0x05383C30>
    <Element 'tags' at 0x05383C60>
    <Element 'season' at 0x05383E40>
    <Element 'updateevery' at 0x05383DB0>
    <Element 'genre' at 0x05383E10>
    <Element 'banner' at 0x05383D20>
    <Element 'lastvideoId' at 0x05383C00>
    <Element 'episode' at 0x05383C90>
    <Element 'removetitle' at 0x05383BD0>
    <Element 'onlygrab' at 0x05383B10>
    <Element 'type' at 0x05383AB0>
    <Element 'maxlength' at 0x05383AE0>
    <Element 'keepvideos' at 0x05383A50>
    <Element 'delete' at 0x053839F0>
    <Element 'epsownfanart' at 0x05383990>
    <Element 'published' at 0x0542AF00>
    <Element 'reverse' at 0x0542AF30>
    <Element 'skiptitle' at 0x0542AF60>
"""