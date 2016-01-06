#post-processing of arff file, correcting the NLPlib tagger
#called in function 'preprocess' in twtt.py
#corrects tags to provide a more accurate normalized tweet file

import re

def post(tags):
    
    #fix consecutive ! or ? to be tagged '.' as EOS punc as opposed to ':' or 'NN'
    tags = re.sub(r'(\A[!?]+/)(.+?$)',r'\1.',tags)
    #consecutive digits, maybe with a comma, tagged as cardinal numbers CD instead of NN
    #also include ##st, ##nd, ##rd, ##th etc. 
    tags = re.sub(r'(\A[0-9]+[,0-9]*?)((st|nd|rd|th)?/)(.+?$)',r'\1\2CD',tags)
    #various symbols (see regex below) as SYM; many are tagged as NN
    #(currently, & and @ are tagged as CC which is not wrong, but more distinct as SYM)
    tags = re.sub(r'(\A[~^@%&*+=/]/)(.+?$)',r'\1SYM',tags)
    #consecutive dashes still tagged as ':' (as NLPlib does with 1 or 2 dashes), not NN
    tags = re.sub(r'(\A[-]+/)(.+?$)',r'\1:',tags)
    #some tweeters (e.g. Stephen Colbert @StephenAtHome) don't capitalize: lower case i's should be tagged as PRP, not NN
    tags = re.sub(r'(\Ai/)(.+?$)',r'\1PRP',tags)
    #time: tag as CD, not NN
    tags = re.sub(r'(\A[0-9]{1,2}:[0-9]{2}/)(.+?)( |$)',r'\1CD',tags)
    #anything tagged CD (e.g. Canada-U.S./CD) but contains no digits, change to NNP
    #NLPlib.py converts nouns to CD if '.' contained in word, which is a bad rule in general
    tags = re.sub(r'(\A[^0-9]+/)(CD$)',r'\1NNP',tags)
    
    return tags
