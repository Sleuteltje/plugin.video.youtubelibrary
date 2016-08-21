# -*- coding: utf-8 -*-
#    Kodi Addon: Youtube Library
#    Copyright 2016 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions to communicate with the youtube API
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

import sys
import re
import json
import urllib2




from resources.lib import vars
from resources.lib import dev


def build_url():
    url = '?api_token='+vars.__settings__.getSetting('api_token')+'&lang=int'
    if vars.__settings__.getSetting('api_language') != 'none':
        url += '+'+vars.__settings__.getSetting('api_language')    
    if vars.__settings__.getSetting('api_language2') != 'none':
        url += '+'+vars.__settings__.getSetting('api_language2')
    if vars.__settings__.getSetting('api_language3') != 'none':
        url += '+'+vars.__settings__.getSetting('api_language3')
    return url


#Browse playlists
def browse(api_url = 'http://youtubelibrary.nl/api/v1/playlists/tv'+build_url()+'&limit=20', params = False):
    if api_url == 'default':
        api_url = 'http://youtubelibrary.nl/api/v1/playlists/tv'+build_url()+'&limit=20'
    
    #Check if we should add params
    if isinstance(params,dict):
        for key, val in params.iteritems():
            api_url += '&'+key+'='+val
    
    
    dev.log('Browse the API with url: '+api_url)
    data = json.load(urllib2.urlopen(api_url))
    
    if 'data' not in data:
        url = dev.build_url({'mode': 'ApiIndex'})
        dev.adddir('Something went wrong', url, description='There was an error connecting to the Ytlibrary API.')
        return False;


    for playlist in data['data']:
        #videos.append(search_result)
        url = dev.build_url({'mode': 'ApiAddPlaylist', 'id': playlist['id']})
        dev.adddir(playlist['title'], url, playlist['thumb'], fanart=playlist['fanart'], description=playlist['description'])
        
    if 'paginator' in data:
        if 'prev_page' in data['paginator']:
            if data['paginator']['prev_page'] is not None:
                url = dev.build_url({'mode': 'ApiBrowse', 'api_url': data['paginator']['prev_page']})
                dev.adddir('<< Page '+str(data['paginator']['current_page']-1), url, description='Go to the previous page')       
    
    if 'paginator' in data:
        if 'next_page' in data['paginator']:
            if data['paginator']['next_page'] is not None:
                url = dev.build_url({'mode': 'ApiBrowse', 'api_url': data['paginator']['next_page']})
                dev.adddir('>> Page '+str(data['paginator']['current_page']+1), url, description='Go to the next page to see more pre-configured playlists.')          
                

#Browse genres
def browse_genres(api_url = 'http://youtubelibrary.nl/api/v1/genres/tv'+build_url()):
    if api_url == 'default':
        api_url = 'http://youtubelibrary.nl/api/v1/genres/tv'+build_url()
    
    
    dev.log('Browse genres at the API with url: '+api_url)
    data = json.load(urllib2.urlopen(api_url))
    
    if 'data' not in data:
        url = dev.build_url({'mode': 'ApiIndex'})
        dev.adddir('Something went wrong', url, description='There was an error connecting to the Ytlibrary API.')
        return False;


    for genre in data['data']:
        #videos.append(search_result)
        url = dev.build_url({'mode': 'ApiBrowse', 'api_url': 'http://youtubelibrary.nl/api/v1/playlists/tv'+build_url()+'&limit=10&genre='+str(genre['id'])})
        dev.adddir(genre['title'], url, description='View all playlists from the genre '+genre['title'])
        
    if 'paginator' in data:
        if 'prev_page' in data['paginator']:
            if data['paginator']['prev_page'] is not None:
                url = dev.build_url({'mode': 'ApiGenres', 'api_url': data['paginator']['prev_page']})
                dev.adddir('<< Page '+str(data['paginator']['current_page']-1), url, description='Go to the previous page')       
    
    if 'paginator' in data:
        if 'next_page' in data['paginator']:
            if data['paginator']['next_page'] is not None:
                url = dev.build_url({'mode': 'ApiGenres', 'api_url': data['paginator']['next_page']})
                dev.adddir('>> Page '+str(data['paginator']['current_page']+1), url, description='Go to the next page to see more genres of pre-configured playlists.')          

#Browse tags
def browse_tags(api_url = 'http://youtubelibrary.nl/api/v1/tags/tv'+build_url()):
    if api_url == 'default':
        api_url = 'http://youtubelibrary.nl/api/v1/tags/tv'+build_url()
    
    
    dev.log('Browse tags at the API with url: '+api_url)
    data = json.load(urllib2.urlopen(api_url))
    
    if 'data' not in data:
        url = dev.build_url({'mode': 'ApiIndex'})
        dev.adddir('Something went wrong', url, description='There was an error connecting to the Ytlibrary API.')
        return False;


    for tag in data['data']:
        #videos.append(search_result)
        url = dev.build_url({'mode': 'ApiBrowse', 'api_url': 'http://youtubelibrary.nl/api/v1/playlists/tv'+build_url()+'&limit=10&tag='+str(tag['id'])})
        dev.adddir(tag['title'], url, description='View all playlists from the tag '+tag['title'])
        
    if 'paginator' in data:
        if 'prev_page' in data['paginator']:
            if data['paginator']['prev_page'] is not None:
                url = dev.build_url({'mode': 'ApiTags', 'api_url': data['paginator']['prev_page']})
                dev.adddir('<< Page '+str(data['paginator']['current_page']-1), url, description='Go to the previous page')       
    
    if 'paginator' in data:
        if 'next_page' in data['paginator']:
            if data['paginator']['next_page'] is not None:
                url = dev.build_url({'mode': 'ApiTags', 'api_url': data['paginator']['next_page']})
                dev.adddir('>> Page '+str(data['paginator']['current_page']+1), url, description='Go to the next page to see more tags of pre-configured playlists.')          
                



def add_playlist(id):
    api_url = 'http://youtubelibrary.nl/api/v1/playlists/tv/'+id+'?api_token='+vars.__settings__.getSetting('api_token')
    dev.log('Adding the Api playlist to the config: '+api_url)
    data = json.load(urllib2.urlopen(api_url))
    
    if 'data' not in data:
        url = dev.build_url({'mode': 'ApiIndex'})
        dev.adddir('Something went wrong', url, description='There was an error getting the playlist from the youtubelibrary.nl API.')
        return False;
    
    playlist = data['data']
    
    return playlist
    
    url = dev.build_url({'mode': 'ApiAddPlaylist'})
    dev.adddir(playlist['title'], url, description=playlist['description'])          


