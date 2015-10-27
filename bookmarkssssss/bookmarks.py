import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

def getBookmark(name, imdb='0'):
    import hashlib
    #log('getBookmark(%s)' % name)
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
    xbmcvfs.mkdir(xbmc.translatePath(addonInfo('profile')).decode('utf-8')) #Create the directory if it does not yet exist
    dbcon = database.connect(os.path.join(dataPath, 'settings.db'))
    dbcur = dbcon.cursor()
    dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
    match = dbcur.fetchone()
    offset = str(match[1])
    dbcon.commit()
    return offset
