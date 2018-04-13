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
#annotated with 'PROBLEM' where appropriate.
#disabled dev.log where present.

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
                #dev.log('Regex '+ma+' found its match: '+m.group(0).encode('UTF-8')+' , '+m.group(1).encode('UTF-8'))
                return m.group(1)
            else:
                #Regex not found, return None
                #dev.log('Regex given by user has not found anything: '+ma+' on '+txt.encode('UTF-8'), True)
                return None #Return the fallback
        else:
            #dev.log('Regex given by user in settings.xml is not valid!'+se, True)
            return None
    else:
        return None #This is not a regex setting

# PROBLEMS
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
            rem = reg(removetitle, title)                               ### PROBLEM 1: Valid regex can include |. However, if | is present, it gets split above and this will fail.
                                                                        ### PROBLEM 2: Valid regex can include multiple capture groups, but this only returns one of them.
            if rem is not None:
                removetitle = rem #Regex was succesfull, set removetitle to the found string so it can be removed as normal
            title = re.sub(removetitle, '', title, flags=re.IGNORECASE) ### PROBLEM 3: this does regex matching regardless of whether it was intended by surrounding in a 'regex()' clause
            #if removetitle in title:
                #title = title.replace(removetitle, '')
    return title

# PROBLEMS
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
            rem = reg(title, striptitle)                                ### PROBLEM 4: this is used backwards - should be reg(striptitle, title) - compare against removetitle
            if rem is not None:
                striptitle = rem #Regex was succesfull, set striptitle to the found string so it can be stripped as normal
            if striptitle in title:
                title = title[:title.index(striptitle)] #Strip everything to the point where the line was found
    return title  



################################################################
#    d888888P                     dP   oo                      #
#       88                        88                           #
#       88    .d8888b. .d8888b. d8888P dP 88d888b. .d8888b.    #
#       88    88ooood8 Y8ooooo.   88   88 88'  `88 88'  `88    #
#       88    88.  ...       88   88   88 88    88 88.  .88    #
#       dP    `88888P' `88888P'   dP   dP dP    dP `8888P88    #
#                                                       .88    #
#                                                   d8888P     #
################################################################
import unittest
class TestStringMethods(unittest.TestCase):
    
    def test_removetitle(self):
        #print("TEST: (original) removetitle")
        self.assertEqual("PUBG | Play Pals!",   removetitle("PUBG | Play Pals!", "foobar"))                         # No removal
        self.assertEqual("PUBG | !",            removetitle("PUBG | Play Pals!", "Play Pals"))                      # Normal removal
        self.assertEqual("PUBG |  !",           removetitle("PUBG | Play Pals!", "Pals|Play"))                      # Multiple removal
        #self.assertEqual("PUBG!",               removetitle("PUBG | Play Pals!", " \| Play Pals"))                  # Escaped delimiter removal                #FAIL cannot escape delimiter (issue #5)
        #self.assertEqual("PUBG | Play Pals!",   removetitle("PUBG | Play Pals!", "...Pals"))                        # Not non-regex removal                    #FAIL see Problem 3
        self.assertEqual("PUBG | Pl!",          removetitle("PUBG | Play Pals!", "regex((...Pals))"))               # Regex removal
        #self.assertEqual("PUBG |  Pals!",       removetitle("PUBG | Play Pals!", "regex(P(l))|ay"))                 # Multiple removal, multiple regex         #FAIL see Problem 2  
        #self.assertEqual("PUBG |  !",           removetitle("PUBG | Play Pals!", "regex(P((l\|a)(a\|l))(y\|s))"))   # Regex removal with (escaped) delimiters  #FAIL see Problem 1
        
  
if __name__ == '__main__':
    unittest.main() 
    