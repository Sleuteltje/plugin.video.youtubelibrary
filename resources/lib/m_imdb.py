# -*- coding: utf-8 -*-
#    Kodi Addon: Youtube Library
#    Copyright 2015-2016 Sleuteltje
#
#    This file is part of plugin.video.youtubelibrary
#    Description: Functions to play a youtube video
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
from __future__ import division
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcplugin
import sys
import re
from BeautifulSoup import BeautifulSoup
import requests
import time

from resources.lib import vars
from resources.lib import dev

def search(search, cutoff = '75', deny_without_poster = False, year=False):
    #search = 'The Shawshank Redemption'
    cutoff = int(cutoff) / 100
    search_urlfriendly = search.replace(' ', '%20')
    #cutoff = 0.8 #The cutoff in which imdb matches are accepted
    #year = '1995' #A year the movie is released in?
    #deny_without_poster = True #Should we skip movies that have no poster image?
    if year is not False:
        search_urlfriendly += '%20'+year
    
    url = 'http://www.imdb.com/find?q='+search_urlfriendly+'&s=tt&ttype=ft'
    
    
    try:
        r = requests.get(url) # where url is the above url
    except:
        dev.log('IMDB refused our connection. Retry again in 12 seconds')
        time.sleep(12)
        try:
            r = requests.get(url)
        except:
            dev.log('IMDB refused the connection again. Retrying last time in 60 seconds')
            time.sleep(60)
            r = requests.get(url)
        
    dev.log('imdb.search() url: '+url)
    
    bs = BeautifulSoup(r.text)
    
    for movie in bs.findAll('tr', {'class': re.compile(r'\bfindResult\b')}):
        
        #movie_info = movie.find('div', {'class': 'lister-item-content'})
        
        movie_name = movie.findAll('a')[1].contents[0]
        movie_url = 'http://imdb.com'+movie.find('a')['href']
        dev.log('-- Found a movie: '+str(movie_name)+' url: '+str(movie_url))
        
        movie_image = movie.find('img')['src']
        if 'nopicture' in movie_image:
            dev.log('Movie does not have a poster')
            if deny_without_poster == True:
                dev.log('deny_without_poster is enabled, skip this movie')
                continue
                
        dev.log('Movie poster: '+movie_image)

        movie_year = movie.find('td', {'class': 'result_text'})
        if movie_year:
            if len(movie_year.contents)>2:
                movie_year = movie_year.contents[2].strip(' \t\n\r')[1:5]
                dev.log('Found the year of the movie: '+str(movie_year))
                if year != movie_year and year is not False:
                    dev.log('Year does not match with the expected year! Skipping movie: '+year)
                    continue
                
        import difflib
        match = difflib.SequenceMatcher(None, search,movie_name).ratio()
        dev.log('Match with search: '+str(match))
        
        if match > cutoff:               
            
            dev.log('imdb.search(): Found match: '+movie_url)
            return {
                'url'  : movie_url,
                'name' : movie_name,
                'year' : movie_year,
                'image': movie_image,
            }
        
        
        else:
            dev.log('Movie did not match enough with the configured cutoff: '+str(cutoff))
    
    dev.log('imdb.search(): Did not find any matches')
    return False
            



def search_advanced(search='The Shawshank Redemption', year=False):
    search = 'The Evolved Part 1'
    search_urlfriendly = search.replace(' ', '%20')
    cutoff = 0.8 #The cutoff in which imdb matches are accepted
    #year = '1994' #A year the movie is released in?
    deny_without_poster = True #Should we skip movies that have no poster image?
    
    url = 'http://www.imdb.com/search/title?sort=num_votes,desc&start=1&title_type=feature'
    

    url = 'http://www.imdb.com/search/title?title='+search_urlfriendly+'&title_type=feature,tv_movie,tv_special,documentary,short,video'
    #http://www.imdb.com/find?q=the%20get%20down&s=tt&ttype=ft&ref_=fn_ft&exact=true
    
    if year is not False:
        url += '&year='+year
    
    
    r = requests.get(url) # where url is the above url    
    dev.log('got url: '+url)
    #dev.log(r.text)
    
    bs = BeautifulSoup(r.text)
    
    for movie in bs.findAll('div', {"class" : "lister-item mode-advanced"}):
        
        movie_info = movie.find('div', {'class': 'lister-item-content'})
        
        movie_name = movie_info.find('a').contents[0]
        movie_url = 'http://imdb.com'+movie_info.find('a')['href']
        dev.log('-- Found a movie: '+str(movie_name)+' url: '+str(movie_url))

        
        movie_year = False
        if movie_info.find('span', {'class': 'lister-item-year text-muted unbold'}) is not None:
            movie_year = movie_info.find('span', {'class': 'lister-item-year text-muted unbold'}).contents[0][1:5]
            dev.log('Found the year of the movie: '+movie_year)
        
        ##Getting runtime
        movie_runtime = False
        if movie_info.find('span', {'class': 'runtime'}):
            movie_runtime = movie_info.find('span', {'class': 'runtime'}).contents[0].replace(' min', '')
            dev.log('Found the runtime of the movie: '+movie_runtime)
        
        ##Getting Genres
        movie_genre = False
        if movie_info.find('span', {'class': 'genre'}):
            movie_genre = movie_info.find('span', {'class': 'genre'}).contents[0].strip(' \t\n\r').replace(', ', ' / ')
            dev.log('Found the genre of the movie: '+movie_genre)
        
        ##Getting Rating
        if movie_info.find('strong'):
            movie_rating = movie_info.find('strong').contents[0]
            dev.log('Found the rating of the movie: '+movie_rating)
        
        ##Getting Metascore
        if movie_info.find('span', {'class': re.compile(r'\bmetascore\b')}):
            movie_metascore = movie_info.find('span', {'class': re.compile(r'\bmetascore\b')}).contents[0]
            dev.log('Found the metascore of the movie: '+movie_metascore)
        
        ##Getting Summary
        if movie_info.find('p', {'class': 'text-muted'}):
            movie_summary = movie_info.find('p', {'class': 'text-muted'}).contents[0].strip(' \t\n\r')
            dev.log('Found the summary of the movie: '+movie_summary)
        
        import difflib
        match = difflib.SequenceMatcher(None, search,movie_name).ratio()
        dev.log('Match with search: '+str(match))
        
        if match > cutoff:               
            
            dev.log('Match accepted')
            #return True
        
        
        else:
            dev.log('Movie did not match enough with the configured cutoff: '+str(cutoff))
    
    dev.log('imdb.search(): Did not find any matches')
    return False
            











