#buildarff.py
#given normalized .twt files, builds .arff file for tweet classification
#assumes the optional argument -N for number of tweets to use per file does not exceed the total #


import sys, re

#tags to match
adV = ['RB','RBR','RBS']
wh = ['WDT','WP','WP\$','WRB']
coord = ['CC']
propN = ['NNP','NNPS']
commN = ['NN','NNS']
pastV = ['VBD']

#sets of tokens to match (assumes they represent a whole token, and come before '/')
futV = ['\'ll','will','gonna']

#files to use
firstPerson = r'../Wordlists/First-person'
secondPerson = r'../Wordlists/Second-person'
thirdPerson = r'../Wordlists/Third-person'
slang = r'../Wordlists/Slang'

#numeric attribute names
numerics = ['1st_prs_pron','2nd_prs_pron','3rd_prs_pron','coord_conj','pst_vrb','fut_vrb',
            'comma','col_semi','dash','parenth','ellipse','comm_noun','prop_noun','advrb','wh',
            'mod_slang','caps','avg_sent_len','avg_toke_len','num_sent']

def getAvgSentLen(twt):
#given a tweet twt, return avg sentence length (in tokens) as float
    sLen = []
    for sent in twt:
        if not sent: return 0
        else: sLen.append(len(sent.split(' ')))
    if len(sLen) == 0: return 0
    else: return float(sum(sLen))/float(len(sLen))

def getAvgTokeLen(twt):
#given twt (list of sentences in a tweet), return avg length of tokens as float
#excludes punctuation tokens as defined in A1-Table 1b (Penn POS tagset)
    tLen = []
    for sent in twt:
        for t in sent.split(' '):
            token = t.rsplit('/')[0]
            if token and not re.match(r'[\.!?(),\'";:]+$',token):    
                tLen.append(len(token))
    if len(tLen) == 0: return 0             #if no valid tokens, return 0      
    else: return float(sum(tLen))/float(len(tLen))

def getNumSent(twt):
#given a tweet twt, return total number of sentences (non-empty lines) as int
    numSent = 0
    for sent in twt:
        if sent:
            numSent += 1
    return numSent

def getData(twt):
#for a given tweet twt, returns list to hold data corresponding to specified attributes
    data = []
    data.append(numInFile(firstPerson,twt))
    data.append(numInFile(secondPerson,twt))
    data.append(numInFile(thirdPerson,twt))
    data.append(numTags(coord,twt))
    data.append(numTags(pastV,twt))
    data.append(numTokes(futV,twt) + numReg(re.compile(r'going/.+? to/.+? [^ ]+?VB'),twt))
    data.append(numReg(re.compile(r',/'),twt))      #this won't include 'commas' in 10,000 -> should it?
    data.append(numReg(re.compile(r':/'),twt) + numReg(re.compile(r';/'),twt))
    data.append(numReg(re.compile(r'-/'),twt))      #won't include hyphens in compound words, like pos-tag
    data.append(numReg(re.compile(r'\(/'),twt) + numReg(re.compile(r'\)/'),twt))
    data.append(numReg(re.compile(r'\.{2,}/'),twt)) #count all instances of >1 period... sometimes only 2 but still mean ellipse
    data.append(numTags(commN,twt))
    data.append(numTags(propN,twt))
    data.append(numTags(adV, twt))
    data.append(numTags(wh,twt))
    data.append(numInFile(slang,twt))
    data.append(numReg(re.compile(r'(\s|\A)([A-Z]{2,}/)'),twt))
    data.append(getAvgSentLen(twt))
    data.append(getAvgTokeLen(twt))
    data.append((getNumSent(twt)))
    
    #convert all to string for writing to arff file
    data = [str(d) for d in data]
    return data

def numReg(reg, twt):
#returns number of occurrences of a certain RegEx pattern, reg, in a tweet twt
    return len(reg.findall(''.join(twt)))

def numTags(posType, twt):
#returns number of occurrences of a certain posType (given as list of posTags to iterate thru) in twt list
    num = 0
    for tag in posType:
        reg = re.compile(r'/'+tag+r'( |$)')
        num += numReg(reg,twt)
    return num

def numTokes(tokes,twt):
#returns # of occurrences of a particular set of tokens (followed by a /POStag) given as a list
    num = 0
    for t in tokes:
        reg = re.compile(r'( |\A)'+t+r'/')
        num += numReg(reg,twt)
    return num        

def numInFile(wordFile,twt):
#returns number of occurrences of words (case insensitive) in wordFile in tweet twt.
#only matches if word exactly matches a token 
    num = 0
    with open (wordFile, 'r') as f:      
        for line in f:
            word = re.compile(r'(\A| )'+line.strip().lower()+r'/')
            num += len(word.findall(''.join(twt).lower()))
    return num

def main():
    outFile = sys.argv[-1]
    classes=[]
    numTweets = None                #use all tweets unless -# is specified
    for arg in sys.argv[1:-1]:      #omit first arg(script) and last arg(output arff file)
        if arg[0] == '-':
            numTweets = int(arg[1:])
        elif '.twt' in arg:
            s = arg.split(':')
            className = s[0]        #everything before colon if specified, otherwise whole argument
            if ':' in arg:   
                twtFiles = s[1]     #could be a.twt+b.twt+c.twt etc.
            else:
                twtFiles = s[0]
            classes.append([className,twtFiles,numTweets])
        
    with open(outFile,'w') as f:
        #relation
        f.write('@RELATION twit_classification\n\n')
        #attributes
        for n in numerics:
            f.write('@ATTRIBUTE ' + n + ' numeric\n')
        for c in classes:
            c[0] = c[0].split('+')
            c[0] = '+'.join(re.sub(r'(.*?/)(.*?)(\.twt)',r'\2',tw) for tw in c[0])
        f.write('@ATTRIBUTE twit_class {%s}\n\n' % ','.join(str(c[0]) for c in classes))
        
        #data
        f.write('@DATA\n')

        for c in classes:
            tFiles = c[1].split('+')
            #compile tweets needed from every file in class c
            for t in tFiles:
                with open(t,'r') as r:
                    if not numTweets:
                        tSet = r.readlines()
                    else:
                        count = 0
                        tSet = []
                        #if numTweets specified, use this many tweets
                        while count < numTweets:
                            line = r.readline()
                            tSet.append(line)
                            if line.strip() == '|':
                                count += 1
                        #remove last '|'
                        tSet = tSet[:-1]    
                    #now tSet has all the twts we need to compile the arff file
                    #for every individual twt in tSet, getData and write to arff
                    twt = []
                    for line in tSet:
                        if line.strip() != '|':
                            #twt is a list of 'sentences' corresponding to one tweet
                            twt.append(line.strip())
                        else:
                            f.write(','.join(getData(twt)) + ',%s\n' % c[0])
                            twt = []
                    #write data for last tweet (since will not be followed by '|' line)
                    f.write(','.join(getData(twt)) + ',%s\n' % c[0])
    return

main()
