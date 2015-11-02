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
def xml_get():
    dev.log('XML_get')
    global document #Set the document variable as global, so every function can reach it
    document = ElementTree.parse( vars.settingsPath+'settings.xml' )
    
# Converts the elementtree element to prettified xml and stores it in the settings.xml file
def write_xml(elem, dir='', output='settings.xml'):
    xbmcvfs.mkdir(vars.settingsPath) #Create the settings dir if it does not exist already
    if dir is not '': xbmcvfs.mkdir(vars.settingsPath+dir) #Create the settings dir if it does not exist already
    #Write these settings to a .xml file in the addonfolder
    output_file = os.path.join(vars.settingsPath+dir, output) #Set the outputfile to settings.xml

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
    write_xml(root)
    dev.log('Create_xml: Created new settings.xml file')

# Builds and returns an playlist element that can be added to the playlist element
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
def xml_remove_playlist(id):
    dev.log('XML_remove_playlist('+id+')')
    pl = xml_get_elem('playlists/playlist', 'playlist', {'id': id})
    if pl is not None:
        dev.log('Found the playlist to delete')
        
        root = document.getroot()
        parent = root.find('playlists')
        parent.remove(pl)
        write_xml(root)
        dev.log('XML_remove_playlist: Removed playlist '+id)
        return True
    else:
        return False
       
    
#Adds the playlist to the xml if it does not exist yet, and retrieves information about the playlist
def xml_add_playlist(id):
    dev.log('XML_add_playlist('+id+')')
    #Check if this playlist isnt in the xml file yet
    if xml_get_elem('playlists/playlist', 'playlist', {'id' : id}) is None:
        #Playlist does not yet exist, grab the channel id by this playlist id
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
                'episode'           : 'default',
                'striptitle'            : '',
                'removetitle'       : '',
                'stripdescription' : '',
                'removedescription' : '',
                #Scan Settings
                'lastvideoId'       : '',
            }
        }
        pl = xml_create_playlist(playlist)
        root = document.getroot()
        root[0].insert(0, pl)
        write_xml(root)
        dev.log('Added the playlist '+id+' to the settings.xml', 1)
    else:
        dev.log('XML_add_playlist: not added playlist '+id+' since the playlist already exists', 2)    
    


# Updates a playlist that already exists
def xml_update_playlist_attr(id, attr, val):
    dev.log('XML: Updating playlist id '+id+' with attr '+attr+' : '+val)
    
    #Grab this playlist from the xml file
    playlist = xml_get_elem('playlists/playlist', 'playlist', {'id' : id})
    
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
        write_xml(root)
        dev.log('XML_update_playlist_attr: written XML')
        
# Updates a playlist setting (like <age>)
def xml_update_playlist_setting(id, tag, newsetting):
    dev.log('XML_update_playlist_setting ('+id+', '+tag+', '+newsetting+')')
    
    #Grab this playlist from the xml file
    elem = xml_get_elem('playlists/playlist', 'playlist', {'id' : id})
    
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
            return False
        else:
            #Change the setting to its new setting
            setting.text = newsetting
            #Write this to the xml
            root = document.getroot()
            write_xml(root)
            dev.log('XML_update_playlist_setting: Updated xml setting '+tag+' of '+id+' to '+newsetting)
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
def xml_get_elem(path, tag, whereAttrib=False, whereTxt=False, playlist=False):    
    dev.log('XML_get_elem')
    if playlist == False:
        xml_get() # Grab the xml file
        doc = document
    else:
        doc = playlist_xml_get(playlist) #Grab the episodes.xml file of this playlist
    
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
def playlist_create_xml(playlist):
    dev.log('playlist_create_xml')
    
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
    write_xml(root, 'episodenr', playlist+'.xml')
    dev.log('playlist_create_xml: Created new episodenr/'+playlist+'.xml')

#Loads the playlist episodes xml document        
def playlist_xml_get(playlist):
    dev.log('playlist_XML_get')
    if xbmcvfs.exists(os.path.join(vars.settingsPath,"episodenr/"+playlist+".xml")) == False: #If the episodes.xml file can't be found, we should create this file
        playlist_create_xml(playlist)
    
    global playlistdocument #Set the document variable as global, so every function can reach it
    playlistdocument = ElementTree.parse( vars.settingsPath+'episodenr/'+playlist+'.xml' )
    return playlistdocument


#Returns the number of episodes in a season
def number_of_episodes(playlist, season):
    s = xml_get_elem('season', 'season', {'number': season}, playlist=playlist)
    if s == None:
        dev.log('number_of_episodes: Could not find season '+season+' in playlist '+playlist)
        return None
    dev.log('number_of_episodes: Found '+str(len(s))+' episodes in season '+season)
    return len(s)
    
#Does the episode already exist
def episode_exists(playlist, episode):
    dev.log('episode_exists('+playlist+', '+episode+')')
    #Quicker way to check if this episode already exists
    doc = playlist_xml_get(playlist)
    e = doc.findall("*/episode[@id='"+episode+"']")
    if len(e) == 0:
        dev.log('episode '+episode+' is not yet present in episodenr file')
        return False
    dev.log('Already present: '+episode)
    return True



#Adds the playlist to the xml if it does not exist yet, and retrieves information about the playlist
def playlist_add_season(playlist, season):
    dev.log('playlist_add_season('+season+')')
    #Check if this playlist isnt in the xml file yet
    #if xml_get_elem('season', 'episode', {'id' : id}, playlist=playlist) is None:
    #Build the playlist
    doc = playlist_xml_get(playlist)
    
    attr = { 'number' : season}
    elem = Element('season', attr)
    root = doc.getroot()
    root.insert(0, elem)
    write_xml(root, dir='episodenr', output=playlist+'.xml')
    dev.log('Added season '+season+' in episodenr/'+playlist+'.xml')
    #else:
        #dev.log('playlist_add_episode: not added episode '+id+' since the episode already exists')    #Adds the playlist to the xml if it does not exist yet, and retrieves information about the playlist

def playlist_add_episode(playlist, season, id):
    dev.log('playlist_add_episode('+season+','+id+')')
    #Check if this playlist isnt in the xml file yet
    #if xml_get_elem('season', 'episode', {'id' : id}, playlist=playlist) is None:
    #Build the playlist
    doc = playlist_xml_get(playlist)
    
    s = doc.find("season[@number='"+season+"']")
    if s is None:
        playlist_add_season(playlist, season)
        doc = playlist_xml_get(playlist)
        s = doc.find("season[@number='"+season+"']")
        
    
    attr = { 'id' : id}
    elem = Element('episode', attr)
    
    s.insert(0, elem)
    root = doc.getroot()
    
    write_xml(root, dir='episodenr', output=playlist+'.xml')
    dev.log('Added the episode '+id+' to season '+season+' in episodenr/'+playlist+'.xml')
    #else:
        #dev.log('playlist_add_episode: not added episode '+id+' since the episode already exists')    