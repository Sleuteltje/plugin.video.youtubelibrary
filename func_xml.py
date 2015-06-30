from addon import log

############################ XML SETTINGS #################################### 
#Loads the xnl document        
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
                #Strip Stuff from NFO information
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




      
      
      

        
        
        



      
# Create new user, but only if the user does not exist yet!
# def xml_new_user(user):
    # log('XML: Create New User', True)
    # # <membership/>
    # document = ElementTree.parse( settingsPath+'settings.xml' )        
    
    
    # root = document.getroot()
    
    # lFound = False
    # for child in document.findall('users/user'):
        # log('XML: Looping <'+child.tag+' name='+child.attrib['name']+'>')
        # if child.tag == 'user':
            # if child.attrib['name'] == user:
                # log('XML: Found user '+user)
                # lFound = True
                # break # Since we found the user we can quit the for loop

    # if not lFound:
        # #lRoot.append(Element('Environment', {'description': 'Username', 'name':'Username'}))
        
        # newNode = Element('user', name=user)
        # #Create a subnode
        # newNodeName = ElementTree.Element('age')
        # newNodeName.text = '26'
        # newNode.append(newNodeName)
        # root[0].insert(0, newNode)
        
        # #output_file = os.path.join(settingsPath, 'settings.xml')
        # #document.write(output_file) 
        # write_xml(root)
    # log('XML: Done', True)

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
        
# Updates a users setting (like <age>)
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

    
    #global root #So that we can store the 
    #root = document.getroot() # Grab the root of the xml document

        
# xml_get_elem
    # Grabs the element you are looking from the xml file and returns it
                        # Example: 
                        # <users>
                        #   <user name="someuser">sometext</user>  <--- This you would like to update
                        #   <user name="leavethisbe">Dont want to update this</user>
                        
        # path: Path to the xml element you would like to parse. (In the examples case: 'users/user')
        # tag:  The tag that should be updated (In the examples case: user)
        # whereAttrib: The element that should be updated should contain the following attribute at the following value. (In the examples case: {name: someuser}
        # whereTxt: The element that should be updated should contain this text. (In the examples case: 'sometext' would find the correct user
        
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