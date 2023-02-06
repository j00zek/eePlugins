# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
from Components.j00zekSkinTranslatedLabels import translate as _
#from enigma import eServiceCenter
import os

try: #obejscie dla VTI 11, ktore nie ma konwertera genre
    from Components.Converter.genre import getGenreStringSub
except Exception:
    def getGenreStringSub(hn = None, ln = None):
        return ''

DBG = False
FULLDBG = True

try:
    if DBG: from Components.j00zekComponents import j00zekDEBUG
except Exception:
    DBG = False

if DBG == False:
    FULLDBG = False

def getExtendedMovieDescription(ref): # taken from MovieInfoParser.py coded by plnick@vuplus-support.org
        f = None
        extended_desc = ""
        name = ""
        extensions = (".txt", ".info")
        info_file = os.path.realpath(ref.getPath())
        name = os.path.basename(info_file)
        ext_pos = name.rfind('.')
        if ext_pos > 0:
                name = (name[:ext_pos]).replace("_", " ")
        else:
                name = name.replace("_", " ")
        for ext in extensions:
                if os.path.exists(info_file + ext):
                        f = info_file + ext
                        break
        if not f:
                ext_pos = info_file.rfind('.')
                name_len = len(info_file)
                ext_len = name_len - ext_pos
                if ext_len <= 5:
                        info_file = info_file[:ext_pos]
                        for ext in extensions:
                                if os.path.exists(info_file + ext):
                                        f = info_file + ext
                                        break
        if f:
                with open(f, "r") as txtfile:
                        extended_desc = txtfile.read()

        return (name, extended_desc)

