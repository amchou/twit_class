################# twtt.py #####################################################
#Amanda Chou
#
#Takes a raw tweet file (first arg), with each line denoting one tweet, and returns a normalized tweet file (2nd arg)
#Some stylistic liberties taken & documented
#Wordlists may be further expanded to improve robustness.
###############################################################################

import sys, re, HTMLParser, NLPlib, bonus_twtt

#getting arguments from command line and instantiating external functions
tweetFile = sys.argv[1]
writeFile = sys.argv[2]
h = HTMLParser.HTMLParser()
tagger = NLPlib.NLPlib()

####### Word Lists / Definitions #############################################
abbrevFile = r'../Wordlists/abbrev.english'
pnFile = r'../Wordlists/pn_abbrev.english'

#for pn_abbrev.english and extras: delete following newline always (ignore etc. since usually EOS)
extras = r'e.g.,E.g.,i.e.,I.e.,viz.'

#for abbrev.english and dates and geo: delete newline unless followed by space+Capital
dates = r'Jan.,Feb.,Mar.,Apr.,Jun.,Jul.,Aug.,Sep., Sept.,Oct.,Nov.,Dec., Mon.,Tue.,Wed.,Thu.,Fri.,Sat.,Sun.'
geos = r'Ont.,Que.'
dates = dates.split(',')
extras = extras.split(',')
geos = geos.split(',')

urls = ['com','org','ca']
reTags = re.compile(r'(?P<at>@?)(?P<tagType><a.+?>)(?P<content>.+?(?=<))(?P<tagEnd></a>)')

#############################################################################

def tagRepl(m):
#fixes html tagged items according to given rules (3 types: web, username, hashtag)
    #if link, remove both tag and content
    if 'tweet-url web' in m.group("tagType"): return ''
    #if username, remove '@' and tags
    if 'tweet-url username' in m.group("tagType"): return m.group("content")
    #if hashtag, remove '#' (first char in content) and tags
    if 'tweet-url hashtag' in m.group("tagType"): return m.group("content")[1:]
    #delete other kinds of html tags: e.g. @<a class="tweet-url list-slug"
    else: return ''     

def abbrevRepl(m):
#replacement function for re.sub, given this match: r'(\b[a-zA-Z\.]+?)( )(\.)([.!?]*["\']? ?)(\n)([, :;-]*?[0-9a-zA-Z])'
#strategically removes newlines created by baseline sentence-breaking rule by taking abbreviations into account   
    #if match is in extras list or pn_abbrev.english, remove newline:
    if ((m.group(1)+m.group(3) in extras) or (inFile(m.group(1)+m.group(3),pnFile))):
        return m.group(1) + m.group(3) + m.group(4) + m.group(6)

    #if match is in dates or abbrev.english(but not pn_abbrev.english), remove newline unless followed by Capital
    if ((m.group(1)+m.group(3) in dates) or (m.group(1)+m.group(3) in geos) or (inFile(m.group(1)+m.group(3), abbrevFile))):
        if re.match(r'[^A-Z]',m.group(6)):
            return m.group(1) + m.group(3) + m.group(4) + m.group(6)
        
    #else keep newline, and leave period as separate token
    else: return m.group()

def inFile(word,wordFile):
#checks if 'word' is in given 'file', a list of words each in its own line (e.g abbrev.english file)
    with open (wordFile, 'r') as f:        
        for line in f:
            if word == line.strip():
                return True
        return False

def splitJoin(rePunc,sents):
#returns string sents with the addition of spaces on either side of every occurrence of regex pattern rePunc
#used in tokenization to separate punctuation or symbols from text    
    split = re.split(rePunc,sents)
    join = ' '.join(split)
    return join

