#    Kodi Addon: Youtube Library
#    Copyright 2015 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions to handle xml files
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
#For XML Reading & Writing
import xbmcvfs
import xbmcgui
import os

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
# For prettyfing the XML
from xml.dom import minidom

from resources.lib import dev
from resources.lib import vars
from resources.lib import ytube

document = ''
playlistdocument = ''

#Loads the xml document        
#file: The file to load (default: settings.xml) use settings_musicvideos.xml for musicvideos
def xml_get(type=''):
    file=dev.typeXml(type)
    dev.log('XML_get('+type+','+file+')')
    global document #Set the document variable as global, so every function can reach it
    try:
        document = ElementTree.parse( vars.settingsPath+file )
    except Exception:
        xbmcgui.Dialog().ok("ERROR: "+file+" got corrupted", "ERROR!: "+file+" got corrupted. Please report this error to the addon developer on youtubelibrary.nl or the kodi forums. Luckily a backup has been created automatically before.")
        dev.log('ERROR: '+file+' got corrupted.', 1)
        raise ValueError(output_file+' got corrupted! Best to quit here')
        return False
    return document
    
    
# Converts the elementtree element to prettified xml and stores it in the settings.xml file
def write_xml(elem, dir='', output='', type=''):
    if output == '':
        output = dev.typeXml(type)
    dev.log('write_xml('+type+','+output+').')
    
    
    xbmcvfs.mkdir(vars.settingsPath) #Create the settings dir if it does not exist already
    if dir is not '': xbmcvfs.mkdir(vars.settingsPath+dir) #Create the settings dir if it does not exist already
    #Write these settings to a .xml file in the addonfolder
    output_file = os.path.join(vars.settingsPath+dir, output) #Set the outputfile to settings.xml
    
    #Creating a backup of the .xml file (in case it gets corrupted)
    backupfile = os.path.join(vars.settingsPath+dir, output+'.backup')
    if xbmcvfs.exists(output_file):
        if xbmcvfs.copy(output_file, backupfile):
            dev.log('Created a backup of the xml file at: '+backupfile)
        else:
            dev.log('Failed to create a backup of the xml file at: '+backupfile)
    else:
        dev.log(output_file+' could not be found, so not able to create a backup')
    
    
    indent( elem ) #Prettify the xml so its not on one line
    tree = ElementTree.ElementTree( elem ) #Convert the xml back to an element
    tree.write(output_file) #Save the XML in the settings file
    
    #For backup purposes, check if the xml got corrupted by writing just now
    if xml_get(type) is False:
        dev.log('corrupt .xml file')
    

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
def create_xml(file='settings.xml'):
    dev.log('Create_xml')
    
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
    write_xml(root, output=file)
    dev.log('Create_xml: Created new '+file+' file')

# Builds and returns an playlist element that can be added to the playlist element
#options the options (attributes) of this playlist
def xml_create_playlist(options):    
    #       <playlist id="">
    attr = { 'id' : options['id'], 'enabled' : options['enabled'], 'scansince' : '' }
    elem = Element('playlist', attr)
    
    #               <settingname>setting</settingname>
    # Loop through all settings and set them accordingly
    for key, value in options['settings'].iteritems():
        SubElement(elem, key).text = value
    
    return elem #Return this element

    

    

    
#Deletes a playlist from the xml and saves it
#type: tv (''), musicvideo, music, movie
def xml_remove_playlist(id, type=''):
    dev.log('XML_remove_playlist('+id+')')
    pl = xml_get_elem('playlists/playlist', 'playlist', {'id': id}, type=type)
    if pl is not None:
        dev.log('Found the playlist to delete')
        
        root = document.getroot()
        parent = root.find('playlists')
        parent.remove(pl)
        write_xml(root, type=type)
        dev.log('XML_remove_playlist: Removed playlist '+id+' ('+dev.typeXml(type)+')', 8)
        return True
    else:
        return False
       
    
