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
                                                                        ### PROBLEM 1: Valid regex can include |. However, if | is present, it gets split above and this will fail.
            if rem is not None:
                striptitle = rem #Regex was succesfull, set striptitle to the found string so it can be stripped as normal
            if striptitle in title:
                title = title[:title.index(striptitle)] #Strip everything to the point where the line was found
    return title  



#################################################################################################################
#     888888ba                    dP                                                           dP               #
#     88    `8b                   88                                                           88               #
#    a88aaaa8P' .d8888b. 88d888b. 88 .d8888b. .d8888b. .d8888b. 88d8b.d8b. .d8888b. 88d888b. d8888P .d8888b.    #
#     88   `8b. 88ooood8 88'  `88 88 88'  `88 88'  `"" 88ooood8 88'`88'`88 88ooood8 88'  `88   88   Y8ooooo.    #
#     88     88 88.  ... 88.  .88 88 88.  .88 88.  ... 88.  ... 88  88  88 88.  ... 88    88   88         88    #
#     dP     dP `88888P' 88Y888P' dP `88888P8 `88888P' `88888P' dP  dP  dP `88888P' dP    dP   dP   `88888P'    #
#                        88                                                                                     #
#                        dP                                                                                     #
#################################################################################################################   

# Now returns list of matches, rather than the first match. Returns None on failure.
# This allows supporting regex with multiple capture groups.
# Adds the capture-all group automatically
def reg2(pattern: str, text: str) -> [type(re.finditer('',''))]:
    if pattern[:6] == 'regex(':
        #print("INSIDE reg2 INSIDE", pattern, txt)
        match = pattern[6:]
        match = match[:-1]
        match = '('+match+')'   #Ensure there's at least one capture group
        #print(match)
        if match is not None:
            if match.count('(') != match.count(')'):
                #This catches cases where the user attempted to use | within regex but did not escape it.
                #Side effect: prevents user-constructed regexes that attmept to match an uneven number of parentheses
                #dev.log("Regex number of parentheses mismatch! Did user forget to escape a '|'?")
                return None
            m = re.finditer(match, text)
            if m:
                #Found the thing we were looking for with the given user regex
                l = list(m)
                #print(l[0].group(1))
                #dev.log('Regex '+match+' found its match: '+l[0].group(0).encode('UTF-8')+' , '+l[0].group(1).encode('UTF-8'))
                return l
            else:
                #Regex not found, return None
                #dev.log('Regex given by user has not found anything: '+match+' on '+txt.encode('UTF-8'), True)
                return None #Return the fallback
        else:
            #dev.log('Regex given by user in settings.xml is not valid!'+pattern, True)
            return None
    else:
        return None #This is not a regex setting

# Modified from https://stackoverflow.com/a/46547822/6739402
#   which is modified from https://stackoverflow.com/a/21882672/6739402
#       which is modified from https://stackoverflow.com/a/18092547/6739402
def split_delimiter_escape(string: str, delimiter: str, escape: str) -> [str]:
    result = []
    current_element = []
    iterator = iter(string)
    for character in iterator:
        if character == escape:
            try:
                next_character = next(iterator)
                if next_character != escape and next_character != delimiter:
                    # Do not copy the escape character if it is escaping itself.
                    # Do not copy the escape character if it escaping a delimiter.
                    # Do copy the escape character otherwise.
                    current_element.append(escape)
                current_element.append(next_character)
            except StopIteration:
                current_element.append(escape)
        elif character == delimiter:
            # split! (add current to the list and reset it)
            result.append(''.join(current_element))
            current_element = []
        else:
            current_element.append(character)
    result.append(''.join(current_element))
    #print(string, '\t', result)
    return result