def twt2Sents(tweet, last=False):
#takes a tweet (string) and inserts newlines at sentence boundaries (done iteratively); strips begin/trailing spaces
    #first, insert \n after all groups of [.!?] potentially followed by a quotation, which is followed by space/end of string
    #add a space before the EOS punctuation to aid in tokenization (undo as needed below)
    tweet = re.sub(r'([.!?]+)(["\']?)(\s|$)',r' \1\2\3\n',tweet)

    ########## Special Cases ##########
    #Note that while some of these could be nested, they were done on a case-by-case basis to improve readability and modularity
    #Since many cases are rare, the increased computation time should be negligible
    
    #For cases like: "On life, the universe, and everything, of course.Pluto too." ==> add newline before start of sentence
    tweet = re.sub(r'([a-z]\.)([A-Z])', r'\1 \n\2',tweet)
    
    #for a.b. or A.B., likely abbreviation: remove newline unless followed by space+Capital (abbreviation could extend to the left but don't care)
    #keep ending period as part of abbrev. token
    tweet = re.sub(r'([a-zA-Z]\.[a-zA-Z])( )(\.)([.!?]*["\']? ?)(\n)([^A-Z])',r'\1\3\4\6',tweet)
    tweet = re.sub(r'([a-zA-Z]\.[a-zA-Z])( )(\.)([.!?]*["\']? ?)(\n)([A-Z])',r'\1\3\4\5\6',tweet)

    #but if this abbreviation is start of line, remove newline even if followed by Capital (e.g.: U.S. Feds)
    tweet = re.sub(r'((\A|\s)([a-zA-Z]\.){2,} )(\n)',r'\1',tweet)

    #for a.m./p.m., remove newline if followed by lowercase or **2-3** Capitals (e.g. ET, EST)
    tweet = re.sub(r'([aApP]\.[mM]\. )(\n)([a-z]|[A-Z]{2,3})',r'\1\3',tweet)

    #St.: delete newline if previous word lowercase or at start of line, and next word Capitalized
    #e.g. 'Meet at St. John's,' or 'St. John is great.'
    tweet = re.sub(r'(\A|\s|[a-z]+? )(St)( )(\. )(\n)([A-Z])',r'\1\2\4\6',tweet)

    #[nN]o. followed by [0-9]
    tweet = re.sub(r'([nN]o)( )(\. )(\n)([0-9])',r'\1\3\5',tweet)
  
    #now check for abbreviations using predefined lists either defined in this script or given 'a1' folder:
    tweet = re.sub(r'(\b[a-zA-Z\.]+?)( )(\.)([.!?]*["\']? ?)(\n)([, :;-]*?[0-9a-zA-Z])', abbrevRepl, tweet)
    
    #remove additional URLs (non-HTML-tagged ones, since those are already gone); preserve punctuation at end if needed
    #note: Prof. Rudzicz indicated in lecture we should remove all links, even beyond html-tagged ones
    tweet = re.sub(r'(www\.|http:)([\./\w-]*[\w/])*(?=[^\w]|$)', '', tweet)                             #e.g. www.ABC.com
    tweet = re.sub(r'([:\.\w/-]*\.)(com|org|ca|gov|co|net|edu)([\./\w-]*[\w/])*(?=[^\w]|$)', '', tweet) #e.g. ABC.com/blah

    ########## Clean up #########
    #strip each line in tweet of leading and trailing whitespace
    tweet = tweet.splitlines()                         #list of lines within tweet
    tweet = '\n'.join(s.strip() for s in tweet)        #remove whitespace and join with newlines
    tweet = re.sub(r'[ ]+',' ',tweet)                  #reduce any group of >1 space to just one space
    
    #if end of tweet is not currently a newline (i.e. if sentence wasn't formally ended), insert a newline
    if tweet:
        if tweet[-1] <> '\n': tweet = tweet + '\n'
    else: tweet = '\n'                                 #tweet empty; put in extra newline
    return tweet