class j00zekModEventName(Poll, Converter, object):
    NAME = 0
    SHORT_DESCRIPTION = 1
    EXTENDED_DESCRIPTION = 2
    FULL_DESCRIPTION = 3
    ID = 4
    NAME_NOW = 5
    NAME_NEXT = 6
    GENRE = 7
    RATING = 8
    SRATING = 9
    PDC = 10
    PDCTIME = 11
    PDCTIMESHORT = 12
    ISRUNNINGSTATUS = 13
    EPGPIC = 14

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.picFileName = ''
        self.poll_interval = 100
        self.WaitForEvent = True
        
        if type == "Description":
            self.type = self.SHORT_DESCRIPTION
        elif type == "ExtendedDescription":
            self.type = self.EXTENDED_DESCRIPTION
        elif type == "FullDescription":
            self.type = self.FULL_DESCRIPTION
        elif type == "ID":
            self.type = self.ID
        elif type == "NameNow":
            self.type = self.NAME_NOW
        elif type == "NameNext":
            self.type = self.NAME_NEXT
        elif type == "Genre":
            self.type = self.GENRE
        elif type == "Rating":
            self.type = self.RATING
        elif type == "SmallRating":
            self.type = self.SRATING
        elif type == "Pdc":
            self.type = self.PDC
        elif type == "PdcTime":
            self.type = self.PDCTIME
        elif type == "PdcTimeShort":
            self.type = self.PDCTIMESHORT
        elif type == "IsRunningStatus":
            self.type = self.ISRUNNINGSTATUS
        elif type.startswith('isEPGpic:'):
            self.type = self.EPGPIC
            self.picFileName = type.split(':')[1]
        else:
            self.type = self.NAME

    def setPoll(self, intervalMS, isEnabled, info):
        self.poll_interval = intervalMS
        self.poll_enabled = isEnabled
        if DBG and info != '': j00zekDEBUG(info)

    @cached
    def getBoolean(self):
        event = self.source.event
        if event is None:
            return False
        if self.type == self.PDC:
            if event.getPdcPil():
                return True
        return False

    boolean = property(getBoolean)

    @cached
    def getText(self):
        event = self.source.event
        if event is None:
            try:
                #recorded movie description
                if hasattr(self.source, 'service') and self.type in (self.SHORT_DESCRIPTION , self.EXTENDED_DESCRIPTION, self.FULL_DESCRIPTION):
                    service = self.source.service
                    if service:
                        ret = getExtendedMovieDescription(service)
                        self.setPoll(1000,False,"[j00zekModEventName:getText] event is None, movie description found")
                        return ret[1]
                #recorded movie name
                elif self.type == self.NAME and hasattr(self.source, 'service'):
                    service = self.source.getCurrentService()
                    if service and service.type in (4097,5001,5002):
                        sname = service.getPath().split('/')[-1].rsplit('.', 1)[0].replace('_', ' ')
                        self.setPoll(1000,False,"[j00zekModEventName:getText] event is None, movie name found")
                        return sname
                elif self.WaitForEvent == True:
                    self.setPoll(100,True,"[j00zekModEventName:getText] event is None, wating 100ms")
                    self.WaitForEvent = False
                    return ""
            except Exception as e:
                if DBG: j00zekDEBUG("[j00zekModEventName:getText] exception" % str(e))
            self.setPoll(1000,False,"[j00zekModEventName:getText] event is None, polling every second")
            return ""
        else:
            self.setPoll(1000,False,"")
            self.WaitForEvent = True #for next event
            
        if self.type == self.NAME:
            retVal = event.getEventName()
            if FULLDBG: j00zekDEBUG("[j00zekModEventName:getText] self.type == self.NAME = '%s'" % retVal)
            return retVal
        elif self.type == self.SRATING:
            rating = event.getParentalData()
            if rating is None:
                return ""
            else:
                country = rating.getCountryCode()
                age = rating.getRating()
                if age == 0:
                    return _("All ages")
                elif age > 15:
                    return _("bc%s") % age
                else:
                    age += 3
                    return " %d+" % age
        elif self.type == self.RATING:
            rating = event.getParentalData()
            if rating is None:
                return ""
            else:
                country = rating.getCountryCode()
                age = rating.getRating()
                if age == 0:
                    return _("Rating undefined")
                elif age > 15:
                    return _("Rating defined by broadcaster - %d") % age
                else:
                    age += 3
                    return _("Minimum age %d years") % age
        elif self.type == self.GENRE:
            genre = event.getGenreData()
            if genre is None:
                return ""
            else:
                return getGenreStringSub(genre.getLevel1(), genre.getLevel2())
        elif self.type == self.EPGPIC:
            if FULLDBG: j00zekDEBUG("[j00zekModEventName:getText] self.type == self.EPGPIC = '%s'" % self.picFileName)
            return self.picFileName
        elif self.type == self.NAME_NOW:
            return pgettext("now/next: 'now' event label", "Now") + ": " + event.getEventName()
        elif self.type == self.NAME_NEXT:
            return pgettext("now/next: 'next' event label", "Next") + ": " + event.getEventName()
        elif self.type == self.ID:
            return str(event.getEventId())
        elif self.type == self.PDC:
            if event.getPdcPil():
                return _("PDC")
            return ""
        elif self.type in (self.PDCTIME, self.PDCTIMESHORT):
            pil = event.getPdcPil()
            if pil:
                if self.type == self.PDCTIMESHORT:
                    return _("%02d:%02d") % ((pil & 0x7C0) >> 6, (pil & 0x3F))
                return _("%d.%02d. %02d:%02d") % ((pil & 0xF8000) >> 15, (pil & 0x7800) >> 11, (pil & 0x7C0) >> 6, (pil & 0x3F))
            return ""
        elif self.type == self.ISRUNNINGSTATUS:
            if event.getPdcPil():
                running_status = event.getRunningStatus()
                if running_status == 1:
                    return _("not running")
                if running_status == 2:
                    return _("starts in a few seconds")
                if running_status == 3:
                    return _("pausing")
                if running_status == 4:
                    return _("running")
                if running_status == 5:
                    return _("service off-air")
                if running_status in (6,7):
                    return _("reserved for future use")
                return _("undefined")
            return ""
        elif self.type in (self.SHORT_DESCRIPTION , self.EXTENDED_DESCRIPTION, self.FULL_DESCRIPTION):
            description = str(event.getShortDescription()).strip()
            extended = str(event.getExtendedDescription()).strip()
            if config.plugins.j00zekCC.enTMDBratingFirst.value:
                tmdbRating = 'TBC'
            else:
                tmdbRating = ''
            if config.plugins.j00zekCC.enDescrType.value == '1' or self.type == self.SHORT_DESCRIPTION:
                return tmdbRating + description.strip()
            elif config.plugins.j00zekCC.enDescrType.value == '2' or self.type == self.EXTENDED_DESCRIPTION:
                retVal = extended or description
                if DBG: j00zekDEBUG("[j00zekModEventName:getText] self.type == self.EXTENDED_DESCRIPTION = '%s'" % retVal)
                return retVal
            elif config.plugins.j00zekCC.enDescrType.value == '3' or self.type == self.FULL_DESCRIPTION:
                if description and extended:
                    if description[0:20] == extended[0:20]:
                        return extended
                return tmdbRating + description + '\n' + extended
            elif config.plugins.j00zekCC.enDescrType.value == '4':
                if description and extended: 
                    extendedCut = extended[:len(description) + 10].replace('\n',' ').strip().replace('  ',' ').split(' ')
                    descrWords = description.replace('\n',' ').strip().replace('  ',' ').split(' ')
                    if len(descrWords) > 0:
                        wordCount = 0
                        for word in descrWords:
                            if word in extendedCut:
                                wordCount += 1
                        if wordCount >= len(descrWords) * 0.75:
                            return tmdbRating + extended
                return tmdbRating + description + extended
                      

    text = property(getText) 