#Adds the playlist to the xml if it does not exist yet, and retrieves information about the playlist
#type:
#   tv ('')
#   musicvideo
#   music
#   movies
def xml_add_playlist(id, type='', api=''):
    dev.log('XML_add_playlist('+id+')')
    #Check if this playlist isnt in the xml file yet
    if xml_get_elem('playlists/playlist', 'playlist', {'id' : id}, type=type) is None:
        #Create the playlist according to its type & if its from the api
        if api == '':
            playlist = xml_build_new_playlist(id, type)
        else:
            playlist = api_xml_build_new_playlist(api, type)

        pl = xml_create_playlist(playlist)
        root = document.getroot()
        root[0].insert(0, pl)
        write_xml(root, type=type)
        dev.log('Added the playlist '+id+' to the '+type+' .xml', 1)
    else:
        dev.log('XML_add_playlist: not added playlist '+id+' ('+type+') since the playlist already exists', 2)    
    

def api_xml_build_new_playlist(api, type=''):
    #### Build new playlist (tv, musicvideo, movies) ###
    #Build the playlist
    playlist = {
        'id'    : api['ytplaylistid'],
        'enabled'      : 'yes',
        'settings'      : {
            'title'                   : api['title'],
            'channel'            : api['channel'],
            'channelId'            : api['channelId'],
            'description'        : api['description'],
            'genre'                : api['genre'],
            'tags'                  : api['tags'],
            'published'          : api['published'],
            'reverse'            : api['reverse'],
            #Art
            'thumb'               : api['thumb'],
            'fanart'                : api['fanart'],
            'banner'              : api['banner'],
            'epsownfanart'    : 'No',
            # STRM & NFO Settings
            'writenfo'             : api['writenfo'],
            'delete'                : api['delete'],
            'updateevery'       : api['updateevery'],
            'updateat'        : api['updateat'],
            'update_gmt'        : api['update_gmt'],
            'onlygrab'          : dev.getAddonSetting("default_onlygrab", ''),
            'keepvideos'        : api['keepvideos'],
            'overwritefolder'   : api['overwritefolder'],
            #Filters
            'minlength'         : api['minlength'],
            'maxlength'         : api['maxlength'],
            'excludewords'    : api['excludewords'],
            'onlyinclude'       : api['onlyinclude'],
            #NFO information
            'striptitle'        : api['striptitle'],
            'removetitle'       : api['removetitle'],
            'stripdescription' : api['stripdescription'],
            'removedescription' : api['removedescription'],
            #Scan Settings
            'lastvideoId'       : '',
        }
    }
    
    if type=='' or type=='tv':
        settings = {
                'season'            : api['season'],
                'episode'           : api['episode'],
        }
        playlist['settings'].update(settings)
        return playlist
    elif type=='musicvideo':
        settings = {
                'skip_albums'                    : api['skip_albums'],
                'skip_lyrics'           : api['skip_lyrics'],
                'skip_audio'                    : api['skip_audio'],
                'skip_live'           : api['skip_live'],

                'genre_hardcoded'                    : api['genre_hardcoded'],
                'genre_fallback'           : api['genre_fallback'],

                'plot'                    : api['plot'],
                'plot_fallback'           : api['plot_fallback'],
                'plot_hardcoded'           : api['plot_hardcoded'],
                
                'artist'                    : api['artist'],
                'artist_fallback'           : api['artist_fallback'],
                'artist_hardcoded'           : api['artist_hardcoded'],
                
                'song_fallback'           : api['song_fallback'],
                
                'year'                      : api['year'],
                'year_fallback'           : api['year_fallback'],
                'year_hardcoded'           : api['year_hardcoded'],
                
                'album'                     : api['album'],
                'album_fallback'           : api['album_fallback'],
                'album_hardcoded'           : api['album_hardcoded'],
        }
        playlist['settings'].update(settings)
        return playlist
    elif type=='movies':
        settings = {
                'set'            : api['set'],
                'search_imdb'           : api['search_imdb'],
                'use_ytimage'           : api['use_ytimage'],
                'imdb_match_cutoff'           : api['imdb_match_cutoff'],
                'smart_search'           : api['smart_search'],
        }
        playlist['settings'].update(settings)
        return playlist
    return False
    
