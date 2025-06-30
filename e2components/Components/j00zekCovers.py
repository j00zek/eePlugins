#######################################################################
#
#    Covers downloader
#    Coded by j00zek (c)2020
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem renderera
#    Please respect my work and don't delete/change name of the renderer author
#
#    Nie zgadzam sie na wykorzystywanie tego skryptu w projektach platnych jak np. Graterlia!!!
#
#    Prosze NIE dystrybuowac tego skryptu w formie archwum zip, czy tar.gz
#    Zgadzam sie jedynie na dystrybucje z repozytorium opkg
#    
#######################################################################

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from twisted.web import client, error as weberror
from twisted.web.client import getPage, downloadPage
try:
    from Components.j00zekComponents import isINETworking
except Exception:
    from j00zekComponents import isINETworking

def WebCover(ret):
    print("[j00zekCovers:WebCover] >>>")
    self.gettingDataFromWEB = False
    self.setCover(WebCoverFile)
    return

def dataError(error = '', errorType='downloading'):
    printDEBUG("Error %s data %s" % ( str(errorType),str(error)))
    self.gettingDataFromWEB = False
    return
            
def HTML(txt):
    return txt.replace(' ','%20').replace('&', '%26')

def readTmBD(data, movieYear, isMovie,myMovie):
    printDEBUG("[j00zekCovers:readTmBD] >>>") #DEBUG
    f = open('/tmp/TmBD.AFP.webdata', 'w')
    f.write(data)
    f.close
    if isMovie == True:
        try: 
            list = json.loads(data)
        except:
            self.gettingDataFromWEB = False
            return
        data=None # some cleanup, just in case
        if 'total_results' in list:
            coverPath=''
            overview=''
            release_date=''
            id=''
            otitle=''
            original_language=''
            title=''
            popularity=''
            coverUrl = ''
            vote_average=''
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>> znajdowanie najlepszego kandydata z listy
            selectedIndex = 0
            selectedIndexScore = 0
            currIndex = 0
            myMovieLC =myMovie.decode('utf-8', 'ignore').lower()
            if list['total_results'] > 1:
                for myItem in list['results']:
                    currScore = 0
                    if myMovieLC == myItem['original_title'].decode('utf-8', 'ignore').lower(): currScore += 10 #jesli org tytul jest taki sam to najwyzszy priorytet
                    if myMovieLC == myItem['title'].decode('utf-8', 'ignore').lower(): currScore += 5 #jesli tytul jest taki sam to drugi najwyzszy priorytet
                    if movieYear != '' and movieYear == myItem['release_date']: currScore += 5 #w efekcie daje w polaczeniu z title takia sama wage jak ortitle
                    if myItem['original_language'] == 'pl': currScore += 4 #wybor wedlug priorytetu jezyka
                    elif myItem['original_language'] == 'en': currScore += 3
                    elif myItem['original_language'] == 'de': currScore += 2
                    elif myItem['original_language'] == 'fr': currScore += 1
                    printDEBUG(">>> film '%s'-analiza indeksu %d(%s): currScore=%d, selIndex=%d, selScore=%d" %(myMovie,
                                                    currIndex, myItem['title'],currScore, selectedIndex, selectedIndexScore))
                    if currScore > selectedIndexScore:
                        selectedIndexScore = currScore
                        selectedIndex = currIndex
                    currIndex += 1
            # pobieranie danych dla wybranego filmu
            myItem = list['results'][selectedIndex]
            if not myItem['poster_path'] is None:
                coverPath=myItem['poster_path'].encode('ascii','ignore')
            overview=myItem['overview']
            release_date=myItem['release_date']
            id=myItem['id']
            otitle=myItem['original_title']
            original_language=myItem['original_language']
            title=myItem['title']
            popularity='{:.2f}'.format(myItem['popularity'])
            vote_average='{:.2f}'.format(myItem['vote_average'])
            if coverPath != '':
                coverUrl = "http://image.tmdb.org/t/p/%s%s" % (myConfig.coverfind_themoviedb_coversize.value, coverPath)
                coverUrl = coverUrl.replace('\/','/')
            Pelny_opis=overview + '\n\n' + _('Released: ') + release_date + '\n' + \
                                            _('Original title: ') + otitle +'\n' + _('Original language: ') + \
                                            original_language +'\n' + _('Popularity: ') + popularity + '\n' + \
                                            _('Score: ') + vote_average + '\n'
            printDEBUG("========== Dane filmu %s ==========\nPlakat: %s,\n%s\n====================" %(title, coverUrl,Pelny_opis))
            printDEBUG(WebDescrFile)
            if not path.exists(WebDescrFile) and Pelny_opis.strip() != '':
                with open(WebDescrFile, 'w') as WDF:
                    WDF.write(Pelny_opis)
                    WDF.close()
            if FoundDescr == False:
                printDEBUG("FoundDescr == False")
                with open(WebDescrFile,'r') as descrTXT:
                    myDescr = descrTXT.read()
                    self.setDescription(myDescr)
            if FoundCover == False or coverUrl != '': #no need to download cover, if we have it, or if there is no cover url. ;)
                downloadPage(coverUrl,WebCoverFile).addCallback(WebCover).addErrback(dataError)
                
        else:
            self.gettingDataFromWEB = False
            return
    else: #dane seriali sa w xml-u!!!!
        list = re.findall('<seriesid>(.*?)</seriesid>.*?<language>(.*?)</language>.*?<SeriesName>(.*?)</SeriesName>.*?<banner>(.*?)</banner>.*?<Overview>(.*?)</Overview>.*?<FirstAired>(.*?)</FirstAired>', data, re.S)
        printDEBUG("len(list) = %s" % len(list)) #DEBUG
        if list is not None and len(list)>0:
            #print">>>>>>>>>>>>>>>>>>>>>>>>>",list
            idx = 0
            seriesid, original_language, SeriesName, banner, overview, FirstAired = list[idx]
            coverUrl = "http://www.thetvdb.com%s" % banner
            printDEBUG("coverUrl = %s" % coverUrl)
            if FoundDescr == False:
                printDEBUG("Series FoundDescr == False")
                myDescr = (overview + '\n\n' + _('Released: ') + FirstAired + '\n' + _('Original title: ') + SeriesName +'\n' + _('Original language: ') + \
                           original_language +'\n')
                self.setDescription(myDescr)
                with open(WebDescrFile, 'w') as WDF:
                    WDF.write(self["Description"].getText() )
                    WDF.close()
            if FoundCover == False: #no need to download cover, if we have it. ;)
                downloadPage(coverUrl,WebCoverFile).addCallback(WebCover).addErrback(dataError,errorType='downloading cover')
        else:
            self.gettingDataFromWEB = False
            return
        