def sents2Tokens(sents):
#converts string of sentences for one tweet into list of sentences, which are each a list of tokens
#sents argument will not have more than one consecutive space between chars
    #keep some punctuation together (!?.-) 
    groups = [r'([?!]+)',r'(\.{2,})',r'(-{2,})']
    #split up punc that don't usually occur in multiples or groups...e.g. @@@@ or #$*&%$%*
    singles = [r'(\$)',r'(@)',r'(~)',r'(\+)',r'(=)',r'(\()',r'(\))',r'(|)',r'(/)',r'(\*)',
               r'(%)',r'(#)',r'(;)',r'(\[)',r'(\])',r'({)',r'(})',r'(<)',r'(>)',r'(")',r'(`)']
    for l in groups+singles:
        sents = splitJoin(l,sents)

    #(,:) pad space if colon/comma not sandwiched by digits (time/ratio 1:23,number 10,000)
    sents = re.sub(r'([^\d])(:|,)(.)',r'\1 \2 \3', sents)
    sents = re.sub(r'(.)(:|,)([^\d])',r'\1 \2 \3', sents)
 
    #(&) keep as whole token if sandwiched by letters (AT&T, Q&A)
    sents = re.sub(r'([^a-zA-Z])(&)(.)',r'\1 \2 \3', sents)
    sents = re.sub(r'(.)(&)([^a-zA-Z])',r'\1 \2 \3', sents)
    
    #(') clitics: n't, 'll, 'm, 've, 're, 's and s'(plural possessive-> keep 's' with word and split off apostrophe)
    sents = re.sub(r'([a-zA-Z])(n\'t\b|\'ll\b|\'m\b|\'ve\b|\'re\b|\'s\b)',r'\1 \2', sents)
    sents = re.sub(r'((?<=[a-z])s)(\'(?![a-zA-Z]))', r'\1 \2', sents)
    
    #(') other cases: split otherwise (apostrophe often used as quotation marks); but leave if sandwiched by letters (e.g. Qu'ok)
    #need to make sure not to mess up the clitics
    sents = re.sub(r'( |\A)(\')(?!ll\b|m\b|ve\b|re\b|s\b)',r'\1\2 ',sents)  #immediately preceding a non-clitic (start quote)
    sents = re.sub(r'([\w\.!?])(\')( |$)',r'\1 \2\3',sents)                 #closing quotation

    #(-) dashes often attached to names in sign-offs: e.g. -Adam; break these off
    sents = re.sub(r'(\s|\A)(-)([a-zA-Z])',r'\1\2 \3',sents)
    
    lines = sents.splitlines()
    tokens = [l.split() for l in lines]
    return tokens     
                
def preprocess(lastLine, reTags, curLine=None):
#preprocesses one tweet (lastLine) by removing html tags, unescaping html, breaking into sentences, tokenizing & tagging
#returns tweet with sentences separated, ending in a newline
    untag = reTags.sub(tagRepl,lastLine)    #remove html tags
    unescape = h.unescape(untag)            #unescape html code using standard library
    sents = twt2Sents(unescape)             #break into sentences
    tokens = sents2Tokens(sents)            #tokenize
    #print tokens
    tags = []
    for t in tokens:        
        tags.append(tagger.tag(t))

    #format to write it in file as required: token/tag token/tag \n token/tag token/tag
    writeList = []
    for s,sent in enumerate(tokens):
        for t,toke in enumerate(sent):
            tagged = sent[t] + '/' + tags[s][t]
            tagged = bonus_twtt.post(tagged)        #bonus_twtt: post-processing to correct NLPlib tags
            writeList.append(tagged)
            if t < len(sent):
                writeList.append(' ')
        writeList.append('\n')

    p = ''.join(writeList)

    if not curLine:                                 #end of tweets, remove trailing newline
        p = p[:-1]     
    return p

def main():
#opens read/write files and uses preprocess() to write the output file
    lastLine = None
    
    with open (writeFile, 'w') as f:
        with open (tweetFile, 'r') as r:
            for line in r:
                if not lastLine == None:
                    f.write(preprocess(lastLine, reTags, line))
                    f.write('|\n')
                lastLine = line
        f.write(preprocess(lastLine, reTags))
    return

main()