def xml_build_new_playlist(id, type=''):
    response = ytube.yt_get_playlist_info(id)
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
        dev.log('The thumbnail: '+thumbnail)
        
    #Grab the channel information 
    response = ytube.yt_get_channel_info(res['channelId'])
    snippet = response['items'][0]['snippet']
    brand = response['items'][0]['brandingSettings']
    #Check if we should do a better thumbnail
    #if thumbnail is False:
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
    dev.log('The thumbnail now: '+thumbnail)
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
    
    bannerTv = brand['image']['bannerImageUrl']
    if 'bannerTvImageUrl' in brand['image']:
        bannerTv = brand['image']['bannerTvImageUrl']


    #### Build new playlist (tv, musicvideo) ###
    if type=='' or type=='tv':
        ##Get the default settings from the addon settings
        writenfo = 'Yes'
        if dev.getAddonSetting("default_generate_nfo") == "false":
            writenfo = 'no'
        genre = dev.getAddonSetting("default_genre", '')
        tags = dev.getAddonSetting("default_tags", 'Youtube')
        season = dev.getAddonSetting("default_season", 'year')
        episode = dev.getAddonSetting("default_episode", 'default')
        minlength = dev.getAddonSetting("default_minlength", '')
        maxlength = dev.getAddonSetting("default_maxlength", '')
        onlyinclude = dev.getAddonSetting("default_onlyinclude", '')
        excludewords = dev.getAddonSetting("default_excludewords", '')
        stripdescription = dev.getAddonSetting("default_stripdescription", '')
        removedescription = dev.getAddonSetting("default_removedescription", '')
        striptitle = dev.getAddonSetting("default_striptitle", '')
        removetitle = dev.getAddonSetting("default_removetitle", '')
        updateevery = dev.getAddonSetting("default_updateevery", 'every 12 hours')
        updateat = dev.getAddonSetting("default_updateat", '23:59')
        update_gmt = dev.getAddonSetting("default_update_gmt", '99')
        
        
        #Build the playlist
        playlist = {
            'id'    : id,
            'enabled'      : 'no',
            'settings'      : {
                'type'                  : 'TV',
                'title'                   : title,
                'channel'            : snippet['title'],
                'channelId' : res['channelId'],
                'description'        : description,
                'genre'                : genre,
                'tags'                  : tags,
                'published'          : snippet['publishedAt'],
                #Art
                'thumb'               : thumbnail,
                'fanart'                : bannerTv,
                'banner'              : brand['image']['bannerImageUrl'],
                'epsownfanart'    : 'No',
                # STRM & NFO Settings
                'writenfo'             : writenfo,
                'delete'                : '',
                'updateevery'       : updateevery,
                'updateat'        : updateat,
                'update_gmt'        : update_gmt,
                'onlygrab'          : dev.getAddonSetting("default_onlygrab", ''),
                'keepvideos'        : '',
                'overwritefolder'   : '',
                #Filters
                'minlength'         : minlength,
                'maxlength'         : maxlength,
                'excludewords'    : excludewords,
                'onlyinclude'       : onlyinclude,
                #NFO information
                'season'            : season,
                'episode'           : episode,
                'striptitle'            : striptitle,
                'removetitle'       : removetitle,
                'stripdescription' : stripdescription,
                'removedescription' : removedescription,
                #Scan Settings
                'lastvideoId'       : '',
                'reverse'           : '0',
            }
        }
        return playlist
    elif type=='movies':
        ##Get the default settings from the addon settings
        writenfo = 'Yes'
        if dev.getAddonSetting("default_movies_generate_nfo") == "false":
            writenfo = 'no'
        genre = dev.getAddonSetting("default_movies_genre", '')
        tags = dev.getAddonSetting("default_movies_tags", 'Youtube')
        search_imdb = dev.getAddonSetting("default_movies_search_imdb", '2')
        imdb_match_cutoff = dev.getAddonSetting("default_movies_imdb_match_cutoff", '0.75')
        use_ytimage = dev.getAddonSetting("default_movies_use_ytimage", '0')
        minlength = dev.getAddonSetting("default_movies_minlength", '')
        maxlength = dev.getAddonSetting("default_movies_maxlength", '')
        onlyinclude = dev.getAddonSetting("default_movies_onlyinclude", '')
        excludewords = dev.getAddonSetting("default_movies_excludewords", '')
        stripdescription = dev.getAddonSetting("default_movies_stripdescription", '')
        removedescription = dev.getAddonSetting("default_movies_removedescription", '')
        striptitle = dev.getAddonSetting("default_movies_striptitle", '')
        removetitle = dev.getAddonSetting("default_movies_removetitle", '')
        updateevery = dev.getAddonSetting("default_movies_updateevery", 'every 12 hours')
        updateat = dev.getAddonSetting("default_movies_updateat", '23:59')
        update_gmt = dev.getAddonSetting("default_movies_update_gmt", '99')
        set = dev.getAddonSetting("default_movies_set", '')
        smart_search = dev.getAddonSetting("default_movies_smart_search", '1')
        
        
        #Build the playlist
        playlist = {
            'id'    : id,
            'enabled'      : 'no',
            'settings'      : {
                'type'                  : 'movies',
                'title'                   : title,
                'channel'            : snippet['title'],
                'channelId' : res['channelId'],
                'description'        : description,
                'genre'                : genre,
                'tags'                  : tags,
                'set'                   : set,
                'published'          : snippet['publishedAt'],
                #Art
                'thumb'               : thumbnail,
                'fanart'                : bannerTv,
                'banner'              : brand['image']['bannerImageUrl'],
                'epsownfanart'    : 'No',
                # STRM & NFO Settings
                'writenfo'             : writenfo,
                'delete'                : '',
                'updateevery'       : updateevery,
                'updateat'        : updateat,
                'update_gmt'        : update_gmt,
                'onlygrab'          : dev.getAddonSetting("default_movies_onlygrab", ''),
                'keepvideos'        : '',
                'overwritefolder'   : '',
                #Filters
                'minlength'         : minlength,
                'maxlength'         : maxlength,
                'excludewords'    : excludewords,
                'onlyinclude'       : onlyinclude,
                #NFO information
                'search_imdb'            : search_imdb,
                'imdb_match_cutoff'           : imdb_match_cutoff,
                'use_ytimage'           : use_ytimage,
                'smart_search'          : smart_search,
                'striptitle'            : striptitle,
                'removetitle'       : removetitle,
                'stripdescription' : stripdescription,
                'removedescription' : removedescription,
                #Scan Settings
                'lastvideoId'       : '',
                'reverse'           : ''
            }
        }
        return playlist
    if type=='musicvideo':
        ##Get the default settings from the addon settings
        writenfo = 'Yes'
        if dev.getAddonSetting("default_musicvideo_generate_nfo") == "false":
            writenfo = 'no'
        genre = dev.getAddonSetting("default_musicvideo_genre", '')
        genre_fallback = dev.getAddonSetting("default_musicvideo_genre_fallback", '')
        genre_hardcoded = dev.getAddonSetting("default_musicvideo_genre_hardcoded", '')
        
        artist = dev.getAddonSetting("default_musicvideo_artist", '')
        artist_fallback = dev.getAddonSetting("default_musicvideo_artist_fallback", '')
        artist_hardcoded = dev.getAddonSetting("default_musicvideo_artist_hardcoded", '')
        
        song_fallback = dev.getAddonSetting("default_musicvideo_song_fallback", '')
        
        album = dev.getAddonSetting("default_musicvideo_album", '')
        album_fallback = dev.getAddonSetting("default_musicvideo_album_fallback", '')
        album_hardcoded = dev.getAddonSetting("default_musicvideo_album_hardcoded", '')
        
        plot = dev.getAddonSetting("default_musicvideo_plot", '')
        plot_fallback = dev.getAddonSetting("default_musicvideo_plot_fallback", '')
        plot_hardcoded = dev.getAddonSetting("default_musicvideo_plot_hardcoded", '')
        
        year = dev.getAddonSetting("default_musicvideo_year", '')
        year_fallback = dev.getAddonSetting("default_musicvideo_year_fallback", '')
        year_hardcoded = dev.getAddonSetting("default_musicvideo_year_hardcoded", '')
        
        tags = dev.getAddonSetting("default_musicvideo_tags", 'Youtube')
        minlength = dev.getAddonSetting("default_musicvideo_minlength", '')
        maxlength = dev.getAddonSetting("default_musicvideo_maxlength", '')
        onlyinclude = dev.getAddonSetting("default_musicvideo_onlyinclude", '')
        excludewords = dev.getAddonSetting("default_musicvideo_excludewords", '')
        stripdescription = dev.getAddonSetting("default_musicvideo_stripdescription", '')
        removedescription = dev.getAddonSetting("default_musicvideo_removedescription", '')
        striptitle = dev.getAddonSetting("default_musicvideo_striptitle", '')
        removetitle = dev.getAddonSetting("default_musicvideo_removetitle", '')
        updateevery = dev.getAddonSetting("default_musicvideo_updateevery", 'every 12 hours')
        updateat = dev.getAddonSetting("default_musicvideo_updateat", '23:59')
        update_gmt = dev.getAddonSetting("default_musicvideo_update_gmt", '99')
        
        #Build the playlist
        playlist = {
            'id'    : id,
            'enabled'      : 'no',
            'settings'      : {
                'type'                  : 'MusicVideo',
                'title'                   : title,
                'channel'            : snippet['title'],
                'channelId' : res['channelId'],
                'description'        : description,
                'published'          : snippet['publishedAt'],
                #Library Info
                'tags'                  : tags,
                'genre'                : genre,
                'genre_fallback'        : genre_fallback,
                'genre_hardcoded'       : genre_hardcoded,
                'artist'                : artist,
                'artist_fallback'       : artist_fallback,
                'artist_hardcoded'       : artist_hardcoded,
                'song_fallback'         : song_fallback,
                'album'                 : album,
                'album_fallback'        : album_fallback,
                'album_hardcoded'       : album_hardcoded,
                'plot'                  : plot,
                'plot_fallback'         : plot_fallback,
                'plot_hardcoded'        : plot_hardcoded,
                'year'                  : year,
                'year_fallback'         : year_fallback,
                'year_hardcoded'        : year_hardcoded,
                #Art
                'thumb'               : thumbnail,
                'fanart'                : bannerTv,
                'banner'              : brand['image']['bannerImageUrl'],
                # STRM & NFO Settings
                'writenfo'             : writenfo,
                'updateevery'       : updateevery,
                'updateat'        : updateat,
                'update_gmt'        : update_gmt,
                'onlygrab'          : dev.getAddonSetting("default_musicvideo_onlygrab", ''),
                'delete'                : '',
                'keepvideos'        : '',
                'overwritefolder'   : '',
                #Filters
                'minlength'         : minlength,
                'maxlength'         : maxlength,
                'excludewords'    : excludewords,
                'onlyinclude'       : onlyinclude,
                #Skip
                'skip_audio'   : dev.getAddonSetting("default_musicvideo_skip_audio", 'false'),
                'skip_lyrics'   : dev.getAddonSetting("default_musicvideo_skip_lyrics", 'false'),
                'skip_live'     : dev.getAddonSetting("default_musicvideo_skip_live", 'false'),
                'skip_albums'   : dev.getAddonSetting("default_musicvideo_skip_albums", 'false'),
                #NFO information
                'striptitle'            : striptitle,
                'removetitle'       : removetitle,
                'stripdescription' : stripdescription,
                'removedescription' : removedescription,
                #Scan Settings
                'lastvideoId'       : '',
                'reverse'           : '',
            }
        }
        return playlist
    return False
    