# Now supports escaped delimiters as literal characters
# Now supports regex using the delimiter character (it must initially be escaped)
# Now requires 'regex(...)' - no longer always treats a single pattern as a regex
# Now supports regex with multiple capture groups (see reg2)
# Adds the capture-all group automatically (see reg2)
def removetext(original: str, pattern: str) -> str:
    if pattern == None:
        pattern = ''
    if len(pattern) > 0:
        returntext = original
        split=split_delimiter_escape(pattern, '|', '\\') #splits on | using \ as escape character        
        for s in split:
            #Check if we should do regex
            rem = reg2(s, returntext)
            if rem is not None:
                for r in rem:
                    #print("AND REM IS: ",r.group(1))
                    s = r.group(1)  #Regex was successful, set s to the found string so it can be removed as normal            
                    returntext = re.sub(s, '', returntext, flags=re.IGNORECASE) #Remove this line from the title
            else:
                returntext = returntext.replace(s, '')
    #print('\''+returntext+'\'')
    return returntext



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
    
    def test_striptitle(self):
        #print("TEST: (original) striptitle")
        self.assertEqual("PUBG | Play Pals!",   striptitle("PUBG | Play Pals!", "foobar"))                          # No truncation
        self.assertEqual("PUBG | ",             striptitle("PUBG | Play Pals!", "Play Pals"))                       # Normal truncation
        self.assertEqual("PUBG | ",             striptitle("PUBG | Play Pals!", "Pals|Play"))                       # Multiple truncation
        #self.assertEqual("PUBG",                striptitle("PUBG | Play Pals!", " \| Play Pals"))                   # Escaped delimiter truncation              #FAIL cannot escape delimiter (issue #5)
        self.assertEqual("PUBG | Play Pals!",   striptitle("PUBG | Play Pals!", "...Pals"))                         # Not non-regex truncation                   
        #self.assertEqual("PUBG | Pl",           striptitle("PUBG | Play Pals!", "regex((...Pals))"))                # Regex truncation                          #FAIL see Problem 4
        #self.assertEqual("PUBG | ",             striptitle("PUBG | Play Pals!", "regex((P(l)(ay)))|Pa"))            # Multiple truncation, multiple regex       #FAIL see Problem 4
        #self.assertEqual("PUBG |  ls!",         striptitle("PUBG | Play Pals!", "regex(P(l)(ay))|Pa"))              # Multiple removal, multiple regex         #FAIL see Problem 2
        #self.assertEqual("PUBG | ",             striptitle("PUBG | Play Pals!", "regex((P((l|a)(a|l))(y|s)))"))     # Regex truncation with delimiters          #FAIL see Problem 1


    def test_removetitle(self):
        #print("TEST: (original) removetitle")
        self.assertEqual("PUBG | Play Pals!",   removetitle("PUBG | Play Pals!", "foobar"))                         # No removal
        self.assertEqual("PUBG | !",            removetitle("PUBG | Play Pals!", "Play Pals"))                      # Normal removal
        self.assertEqual("PUBG |  !",           removetitle("PUBG | Play Pals!", "Pals|Play"))                      # Multiple removal
        #self.assertEqual("PUBG!",               removetitle("PUBG | Play Pals!", " \| Play Pals"))                  # Escaped delimiter removal                #FAIL cannot escape delimiter (issue #5)
        #self.assertEqual("PUBG | Play Pals!",   removetitle("PUBG | Play Pals!", "...Pals"))                        # Not non-regex removal                    #FAIL see Problem 3
        self.assertEqual("PUBG | Pl!",          removetitle("PUBG | Play Pals!", "regex((...Pals))"))               # Regex removal
        #self.assertEqual("PUBG |  ls!",         removetitle("PUBG | Play Pals!", "regex((P(l)(ay)))|Pa"))           # Multiple removal, multi-in-one regex
        #self.assertEqual("PUBG |  ls!",         removetitle("PUBG | Play Pals!", "regex(P(l)(ay))|Pa"))             # Multiple removal, multiple regex         #FAIL see Problem 2
        #self.assertEqual("PUBG |  !",           removetitle("PUBG | Play Pals!", "regex((P((l|a)(a|l))(y|s)))"))    # Regex removal with (escaped) delimiters  #FAIL see Problem 1
        
    def test_removetext(self):
        #print("TEST: (replacement) removetext")
        self.assertEqual("PUBG | Play Pals!",    removetext("PUBG | Play Pals!", "foobar"))                         # No removal
        self.assertEqual("PUBG | !",             removetext("PUBG | Play Pals!", "Play Pals"))                      # Normal removal
        self.assertEqual("PUBG |  !",            removetext("PUBG | Play Pals!", "Pals|Play"))                      # Multiple removal
        self.assertEqual("PUBG!",                removetext("PUBG | Play Pals!", " \| Play Pals"))                  # Escaped delimiter removal
        self.assertEqual("PUBG | Play Pals!",    removetext("PUBG | Play Pals!", "...Pals"))                        # Not non-regex removal 
        self.assertEqual("PUBG | Pl!",           removetext("PUBG | Play Pals!", "regex(...Pals)"))                 # Regex removal
        self.assertEqual("PUBG |  ls!",          removetext("PUBG | Play Pals!", "regex((P(l)(ay)))|Pa"))           # Multiple removal, multi-in-one regex      
        self.assertEqual("PUBG |  Pals!",        removetext("PUBG | Play Pals!", "regex(P(l))|ay"))                 # Multiple removal, multiple regex
        self.assertEqual("PUBG |  !",            removetext("PUBG | Play Pals!", "regex(P((l\|a)(a\|l))(y\|s))"))   # Regex removal with delimiters
    
    def test_split_delimiter_escape(self):
        #print("TEST: (replacement) split_delimiter_escape")
        self.assertListEqual(['A', 'B'],    split_delimiter_escape('A+B', '+', '?'))        # Delimit
        self.assertListEqual(['A+B'],       split_delimiter_escape('A?+B', '+', '?'))       # Escape the delimiter
        self.assertListEqual(['A?', 'B'],   split_delimiter_escape('A??+B', '+', '?'))      # Escape the escape character
        self.assertListEqual(['A?+B'],      split_delimiter_escape('A???+B', '+', '?'))     # Three escapes becomes ?? ?+ becomes ?+
        self.assertListEqual(['A?B'],       split_delimiter_escape('A?B', '+', '?'))        # Escape character remains when preceeding neither delimiter nor escape character
  
if __name__ == '__main__':
    unittest.main()

