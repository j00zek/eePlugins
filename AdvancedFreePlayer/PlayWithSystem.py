from Components.config import *
from enigma import eServiceReference
from Screens.InfoBar import MoviePlayer as systemMoviePlayer

class AdvancedFreePlayer(systemMoviePlayer):
    def __init__(self, session,openmovie,opensubtitle, rootID, LastPlayedService, URLlinkName = '', movieTitle='', LastPosition = 0):
        self.session = session
        #if '://' not in uri: uri = 'file://' + uri
        fileRef = eServiceReference(int(rootID),0,openmovie)
        fileRef.setName (movieTitle)
        
        self.Ask_on_movie_stop = False
        #try:
        if config.usage.on_movie_stop.value == "ask":
            self.Ask_on_movie_stop = True
            config.usage.on_movie_stop.value = "quit"
            config.usage.on_movie_stop.save()
        #except:
        #    pass

        self.Ask_on_movie_eof = False
        try:
            if config.usage.on_movie_eof.value == "ask":
                self.Ask_on_movie_eof = True
                config.usage.on_movie_eof.value = "quit"
                config.usage.on_movie_eof.save()
        except:
            pass
            
        systemMoviePlayer.__init__(self, self.session, fileRef)
        self.skinName = "MoviePlayer"
        systemMoviePlayer.skinName = "MoviePlayer"
        
        if self.Ask_on_movie_stop == True:
            config.usage.on_movie_stop.value = "ask"
            config.usage.on_movie_stop.save()
        if self.Ask_on_movie_eof == True:
            config.usage.on_movie_eof.value = "ask"
            config.usage.on_movie_eof.save()