# Updates a playlist that already exists
def xml_update_playlist_attr(id, attr, val, type=''):
    dev.log('XML: Updating playlist id '+id+' with attr '+attr+' : '+val+' ('+type+')')
    
    #Grab this playlist from the xml file
    playlist = xml_get_elem('playlists/playlist', 'playlist', {'id' : id}, type=type)
    
    #Check if we have succesfully retrieved the playlist
    if playlist == None:
        dev.log('XML_update_playlist: could not find playlist '+id)
    else:
        dev.log('XML_update_playlist_: found playlist '+id)
        
        
        #Update this attribute to the new val
        try: 
            del playlist.attrib[attr]  
        except: pass
        playlist.attrib[attr] = val
        #playlist.set(attr, val)
        #Write this to the xml
        root = document.getroot()
        write_xml(root, type=type)
        dev.log('XML_update_playlist_attr: written XML')
        
# Updates a playlist setting (like <age>)
def xml_update_playlist_setting(id, tag, newsetting, type=''):
    dev.log('XML_update_playlist_setting ('+id+', '+tag+', '+newsetting+', type='+type+')')
    
    #Grab this playlist from the xml file
    elem = xml_get_elem('playlists/playlist', 'playlist', {'id' : id}, type=type)
    
    #Check if we have succesfully retrieved the playlist
    if elem == None:
        dev.log('XML_update_playlist_setting: could not find playlist '+id)
        return False
    else:
        dev.log('XML_update_playlist_setting: found playlist '+id)
        
        #Find the setting that needs to be changed
        setting = elem.find(tag)
        if setting == None:
            #Could not find setting
            dev.log('XML_update_playlist_setting: could not find setting '+tag+' of '+id)
            #Lets create it
            setting = Element(tag)
            setting.text = newsetting
            elem.append(setting)
            root = document.getroot()
            write_xml(root, type=type)
            dev.log('XML_update_playlist_setting('+type+'): Created xml setting '+tag+' of '+id+' to '+newsetting)
            return False
        else:
            #Change the setting to its new setting
            setting.text = newsetting
            #Write this to the xml
            root = document.getroot()
            write_xml(root, type=type)
            dev.log('XML_update_playlist_setting('+type+'): Updated xml setting '+tag+' of '+id+' to '+newsetting)
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
        # playlist: The playlist id if we should grab a episodenr/playlist.xml instead of the settings.xml
        # type: The type of playlist we would like to select. tv (''), musicvideo, music, movies
