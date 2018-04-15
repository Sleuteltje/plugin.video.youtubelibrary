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
            print("Rem:",rem)                                           ### PROBLEM 5: Rem can contain plaintext of special characters that were matched by escape or wildcards that will break regex, like |
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

#Returns pattern suitable for using in regex search
#Strips "regex(" and ")" from patterns marked that way
#Otherwise, returns pattern with special characters escaped 
def regularize(pattern: str) -> str:
    if pattern[:6] == 'regex(':
        if pattern[-1] == ')':
            return pattern[6:-1]    #substring is already regex-compatible, just return it
        else: 
            #dev.log("Found 'Regex('' without closing ')' - did the user forget to escape a '|'?")
            return re.escape(pattern) #don't want to return nothing, so treat it literally
    else:
        #pattern was not already structured for regex and must be sanitized before use
        return re.escape(pattern)


# Supports escaped delimiters as literal characters
# Supports regex using the delimiter character (it must initially be escaped)
# Only treats patterns as regex if properly encased in "regex()" (see regularize)
# Supports any valid regex expression, not merely a single capture group without | characters
# Supports keeping all nonmatching text, text preceeding match, or text following match. (Or no text at all.)
def deletetext(text: str, pattern: str, keep_start: bool, keep_end: bool) -> str:
    if pattern:
        splitpattern=split_delimiter_escape(pattern, '|', '\\') #splits pattern on | using \ as escape character        
        for s in splitpattern:
            if s:
                regexpattern=regularize(s) #get regex-safe version of pattern 
                m=re.search(regexpattern,text)
                while m:
                    start = m.string[:m.start()] if keep_start else ""  #keep text before the regex match?
                    end = m.string[m.end():] if keep_end else ""        #keep text after the regex match?
                    text=start+end                                      #remove the matching text, i.e. omit m.string[m.start():m.end()]
                    m=re.search(m.re.pattern,text)                      #recurse until no matches
    return text




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
        #self.assertEqual("PUBG",                striptitle("PUBG | Play Pals!", " \| Play Pals"))                   # Escaped delimiter truncation              #FAIL cannot escape delimiter (github Issue #5)
        self.assertEqual("PUBG | Play Pals!",   striptitle("PUBG | Play Pals!", "...Play"))                         # Not non-regex truncation                   
        #self.assertEqual("PUBG",                striptitle("PUBG | Play Pals!", "regex((...Play))"))                # Regex truncation                          #FAIL see Problem 4, 5
        #self.assertEqual("PUBG | ",             striptitle("PUBG | Play Pals!", "regex((P(l)(ay)))|Pa"))            # Multiple truncation, multiple regex       #FAIL see Problem 4
        #self.assertEqual("PUBG | ",             striptitle("PUBG | Play Pals!", "regex(P(l)(ay))|Pa"))              # Multiple removal, multiple regex          #FAIL see Problem 2
        #self.assertEqual("PUBG | ",             striptitle("PUBG | Play Pals!", "regex((P((l|a)(a|l))(y|s)))"))     # Regex truncation with delimiters          #FAIL see Problem 1

    def test_removetitle(self):
        #print("TEST: (original) removetitle")
        self.assertEqual("PUBG | Play Pals!",   removetitle("PUBG | Play Pals!", "foobar"))                         # No removal
        self.assertEqual("PUBG | !",            removetitle("PUBG | Play Pals!", "Play Pals"))                      # Normal removal
        self.assertEqual("PUBG |  !",           removetitle("PUBG | Play Pals!", "Pals|Play"))                      # Multiple removal
        #self.assertEqual("PUBG!",               removetitle("PUBG | Play Pals!", " \| Play Pals"))                  # Escaped delimiter removal                #FAIL cannot escape delimiter (github Issue #5)
        #self.assertEqual("PUBG | Play Pals!",   removetitle("PUBG | Play Pals!", "...Play"))                        # Not non-regex removal                    #FAIL see Problem 3
        #self.assertEqual("PUBG Pals!",          removetitle("PUBG | Play Pals!", "regex((...Play))"))               # Regex removal                            #FAIL see Problem 5
        #self.assertEqual("PUBG |  ls!",         removetitle("PUBG | Play Pals!", "regex((P(l)(ay)))|Pa"))           # Multiple removal, multi-in-one regex
        #self.assertEqual("PUBG |  ls!",         removetitle("PUBG | Play Pals!", "regex(P(l)(ay))|Pa"))             # Multiple removal, multiple regex         #FAIL see Problem 2
        #self.assertEqual("PUBG |  !",           removetitle("PUBG | Play Pals!", "regex((P((l|a)(a|l))(y|s)))"))    # Regex removal with (escaped) delimiters  #FAIL see Problem 1
    
    def test_null_text(self):
        #print("TEST: (replacement) deletetext in 'null' mode (false, false)")
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "",                                 False, False))    # Null pattern
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "|",                                False, False))    # Bare delimiter
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "foobar",                           False, False))    # No removal
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "Play Pals",                        False, False))    # Normal removal
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "Pals|Play",                        False, False))    # Multiple removal
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     " \| Play Pals",                    False, False))    # Escaped delimiter removal
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "...Play",                          False, False))    # Not non-regex removal 
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "regex(...Play)",                   False, False))    # Regex removal
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "regex((P(l)(ay)))|Pa",             False, False))    # Multiple removal, multi-in-one regex      
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "regex(P(l))|ay",                   False, False))    # Multiple removal, multiple regex
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "regex(P((l\|a)(a\|l))(y\|s))",     False, False))    # Regex removal with delimiters
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "regex(\\\\\\|)",                   False, False))    # Regex removal of escaped delimier / special regex character
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     r"regex(\\\|)",                     False, False))    # Note: identical to above.
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "P",                                False, False))    # Multi-match
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "PUBG",                             False, False))    # Start of string
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "!",                                False, False))    # End of string 
    
    def test_tail_text(self):
        #print("TEST: (replacement) deletetext in 'keep-end' mode (false, true)")
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "",                                 False, True))    # Null pattern
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "|",                                False, True))    # Bare delimiter
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "foobar",                           False, True))    # No removal
        self.assertEqual("!",                   deletetext("PUBG | Play Pals!",     "Play Pals",                        False, True))    # Normal removal
        self.assertEqual("!",                   deletetext("PUBG | Play Pals!",     "Pals|Play",                        False, True))    # Multiple removal
        self.assertEqual("!",                   deletetext("PUBG | Play Pals!",     " \| Play Pals",                    False, True))    # Escaped delimiter removal
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "...Play",                          False, True))    # Not non-regex removal 
        self.assertEqual(" Pals!",              deletetext("PUBG | Play Pals!",     "regex(...Play)",                   False, True))    # Regex removal
        self.assertEqual("ls!",                 deletetext("PUBG | Play Pals!",     "regex((P(l)(ay)))|Pa",             False, True))    # Multiple removal, multi-in-one regex      
        self.assertEqual(" Pals!",              deletetext("PUBG | Play Pals!",     "regex(P(l))|ay",                   False, True))    # Multiple removal, multiple regex
        self.assertEqual("!",                   deletetext("PUBG | Play Pals!",     "regex(P((l\|a)(a\|l))(y\|s))",     False, True))    # Regex removal with delimiters
        self.assertEqual(" Play Pals!",         deletetext("PUBG | Play Pals!",     "regex(\\\\\\|)",                   False, True))    # Regex removal of escaped delimier / special regex character
        self.assertEqual(" Play Pals!",         deletetext("PUBG | Play Pals!",     r"regex(\\\|)",                     False, True))    # Note: identical to above.
        self.assertEqual("als!",                deletetext("PUBG | Play Pals!",     "P",                                False, True))    # Multi-match
        self.assertEqual(" | Play Pals!",       deletetext("PUBG | Play Pals!",     "PUBG",                             False, True))    # Start of string
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "!",                                False, True))    # End of string
    
    def test_strip_text(self):
        #print("TEST: (replacement) deletetext in 'strip' or 'keep-start' mode (true, false)")
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "",                                 True, False))    # Null pattern
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "|",                                True, False))    # Bare delimiter
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "foobar",                           True, False))    # No removal
        self.assertEqual("PUBG | ",             deletetext("PUBG | Play Pals!",     "Play Pals",                        True, False))    # Normal removal
        self.assertEqual("PUBG | ",             deletetext("PUBG | Play Pals!",     "Pals|Play",                        True, False))    # Multiple removal
        self.assertEqual("PUBG",                deletetext("PUBG | Play Pals!",     " \| Play Pals",                    True, False))    # Escaped delimiter removal
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "...Play",                          True, False))    # Not non-regex removal 
        self.assertEqual("PUBG",                deletetext("PUBG | Play Pals!",     "regex(...Play)",                   True, False))    # Regex removal
        self.assertEqual("PUBG | ",             deletetext("PUBG | Play Pals!",     "regex((P(l)(ay)))|Pa",             True, False))    # Multiple removal, multi-in-one regex      
        self.assertEqual("PUBG | ",             deletetext("PUBG | Play Pals!",     "regex(P(l))|ay",                   True, False))    # Multiple removal, multiple regex
        self.assertEqual("PUBG | ",             deletetext("PUBG | Play Pals!",     "regex(P((l\|a)(a\|l))(y\|s))",     True, False))    # Regex removal with delimiters
        self.assertEqual("PUBG ",               deletetext("PUBG | Play Pals!",     "regex(\\\\\\|)",                   True, False))    # Regex removal of escaped delimier / special regex character
        self.assertEqual("PUBG ",               deletetext("PUBG | Play Pals!",     r"regex(\\\|)",                     True, False))    # Note: identical to above.
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "P",                                True, False))    # Multi-match
        self.assertEqual("",                    deletetext("PUBG | Play Pals!",     "PUBG",                             True, False))    # Start of string
        self.assertEqual("PUBG | Play Pals",    deletetext("PUBG | Play Pals!",     "!",                                True, False))    # End of string

    def test_remove_text(self):
        #print("TEST: (replacement) deletetext in 'remove' or 'keep-all' mode (true, true)")
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "",                                 True, True))     # Null pattern
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "|",                                True, True))     # Bare delimiter
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "foobar",                           True, True))     # No removal
        self.assertEqual("PUBG | !",            deletetext("PUBG | Play Pals!",     "Play Pals",                        True, True))     # Normal removal
        self.assertEqual("PUBG |  !",           deletetext("PUBG | Play Pals!",     "Pals|Play",                        True, True))     # Multiple removal
        self.assertEqual("PUBG!",               deletetext("PUBG | Play Pals!",     " \| Play Pals",                    True, True))     # Escaped delimiter removal
        self.assertEqual("PUBG | Play Pals!",   deletetext("PUBG | Play Pals!",     "...Play",                          True, True))     # Not non-regex removal 
        self.assertEqual("PUBG Pals!",          deletetext("PUBG | Play Pals!",     "regex(...Play)",                   True, True))     # Regex removal
        self.assertEqual("PUBG |  ls!",         deletetext("PUBG | Play Pals!",     "regex((P(l)(ay)))|Pa",             True, True))     # Multiple removal, multi-in-one regex      
        self.assertEqual("PUBG |  Pals!",       deletetext("PUBG | Play Pals!",     "regex(P(l))|ay",                   True, True))     # Multiple removal, multiple regex
        self.assertEqual("PUBG |  !",           deletetext("PUBG | Play Pals!",     "regex(P((l\|a)(a\|l))(y\|s))",     True, True))     # Regex removal with delimiters
        self.assertEqual("PUBG  Play Pals!",    deletetext("PUBG | Play Pals!",     "regex(\\\\\\|)",                   True, True))     # Regex removal of escaped delimier / special regex character
        self.assertEqual("PUBG  Play Pals!",    deletetext("PUBG | Play Pals!",     r"regex(\\\|)",                     True, True))     # Note: identical to above.
        self.assertEqual("UBG | lay als!",      deletetext("PUBG | Play Pals!",     "P",                                True, True))     # Multi-match
        self.assertEqual(" | Play Pals!",       deletetext("PUBG | Play Pals!",     "PUBG",                             True, True))     # Start of string
        self.assertEqual("PUBG | Play Pals",    deletetext("PUBG | Play Pals!",     "!",                                True, True))     # End of string
    
    def test_regularize(self):
        #print("TEST: (replacement) regularize")
        self.assertEqual("",            regularize(""))                 # Null pattern
        self.assertEqual(r"A\+B\*C\.",  regularize("A+B*C."))           # Not regex
        self.assertEqual("",            regularize("regex()"))          # Null regex
        self.assertEqual("A+B*C.",      regularize("regex(A+B*C.)"))    # Regex
        self.assertEqual(r"regex\(",    regularize("regex("))           # Malformed regex
        self.assertEqual(r"A\+regex\(", regularize("A+regex("))         # Not regex
        
    def test_split_delimiter_escape(self):
        #print("TEST: (replacement) split_delimiter_escape")
        self.assertListEqual([''],          split_delimiter_escape('', '+', '?'))           # Null pattern
        self.assertListEqual(['A', 'B'],    split_delimiter_escape('A+B', '+', '?'))        # Delimit
        self.assertListEqual(['A+B'],       split_delimiter_escape('A?+B', '+', '?'))       # Escape the delimiter
        self.assertListEqual(['A?', 'B'],   split_delimiter_escape('A??+B', '+', '?'))      # Escape the escape character
        self.assertListEqual(['A?+B'],      split_delimiter_escape('A???+B', '+', '?'))     # Three escapes becomes ?? ?+ becomes ?+
        self.assertListEqual(['A?B'],       split_delimiter_escape('A?B', '+', '?'))        # Escape character remains when preceeding neither delimiter nor escape character
        self.assertListEqual(['',''],       split_delimiter_escape('+', '+', '?'))          # Bare delimiter
        self.assertListEqual(['?'],         split_delimiter_escape('?', '+', '?'))          # Bare escape character
                                                                                        
        self.assertListEqual([''],          split_delimiter_escape('', '+', '\\'))          # Repeat above tests using \ as escape character,
        self.assertListEqual(['A', 'B'],    split_delimiter_escape('A+B', '+', '\\'))       #  which gets messy if you're not using raw strings
        self.assertListEqual(['A+B'],       split_delimiter_escape('A\\+B', '+', '\\'))     
        self.assertListEqual(['A\\', 'B'],  split_delimiter_escape('A\\\\+B', '+', '\\'))      
        self.assertListEqual(['A\\+B'],     split_delimiter_escape('A\\\\\\+B', '+', '\\'))     
        self.assertListEqual([r'A\+B'],     split_delimiter_escape(r'A\\\+B', '+', '\\'))   # Note: identical to above. Note: can't do r'\' for last term; raw strings can't end in backslashes.
        self.assertListEqual(['A\\B'],      split_delimiter_escape('A\\B', '+', '\\'))
        self.assertListEqual(['',''],       split_delimiter_escape('+', '+', '\\'))
        self.assertListEqual(['\\'],        split_delimiter_escape('\\', '+', '\\'))
        
  
if __name__ == '__main__':
    unittest.main()

