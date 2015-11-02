import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
#Import database libs
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database
import os

from resources.lib import vars
from resources.lib import dev

# Gets the bookmark of the given episode
def getBookmark(name, imdb='0'):
    import hashlib
    dev.log('getBookmark(%s)' % name)
    offset = '0'
    #log('getBookmark 1')
    idFile = hashlib.md5()
    #log('getBookmark 2')
    for i in name: idFile.update(str(i))
    #log('getBookmark 3')
    for i in imdb: idFile.update(str(i))
    #log('getBookmark 4')
    idFile = str(idFile.hexdigest())
    #log('getBookmark: idFile calculated: %s' % idFile)
    xbmcvfs.mkdir(vars.dataPath) #Create the directory if it does not yet exist
    dbcon = database.connect(vars.databaseFile)
    dbcur = dbcon.cursor()
    dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
    match = dbcur.fetchone()
    offset = str(match[1])
    dbcon.commit()
    return offset  


def addBookmark(currentTime, name, imdb='0'):
    import hashlib
    dev.log('addBookmark(%s)' % name)
    try:
        idFile = hashlib.md5()
        for i in name: idFile.update(str(i))
        for i in imdb: idFile.update(str(i))
        idFile = str(idFile.hexdigest())
        dev.log('addBookmark: idFile calculated: %s' % idFile)
        timeInSeconds = str(currentTime)
        xbmcvfs.mkdir(xbmc.translatePath(vars.addonInfo('profile')).decode('utf-8')) #Create the directory if it does not yet exist
        dbcon = database.connect(os.path.join(vars.dataPath, 'settings.db'))
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
        dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
        dbcur.execute("INSERT INTO bookmark Values (?, ?)", (idFile, timeInSeconds))
        dbcon.commit()
    except:
        pass

#Deletes a bookmark from the database
def deleteBookmark(name, imdb='0'):
    dev.log('deleteBookmark(%s)' % name)
    import hashlib
    try:
        idFile = hashlib.md5()
        for i in name: idFile.update(str(i))
        for i in imdb: idFile.update(str(i))
        idFile = str(idFile.hexdigest())
        control.makeFile(control.vars.dataPath)
        dbcon = database.connect(os.path.join(vars.dataPath, 'settings.db'))
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
        dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
        dbcon.commit()
    except:
        pass

    
#Mark the video as watched through the JSON of Kodi   
def mark_as_watched(DBID, folderPath):    
    try:
        xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(DBID))
        if not folderPath.startswith('plugin://'): xbmc.executebuiltin('Container.Refresh')
    except:
        pass