def xml_get_elem(path, tag, whereAttrib=False, whereTxt=False, playlist=False, type=''):    
    dev.log('XML_get_elem('+type+')')
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

    
    
'''
    PLAYLIST EPISODENUMBERING 
'''
# Creates the episodes.xml file
def playlist_create_xml(playlist, type=''):
    dev.log('playlist_create_xml('+type+')')
    
    #<playlists>
    root = Element('seasons')
    #attr = { 'number' : season }
    #newxml = SubElement(root, 'season', attr)
    #attr = { 'id' : videoId}
    #elem = SubElement(newxml, 'episode', attr)
    
    #playlist = xml_create_playlist(example)
    #Append this playlist to the new created xml file
    #newxml.append(playlist)
    #Write this new xml to the settings.xml file
    write_xml(root, dev.typeEpnr(type), playlist+'.xml')
    dev.log('playlist_create_xml: Created new '+dev.typeEpnr(type)+'/'+playlist+'.xml')

#Loads the playlist episodes xml document
#type: tv (''), musicvideo, music, movies        
def playlist_xml_get(playlist, type=''):
    dev.log('playlist_XML_get('+type+')')
    if xbmcvfs.exists(os.path.join(vars.settingsPath,dev.typeEpnr(type)+"/"+playlist+".xml")) == False: #If the episodes.xml file can't be found, we should create this file
        playlist_create_xml(playlist, type=type)
    
    global playlistdocument #Set the document variable as global, so every function can reach it
    playlistdocument = ElementTree.parse( vars.settingsPath+dev.typeEpnr(type)+'/'+playlist+'.xml' )
    return playlistdocument