#for tests outside e2
if __name__ == '__main__':
    myMovie=DecodeNationalLetters(myMovie)
    if myConfig.PermanentCoversDescriptons.value == True:
        WebCoverFile='%s/%s.jpg' % (self.filelist.getCurrentDirectory(), getNameWithoutExtension(self.filelist.getFilename()) )
        WebDescrFile='%s/%s.txt' % (self.filelist.getCurrentDirectory(), getNameWithoutExtension(self.filelist.getFilename()) )
    else:
        WebCoverFile='/tmp/%s.AFP.jpg' % getNameWithoutExtension(self.filelist.getFilename())
        WebDescrFile='/tmp/%s.AFP.txt' % getNameWithoutExtension(self.filelist.getFilename())
            
    printDEBUG("mySeries = %s" % self.filelist.getFilename())
    printDEBUG("Description = %s" % self["Description"].getText())
    if re.search('[Ss][0-9]+[Ee][0-9]+', myMovie):
        printDEBUG("re.search('[Ss][0-9]+[Ee][0-9]+'")
        seriesName=re.sub('[Ss][0-9]+[Ee][0-9]+.*','', myMovie, flags=re.I)
        url = "http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s" % (HTML(seriesName),myConfig.coverfind_language.value)
        isMovie = False
    elif re.search('odc[_ ]*[0-9]+', self.filelist.getFilename()): #odc w nazwie pliku
        printDEBUG("SERIAL >>> odc w nazwie pliku")
        seriesName=re.sub('odc.*','', myMovie, flags=re.I).replace('(','').replace(')','')
        url = "http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s" % (HTML(seriesName),myConfig.coverfind_language.value)
        isMovie = False
    elif re.search('odc[\. ]+[0-9]+', self["Description"].getText()): #odc w opisie
        printDEBUG("re.search('odc.*[0-9]+'")
        seriesName= myMovie #re.sub('.odc_.*','', myMovie, flags=re.I)
        url = "http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s" % (HTML(seriesName),myConfig.coverfind_language.value)
        isMovie = False
    else:
        url = "http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=%s" % (HTML(myMovie),myConfig.coverfind_language.value)
        isMovie = True
    if self.gettingDataFromWEB == True:
        printDEBUG("[GetFromTMDBbyName] getPage running, skip '%s'this time" % url) #DEBUG
    else:
        printDEBUG("[GetFromTMDBbyName] url: " + url) #DEBUG
        self.gettingDataFromWEB = True
        getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(readTmBD,movieYear,isMovie,myMovie).addErrback(dataError,errorType='getting data')
