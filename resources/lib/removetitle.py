# -*- coding: utf-8 -*-

import re
import os
import urllib



#########################################################################
#     .88888.           oo          oo                   dP             #
#    d8'   `8b                                           88             #
#    88     88 88d888b. dP .d8888b. dP 88d888b. .d8888b. 88 .d8888b.    #
#    88     88 88'  `88 88 88'  `88 88 88'  `88 88'  `88 88 Y8ooooo.    #
#    Y8.   .8P 88       88 88.  .88 88 88    88 88.  .88 88       88    #
#     `8888P'  dP       dP `8888P88 dP dP    dP `88888P8 dP `88888P'    #
#                               .88                                     #
#                           d8888P                                      #
#########################################################################

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
                dev.log('Regex '+ma+' found its match: '+m.group(0).encode('UTF-8')+' , '+m.group(1).encode('UTF-8'))
                return m.group(1)
            else:
                #Regex not found, return None
                dev.log('Regex given by user has not found anything: '+ma+' on '+txt.encode('UTF-8'), True)
                return None #Return the fallback
        else:
            dev.log('Regex given by user in settings.xml is not valid!'+se, True)
            return None
    else:
        return None #This is not a regex setting


def removetitle(title, removetitle):
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
            title = re.sub(removetitle, '', title, flags=re.IGNORECASE)
            #if removetitle in title:
                #title = title.replace(removetitle, '')
    return title

def striptitle(title, striptitle):
    if striptitle == None:
        striptitle = ''
    if len(striptitle) > 0:
        #See if there are multiple lines
        if '|' in striptitle:
            strip = striptitle.split('|')
            for s in strip:
                if s in title:
                    title = title[:title.index(s)] #Strip everything to the point where the line was found
        else:
            #Check if this is a regex var of what should be removed
            rem = reg(title, striptitle)
            if rem is not None:
                striptitle = rem #Regex was succesfull, set striptitle to the found string so it can be stripped as normal
            if striptitle in title:
                title = title[:title.index(striptitle)] #Strip everything to the point where the line was found
    return title  