#Returns the number of episodes in a season
def number_of_episodes(playlist, season, season_tag='season', type=''):
    s = xml_get_elem(season_tag, season_tag, {'number': season}, playlist=playlist, type=type)
    if s == None:
        dev.log('number_of_episodes('+type+'): Could not find '+season_tag+' '+season+' in playlist '+playlist)
        return None
    dev.log('number_of_episodes('+type+'): Found '+str(len(s))+' episodes in '+season_tag+' '+season)
    return len(s)
    
#Does the episode already exist
def episode_exists(playlist, episode, season_tag='season', episode_tag='episode', type=''):
    dev.log('episode_exists('+playlist+', '+episode+', type='+type+')')
    #Quicker way to check if this episode already exists
    #doc = playlist_xml_get(playlist)
    #e = doc.findall("*/episode[@id='"+episode+"']")
    e = xml_get_elem(season_tag+'/'+episode_tag, episode_tag, {'id' : episode}, playlist=playlist, type=type)
    #if len(e) == 0:
    if e == None:
        dev.log(episode_tag+' '+episode+' is not yet present in '+dev.typeEpnr(type)+' file')
        return False
    dev.log('Already present: '+episode)
    return True



#Adds the playlist to the xml if it does not exist yet, and retrieves information about the playlist
def playlist_add_season(playlist, season, season_tag='season', type=''):
    dev.log('playlist_add_season('+season+')')
    #Check if this playlist isnt in the xml file yet
    #if xml_get_elem('season', 'episode', {'id' : id}, playlist=playlist) is None:
    #Build the playlist
    doc = playlist_xml_get(playlist, type=type)
    
    attr = { 'number' : season}
    elem = Element(season_tag, attr)
    root = doc.getroot()
    root.insert(0, elem)
    write_xml(root, dir=dev.typeEpnr(type), output=playlist+'.xml')
    dev.log('Added '+season_tag+': '+season+' in '+dev.typeEpnr(type)+'/'+playlist+'.xml')
    #else:
        #dev.log('playlist_add_episode: not added episode '+id+' since the episode already exists')    #Adds the playlist to the xml if it does not exist yet, and retrieves information about the playlist

