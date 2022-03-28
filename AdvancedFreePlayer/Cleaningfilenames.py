# -*- coding: utf-8 -*-
import re
from os import path

def cleanFile(text, ReturnMovieYear = True, metaFileName = ''):
    if text.endswith('.ts'):
        if metaFileName != '' and path.exists(metaFileName):
            with open(metaFileName,'r') as descrTXT:
                tmpTXT = descrTXT.readline()
                descrTXT.close()
                if tmpTXT.find('::') > -1:
                    ChannelName = tmpTXT.split('::')[1].strip()
                    text = re.sub(ChannelName,'', text, flags=re.I)
        movieYear=''
        #removing exact character combinations
        ExactCutList = ['.ts', '^[12][09][0-9]* [0-9][0-9]* -', '.*[kK]omediowa sobota', '.*[Dd]obre kino', 
                    '.*[Hh]it na sobotę', '.*[Kk]omediowy czwartek', '.*[Ss]iatkówka mężczyzn','.*[Cc]anal.* [Ff]ilm w akcji', '.*[Mm]ocne sobotnie kino',
                    '.*[Zz]akochana jedynka',
                    '.*HD -', '.*TV -', '^[ ]*[-][ ]*']
        for word in ExactCutList:
            text = re.sub(word,'', text, flags=re.I) 
        text = re.sub('(\_|\.|\+)',' ', text, flags=re.I) #cleaning
    else:
        text=getNameWithoutExtension(text)
        # removing found text and everything after it, its's probably a garbage
        cutlist = ['x264','h264','720p','1080p','1080i','2160','PAL','GERMAN','ENGLiSH','ENG', 'RUS', 'WS','DVDRiP','UNRATED','RETAIL','Web-DL','DL','LD','MiC','MD','DVDR','BDRiP','BLURAY','DTS','UNCUT',
                'ANiME','AC3MD','AC3','AC3D','TS','DVDSCR','COMPLETE','INTERNAL','DTSD','XViD','DIVX','DUBBED','LINE.DUBBED','DD51','DVDR9','DVDR5','AVC','WEBHDTVRiP','WEBHDRiP','WEBRiP',
                'WEBHDTV','WebHD','HDTVRiP','HDRiP','HDTV','ITUNESHD','REPACK','SYNC','REAL','PROPER','SUBBED','PLSUBBED']
    
        for word in cutlist:
            #text = re.sub('(\_|\-|\.|\+)'+word+'(\_|\-|\.|\+)','+', text, flags=re.I)
            text = re.sub('(\_|\-|\.|\+)'+word+'(\_|\-|\.|\+).*','.', text, flags=re.I) #assumtion is that everything after garbage is a garbadge too. ;)
        #text = re.sub('(\_|\-|\.|\+)[12][0-9][0-9][0-9]\+.*','', text, flags=re.I) #if there is plus sign after date, date is most probably the garbage, so removing it ;)
    
        #let's take a year, if exists
        try:
            movieYear=re.sub('(\_|\-|\.|\+|\()','', re.search('(\_|\-|\.|\+)[12][09][0-9][0-9]', text, flags=re.I).group() ) #for future use
        except:
            movieYear=''
    
        #removing exact character combinations
        ExactCutList = ['(\_|\-|\.|\+|\()[12][09][0-9][0-9](\_|\-|\.|\+|\))','\[HD\]', 'Lektor[ ]*[-]*[ ]*PL','\(Lektor\)',
                    '^psig-', '-[ ]*zwiastun','[-,]*[ ]*Lektor[ ]*$']
        for word in ExactCutList:
            text = re.sub(word,'', text, flags=re.I) 
        
        text = re.sub('(\_|\-|\.|\+)',' ', text, flags=re.I) #cleaning
    text = re.sub('(  [ ]*)',' ', text, flags=re.I) #merge multiple (2+) spaces into one
    text = text.strip()

    if ReturnMovieYear:
        return text, movieYear
    else:
        return text
    
def DecodeNationalLetters(text):
    #polskie litery
    text = text.replace('ą','a').replace('ę','e').replace('ś','s').replace('ć','c').replace('ż','z').replace('ź','z').replace('ł','l').replace('ń','n')
    text = text.replace('Ą','A').replace('Ę','E').replace('Ś','S').replace('Ć','C').replace('Ż','Z').replace('Ź','Z').replace('Ł','L').replace('Ń','N')
    return text.strip()

def ConvertChars(text):
    CharsTable={ '\xC2\xB1': '\xC4\x85','\xC2\xB6': '\xC5\x9b','\xC4\xBD': '\xC5\xba'}
    for i, j in CharsTable.iteritems():
        text = text.replace(i, j)
    return text

def getNameWithoutExtension(MovieNameWithExtension):
    extLenght = len(path.splitext( path.basename(MovieNameWithExtension) )[1])
    return MovieNameWithExtension[: -extLenght]

