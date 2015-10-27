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
#For database connections to store the resume point and watched flag
#Import database libs
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database




##NONCONFIGURABLE
addonInfo = xbmcaddon.Addon().getAddonInfo
skinPath = xbmc.translatePath('special://skin/')
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
databaseFile = os.path.join(dataPath, 'settings.db')
cachesourcesFile = os.path.join(dataPath, 'sources.db')
cachemetaFile = os.path.join(dataPath, 'metacache.db')
cacheFile = os.path.join(dataPath, 'cache.db')
#Paths
addonPath = xbmcaddon.Addon().getAddonInfo("path")
IMG_DIR = os.path.join(addonPath,'resources/media')
gearArt = os.path.join(addonPath,'resources/media/gear.png')
settingsPath = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.youtubelibrary/Settings'), '')
#Addonname and icon
__addonname__ = xbmcaddon.Addon().getAddonInfo('name')
__icon__ = xbmcaddon.Addon().getAddonInfo('icon')