def playlist_add_episode(playlist, season, id, season_tag='season', type=''):
    dev.log('playlist_add_episode('+season+','+id+', type='+type+')')
    #Check if this playlist isnt in the xml file yet
    #if xml_get_elem('season', 'episode', {'id' : id}, playlist=playlist) is None:
    #Build the playlist
    #doc = playlist_xml_get(playlist)
    
    #s = doc.find("season[@number='"+season+"']")
    s = xml_get_elem(season_tag, season_tag, {'number': season}, playlist=playlist, type=type)
    if s is None:
        playlist_add_season(playlist, season, type=type)
        #doc = playlist_xml_get(playlist)
        #s = doc.find("season[@number='"+season+"']")
        s = xml_get_elem(season_tag, season_tag, {'number': season}, playlist=playlist, type=type)
        
    #doc = playlist_xml_get(playlist)
    global playlistdocument
    attr = { 'id' : id}
    elem = Element('episode', attr)
    
    s.insert(0, elem)
    root = playlistdocument.getroot()
    
    write_xml(root, dir=dev.typeEpnr(type), output=playlist+'.xml')
    dev.log('Added the episode '+id+' to '+season_tag+': '+season+' in '+dev.typeEpnr(type)+'/'+playlist+'.xml')
    #else:
        #dev.log('playlist_add_episode: not added episode '+id+' since the episode already exists')    