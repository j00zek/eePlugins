# -*- coding: utf-8 -*-
from __init__ import *
from __init__ import translate as _
from Cleaningfilenames import *
from cueSheetHelper import setCut, CUT_TYPE_LAST

from Screens.Screen import Screen

from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox

from Components.ActionMap import ActionMap
from Components.AVSwitch import eAVSwitch
from Components.Label import Label
#from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Sources.StaticText import StaticText
#from Components.ProgressBar import ProgressBar
from Components.config import *
#from Components.GUIComponent import GUIComponent
#from Components.Converter.ConditionalShowHide import ConditionalShowHide
#from Tools.LoadPixmap import LoadPixmap
from os import path, remove, listdir, symlink, system, access, W_OK
import re

from enigma import eTimer,ePoint,eSize,gFont,eConsoleAppContainer,iServiceInformation,eServiceReference, addFont, getDesktop, iPlayableService, fontRenderClass

from skin import parseColor,parseFont

from time import *
import codecs

if path.exists('/usr/local/e2/'):
  KeyMapInfo=_("Player KEYMAP:\n\n\
up/down - position subtitle\n\
left/right - size subtitle\n\
channel up/down - seek+/- subtitle\n\
3/6/9 - seek+ 30sek/2min/5min movie\n\
1/4/7 - seek- 15sek/2min/5min movie\n\
F1 - change ascpect ratio\n\
F2 - change background color\n\
F3 - change type font\n\
F4 - change color font\n\
T - show/hide subtitle\n\
D - Download subtitles\n\
SPACE - show about\n\
F5/OK - infobar\n\
audio - change audio track\n\
")
else:
  KeyMapInfo=_("Player KEYMAP:\n\n\
up/down - position subtitle\n\
left/right - size subtitle\n\
channel up/down - seek+/- subtitle\n\
3/6/9 - seek+ 30s/2min/5min movie\n\
1/4/7 - seek- 15s/2min/5min movie\n\
play - pause on/off\n\
red - change aspect ratio\n\
green - change background color\n\
yellow - change type font\n\
blue - change color font\n\
TV - show/hide subtitle\n\
text - Download subtitles\n\
menu/info - show about\n\
ok - infobar\n\
audio - change audio track\n\
")

class AdvancedFreePlayerInfobar(Screen):
    skin = LoadSkin('AdvancedFreePlayerInfobar')
    def __init__(self,session, isPause = False):
        Screen.__init__(self, session)
        
        if isPause == False:
            self["actions"] = ActionMap(["AdvancedFreePlayerInfobar"],
            {
                "CloseInfobar": self.CloseInfobar,
                "CloseAndStop": self.CloseAndStop,
                "CloseAndTogglePause": self.CloseAndTogglePause,
            },-2)
            self.onShown.append(self.__LayoutFinish)
        else:
            self["actions"] = ActionMap(["AdvancedFreePlayerPauseInfobar"],
            {
                "unPause": self.unPause,
                "CloseAndStop": self.CloseAndStop,
            },-2)
            self.onShown.append(self.__PauseLayoutFinish)
        
    def __LayoutFinish(self):
        self.autoHideTime = 1000 * int(myConfig.InfobarTime.value)
        self.hideOSDTimer = eTimer()
        self.hideOSDTimer.callback.append(self.CloseInfobar)
        self.hideOSDTimer.start(self.autoHideTime, True) # singleshot

    def __PauseLayoutFinish(self):
        printDEBUG('AdvancedFreePlayerInfobar in pause')

    def unPause(self):
        self.close('unPause')
        
    def CloseAndStop(self):
        self.close('StopPlayer')
        
    def CloseAndTogglePause(self):
        self.close('togglePause')
        
    def CloseInfobar(self):
        self.close()

    def createSummary(self):
        return AdvancedFreePlayerLCD

class AdvancedFreePlayer(Screen):
    ENABLE_RESUME_SUPPORT = True
    VISIBLE = 4
    HIDDEN = 5
    SHOWNSUBTITLE = 6
    HIDDENSUBTITLE = 7

    def __init__(self, session,openmovie,opensubtitle, rootID, LastPlayedService, URLlinkName = '', movieTitle='', LastPosition = 0, movieDescription='', movieCover=''):
        self.session = session
        self.statusScreen = self.session.instantiateDialog(StatusScreen)
        
        self.movieDescription = movieDescription
        self.movieCover = movieCover
        self.URLlinkName = URLlinkName
        self.frameon = 1 / 24
        self.seeksubtitle = 0
        self.resume_point = LastPosition
        self.nrsubtitle = 0
        self.statesubtitle = self.HIDDENSUBTITLE
        self.subtitles_enabled = False
        self.selected_subtitle = False
        self.stateplay = ""
        self.stateinfo = self.VISIBLE
        self.openmovie = openmovie
        
        if movieTitle == '':
            self.movieTitle = getNameWithoutExtension(path.basename(self.openmovie))
            #printDEBUG(self.movieTitle)
        else:
            self.movieTitle = movieTitle
            
        self.opensubtitle = opensubtitle
        self.rootID = int(rootID)
        self.LastPlayedService = LastPlayedService
        self.subtitle = []
        self.fontpos = 540
        self.fontsize = 60
        self.SubtitleLineHeight=66
        self.osdPosX = 0
        self.osdPosY = 0
        self.fonttype_nr = 0
        self.fontcolor_nr = 0
        self.fontbackground_nr = 0
        self.fontBackgroundState = 1
        self.aspectratiomode = '0'
        #load
        self.loadfont()
        self.loadcolor()
        self.loadBackgroundColor()
        self.loadconfig()
        
        self.enablesubtitle = False

        isHD = False
        isWideScreen = False
        isDolby = False
        if getDesktop(0).size().width() == 1920:
            self.skin = """
              <screen name="AdvancedFreePlayer" position="0,0" size="1920,1080" title="InfoBar" backgroundColor="transparent" flags="wfNoBorder">
                <!-- SubTitles -->
                <widget name="afpSubtitles" position="0,0" size="1,1" valign="center" halign="center" font="Regular;60" backgroundColor="#ff000000" transparent="0" />
                <!-- Info about ff,rf -->
                <widget name="showJump" position="120,120" zPosition="10" size="120,40" valign="center" halign="center" font="Regular;36" backgroundColor="#80000000" transparent="0" />
              </screen>"""
        else:
            self.skin = """
              <screen name="AdvancedFreePlayer" position="0,0" size="1280,720" title="InfoBar" backgroundColor="transparent" flags="wfNoBorder">
                <!-- SubTitles -->
                <widget name="afpSubtitles" position="0,0" size="1,1" valign="center" halign="center" font="Regular;60" backgroundColor="#ff000000" transparent="0" />
                <!-- Info about ff,rf -->
                <widget name="showJump" position="100,100" zPosition="10" size="120,34" valign="center" halign="center" font="Regular;30" backgroundColor="#80000000" transparent="0" />
              </screen>"""
        Screen.__init__(self, session)
        self["afpSubtitles"] = Label()
        self["showJump"] = Label()
        self["showJump"].hide()
        self.showJumpNumber = 0

        self["actions"] = ActionMap(["AdvancedFreePlayer"],
            {
                "ToggleInfobar": self.ToggleInfobar,
                "HelpScreen": self.HelpScreen,
                
                "ExitPlayer": self.ExitPlayer,
                "MoveSubsUp": self.MoveSubsUp,
                "MoveSubsDown": self.MoveSubsDown,
                "SetSmallerFont": self.SetSmallerFont,
                "SetBiggerFont": self.SetBiggerFont,
                "pause": self.pause,
                "play": self.play,
                "FastF30s": self.FastF30s,
                "FastF120s": self.FastF120s,
                "FastF300s": self.FastF300s,
                "BackF30s": self.BackF30s,
                "BackF120s": self.BackF120s,
                "BackF300s": self.BackF300s,
                "toggleFontBackground": self.toggleFontBackground,
                "SeekUpSubtitles": self.SeekUpSubtitles,
                "SeekDownSubtitles": self.SeekDownSubtitles,
                "togglePause": self.togglePause,
                "ToggleFont": self.ToggleFont,
                "ToggleFontColor": self.ToggleFontColor,
                "ToggleSubtitles": self.ToggleSubtitles,
                "SelectAudio": self.SelectAudio,
                "SelectSubtitles": self.SelectSubtitles,
                "aspectChange": self.aspectChange,
            },-2)
        self.onShown.append(self.__LayoutFinish)
        self.onClose.append(self.__onClose)
        if self.LastPlayedService is None:
            self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.session.nav.stopService()
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
            {
                #iPlayableService.evSeekableStatusChanged: self.__seekableStatusChanged,
                iPlayableService.evStart: self.resumeLastPlayback,
                #iPlayableService.evEOF: self.__evEOF,
                #iPlayableService.evSOF: self.__evSOF,
            })

    def __onClose(self):
        myConfig.Inits.value = str(self.fontpos) + "," + str(self.fontsize) + "," + \
                                                        str(self.fonttype_list[self.fonttype_nr]) + "," + str(self.fontcolor_nr) + "," + \
                                                        str(self.fontBackgroundState) + "," + str(self.fontbackground_nr)
        myConfig.Inits.save()

        if self.LastPlayedService:
            self.session.nav.playService(self.LastPlayedService, forceRestart=True)

    def __LayoutFinish(self):
        #print("--> Start of __LayoutFinish")
        self.currentHeight= getDesktop(0).size().height()
        self.currentWidth = getDesktop(0).size().width()
        
        self.onShown.remove(self.__LayoutFinish)
        print("--> Loading subtitles")
        self.loadsubtitle()
        print("End of __LayoutFinish")
        
        self.ShowJumpTimer = eTimer()
        self.ShowJumpTimer.callback.append(self.ShowJumpTimerCallBack)

    def ShowJump(self, seconds, subtitlesSeek = False):
        self.showJumpNumber += seconds #seconds can be positiove or negative
        if self.showJumpNumber != 0:
            if subtitlesSeek:
                text = "%ss | %ss" % (self.showJumpNumber,self.seeksubtitle)
            else:
                text = "%02d:%02d" % divmod(self.showJumpNumber,60)
            #w = self["showJump"].instance.size().width()
            self["showJump"].setText(text)
            height = self["showJump"].instance.size().height()
            width = int(int(fontRenderClass.getInstance().getLineHeight(self["showJump"].instance.getFont())) * len(text) * 0.7)
            #self["showJump"].instance.resize(eSize(width, linesNO * self.SubtitleLineHeight) )
            self["showJump"].instance.resize( eSize(width, height) )
            self["showJump"].show()
            self.ShowJumpTimer.stop() #in case ff/rf pressed several timwes
            self.ShowJumpTimer.start(1000 * int(myConfig.InfobarTime.value), True) # singleshot
        else:
            self["showJump"].setText("")
            self["showJump"].hide()
            self.showJumpNumber = 0
      
    def ShowJumpTimerCallBack(self):
        self["showJump"].setText("")
        self["showJump"].hide()
        self.showJumpNumber = 0
      
    def __getCuesheet(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return None
        return service.cueSheet()

    def resumeLastPlayback(self):
        #printDEBUG("resumeLastPlayback>>>")
        if not self.ENABLE_RESUME_SUPPORT:
            printDEBUG("resumeLastPlayback: ENABLE_RESUME_SUPPORT=false")
            return
        self.ResumeTimer = eTimer()
        self.ResumeTimer.callback.append(self.resumeLastPlaybackNext)
        self.ResumeTimer.start(1000, True) # singleshot

    def resumeLastPlaybackNext(self):
        if self.resume_point > 0:
            last = self.resume_point
            printDEBUG("PlayWithDmnapi|resumeLastPlayback: last position (%d) provided on start" % last)
        else:
            cue = self.__getCuesheet()
            if cue is None:
                printDEBUG("resumeLastPlayback: cue is None")
                return
            cut_list = cue.getCutList()

            last = None
            for (pts, what) in cut_list:
                if what == CUT_TYPE_LAST:
                    last = pts
                    printDEBUG("resumeLastPlayback: last position found at %d" % last)
                    break
            if last is None:
                printDEBUG("resumeLastPlayback: last position is None")
                return
            
        # only resume if at least 10 seconds ahead, or <10 seconds before the end.
        seekable = self.__getSeekable()
        if seekable is None:
            printDEBUG("resumeLastPlayback: seekable is None")
            return  # Should not happen?
        length = seekable.getLength() or (None, 0)
        printDEBUG("resumeLastPlayback: seekable.getLength() returns: %d" % length[1])
        # Hmm, this implies we don't resume if the length is unknown...
        if (last > 900000) and (not length[1]  or (last < length[1] - 900000)):
            self.resume_point = last
            l = last / 90000
            self.playLastCB(True)
    
    def playLastCB(self, answer):
        if answer == True:
            try:
                printDEBUG("resuming from %d" % (self.resume_point/90000))
                self.doSeek(self.resume_point)
            except:
                pass
#        self.hideAfterResume()

    def go(self):
        if len(self.subtitle) == 0:
            printDEBUG("Subtitles not loaded, timer disabled.")
        else:
            printDEBUG("Enable loaded %d subtitles" % len(self.subtitle))
            self.enablesubtitle = True
            self.timer = eTimer()
            self.timer.callback.append(self.timerEvent)
            self.timer.start(200, False)
        printDEBUG("Playing: " + str(self.rootID) + ":0:0:0:0:0:0:0:0:0:" + self.openmovie)
        root = eServiceReference(self.rootID, 0, self.openmovie)
        root.setName (self.movieTitle)
        self.session.nav.playService(root)
        myConfig.PlayerOn.value = True
        self.stateplay = "Play"
        self["afpSubtitles"].instance.move(ePoint(0,self.fontpos))
        self["afpSubtitles"].instance.setForegroundColor(parseColor(self.fontcolor_list[self.fontcolor_nr]))
        self["afpSubtitles"].instance.setBackgroundColor(parseColor(self.backgroundcolor_list[self.fontbackground_nr]))
        self["afpSubtitles"].instance.setFont(gFont(self.fonttype_list[self.fonttype_nr], self.fontsize))
        self.SubtitleLineHeight = int(fontRenderClass.getInstance().getLineHeight(self["afpSubtitles"].instance.getFont()))
        if self.SubtitleLineHeight > self.fontsize:
            printDEBUG("SubtitleLineHeight calculated: %d" % self.SubtitleLineHeight)
        else:
            self.SubtitleLineHeight = int(self.fontsize * 1.1)
            printDEBUG("SubtitleLineHeight assumed: %d" % self.SubtitleLineHeight)
        self.ToggleInfobar()
            
        #print("End of go")

    def loadfont(self):
        self.fonttype_list = []
        self.fonttype_list.append("Regular")
          
        fonts = []
        fonts_paths =[ "/usr/share/fonts/" , PluginPath + "fonts/"]
        for font_path in fonts_paths:
            if path.exists(font_path):
                for file in listdir(font_path):
                    if file.lower().endswith(".ttf") and file not in fonts:
                        fonts.append( (font_path + '/' + file, file))
                        addFont(font_path + '/' + file, file, 100, False)
        fonts.sort()
        for font in fonts:
            self.fonttype_list.append(font[1])  

    def loadcolor(self):
        self.fontcolor_list = []
        self.fontcolor_list.append("white")
        if path.exists(PluginPath + 'colors.ini'):
            o = open(PluginPath + 'colors.ini','r')
            while True:
                l = o.readline()
                if len(l) == 0: break
                l = l.strip()
                #print(l)
                self.fontcolor_list.append(l)
            o.close()

    def loadBackgroundColor(self):
        self.backgroundcolor_list = []
        self.backgroundcolor_list.append("#ff000000")
        if path.exists(PluginPath + 'backgrounds.ini'):
            with open(PluginPath + 'backgrounds.ini','r') as o:
                for l in o:
                    if len(l) > 0:
                        l = l.strip()
                        #print(l)
                        self.backgroundcolor_list.append(l)
                o.close()

    def loadconfig(self):
        try:
            configs=myConfig.Inits.value.split(',')
        except:
            return
            
        self.fontpos = int(configs[0])
        self.fontsize = int(configs[1])
        
        self.fonttype_nr = 0
        tmp = configs[2]
        
        self.fontcolor_nr = int(configs[3])
        self.fontBackgroundState = int(configs[4])
        self.fontbackground_nr = int(configs[5])

    def convertTime(self, time):
#        print("convertTime:"+str(time))
        if time is None:
            time=0
        s = "%d:%02d:%02d" % ((time/3600/90000), (time/90000)%3600/60, (time/90000)%60)
        return s

    def timerEvent(self):
        if self.nrsubtitle < 0:
            self.nrsubtitle += 1
            return
        lCurrent = self.GetCurrentPosition() or 0
        #printDEBUG("lCurrent=%d" % lCurrent)
        if not lCurrent is None:
            self.showsubtitle(lCurrent)

    def showsubtitle(self,tim):
        if self.enablesubtitle == False:
            return
        tim = tim + (self.seeksubtitle * 90000) #current position + movement
        for pos in self.subtitle:
            nr=pos[0]
            start=pos[1]
            stop=pos[2]
            text=pos[3]
            if tim >= start and tim < stop and (nr > self.nrsubtitle or self.nrsubtitle == 0):
                self.nrsubtitle = nr
                self.setTextForAllLInes(text)
                self.statesubtitle = self.SHOWNSUBTITLE
                #printDEBUG ("%d Show %d %d --> %d\t%s" %(tim, nr, start, stop, text) )
            elif tim > stop and nr == self.nrsubtitle:
                if self.statesubtitle == self.SHOWNSUBTITLE:
                    self.setTextForAllLInes("")
                    self.statesubtitle = self.HIDDENSUBTITLE
                    #printDEBUG ("%d Hide %d %d --> %d\t%s" %(tim, nr, start, stop, text) )

    def clearTags(self,l):
        if len(l) > 0:
            l = l.replace('<b>','').replace('</b>','')
            l = l.replace('<i>','').replace('</i>','')
            l = l.replace('<u>','').replace('</u>','')
            #<font color=#rrggbb></font>
            l = re.sub('<font color=#......>', '', l).replace('</font>','')
            for i in (0, 1):
                if l[0] == "{":
                    p = l.find("}")
                    if p != -1:
                        l = l[p+1:]
                else:
                    break
            l = l.strip()
        return l
        
    def loadsubtitle(self):
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        if self.opensubtitle.startswith('http://') and path.exists('/usr/bin/curl') and self.opensubtitle.endswith('.srt'):
            printDEBUG("Downloading http srt subtitles from %s" % self.opensubtitle)
            system('curl -kLs  %s -o /tmp/afpsubs.srt' % self.opensubtitle) 
            self.opensubtitle = '/tmp/afpsubs.srt'
        elif self.opensubtitle.startswith('ftp://') and path.exists('/usr/bin/curl') and self.opensubtitle.endswith('.srt'):
            printDEBUG("Downloading ftp srt subtitles from %s" % self.opensubtitle)
            system('curl -kLs --ftp-pasv %s -o /tmp/afpsubs.srt' % self.opensubtitle)
            self.opensubtitle = '/tmp/afpsubs.srt'
        elif self.opensubtitle.startswith('http://') and path.exists('/usr/bin/curl') and self.opensubtitle.endswith('.txt'):
            printDEBUG("Downloading http txt subtitles from %s" % self.opensubtitle)
            system('curl -kLs  %s -o /tmp/afpsubs.txt' % self.opensubtitle) 
            self.opensubtitle = '/tmp/afpsubs.txt'
        elif self.opensubtitle.startswith('ftp://') and path.exists('/usr/bin/curl') and self.opensubtitle.endswith('.txt'):
            printDEBUG("Downloading ftp txt subtitles from %s" % self.opensubtitle)
            system('curl -kLs --ftp-pasv %s -o /tmp/afpsubs.txt' % self.opensubtitle)
            self.opensubtitle = '/tmp/afpsubs.txt'
            
        if path.exists(self.opensubtitle):
            # >>> Detect encoding through BOM
            encoding=None
            with open(self.opensubtitle, 'rb') as f:
                raw = f.read(4)
                f.close
            for enc,boms in \
                    ('utf-8-sig',(codecs.BOM_UTF8,)),\
                    ('utf-16',(codecs.BOM_UTF16_LE,codecs.BOM_UTF16_BE)),\
                    ('utf-32',(codecs.BOM_UTF32_LE,codecs.BOM_UTF32_BE)):
                if any(raw.startswith(bom) for bom in boms):
                    encoding = enc
                    break
            if encoding is None:
                #eventual additional chardetection ;)
                encoding='UTF-8'
                
            if self.opensubtitle[-4:] == ".srt":
                self.loadsrt(encoding)
                self.go()
            else:
                self.loadtxt_type(encoding)
        else:
            self.go()

    def loadtxt_type(self, encoding='utf-8'):
        printDEBUG("loadtxt_type>>> '%s'" % self.opensubtitle)
        try:
            #o = open(self.opensubtitle,'r')
            o = codecs.open(self.opensubtitle, 'r', encoding, 'replace')
            l = o.readline()
            o.close()
        except IOError as e:
            try:
                printDEBUG("Error loadtxt_type, I/O error({0}): {1}".format(e.errno, e.strerror) )
                o.close()
            except:
                pass
        try:
            if len(l) < 3:
                print("[FP] Load subtitle unkown TXT - not load")
                self.go()
                return
            elif l[0] == "{":
                printDEBUG("[FP] Load subtitle TXT mDVD")
                oo = open(self.openmovie,'r')
                d = oo.read(250)
                oo.close()
                if d[0] == "R" and d.find("strlstrh") != -1:
                    print("AVI RIFF")
                    temp = d.find("strlstrh")
                    l4 = ord(d[temp+32])
                    l3 = ord(d[temp+33])
                    l2 = ord(d[temp+34])
                    l1 = ord(d[temp+35])
                    #print("%x" %l1)
                    #print("%x" %l2)
                    #print("%x" %l3)
                    #print("%x" %l4)
                    l1 = l1 << 24
                    l2 = l2 << 16
                    l3 = l3 << 8
                    dwscale = float(l1 + l2 + l3 + l4)
                    #print("%x" % dwscale)
                    l4 = ord(d[temp+36])
                    l3 = ord(d[temp+37])
                    l2 = ord(d[temp+38])
                    l1 = ord(d[temp+39])
                    #print("%x" %l1)
                    #print("%x" %l2)
                    #print("%x" %l3)
                    #print("%x" %l4)
                    l1 = l1 << 24
                    l2 = l2 << 16
                    l3 = l3 << 8
                    dwrate = float(l1 + l2 + l3 + l4)
                    #print("%x" % dwrate)
                    framerate = dwrate / dwscale
                    print("framerate =",framerate)
                    self.frameone = 1 / framerate
                else:
                    printDEBUG("Unkown AVI - set manual framerate")
                    self.session.openWithCallback(self.framerateCallback, ChoiceBox, \
                    title=_("AdvancedFreePlayer not found framerate in movie.\nPlease select manual framerate !"), \
                    list=[["23.0","23.0"],["23.5","23.5"],["23.976","23.976"],["24.0","24.0"],["24.5","24.5"],["25.0","25.0"]])
                    return
            elif l[0] == "[":
                printDEBUG("[FP] Load subtitle TXT mpl2")
            elif l[1] == ":":
                print("[FP] Load subtitle TXT tmp 0:00:00")
            elif l[2] == ":":
                print("[FP] Load subtitle TXT tmp 00:00:00")
            else:
                print("[FP] Load subtitle unkown TXT - not load")
                self.go()
                return
            self.loadtxt()
            self.go()
        except:
            printDEBUG("Error in loadtxt_type")
            try:
                oo.close()
            except:
                pass
            self.session.open(MessageBox,_("Error load subtitle !!!"),  MessageBox.TYPE_ERROR)
            self.go()

    def framerateCallback(self,val):
        if val is not None:
            print("Manual framerate = ",val[1])
            a = float(val[1])
            self.frameone = 1 / a
            self.loadtxt()
        self.go()

    def loadtxt(self, encoding='utf-8'):
        try:
            self.subtitle = []
            #o = open(self.opensubtitle,'r')
            o = codecs.open(self.opensubtitle, 'r', encoding, 'replace')
            nr = 1
            while True:
                l = o.readline()
                if len(l) == 0:break
                if ord(l[0]) == 13: continue
                if l == "\n": continue
                l = l.strip()
                #tmp
                if l[1] == ":": #0:00:00
                    tim1_h = int(l[0:1])
                    tim1_m = int(l[2:4])
                    tim1_s = int(l[5:7])
                    t1 = ((((int(tim1_h) * 3600) + (int(tim1_m) * 60) + int(tim1_s))*1000))*90
                    l = l[8:]
                    if len(l)==0:continue
                    l = l.decode('windows-1250').encode('utf-8')
                    l = l.replace('/','')
                    l = l.replace('|','\n')
                    #ustalenie czasu wyswietlania napisow
                    seek=o.tell()
                    ll = o.readline()
                    if len(ll) == 0:break
                    o.seek(seek)
                    tim2_h = int(ll[0:1])
                    tim2_m = int(ll[2:4])
                    tim2_s = int(ll[5:7])
                    t2 = ((((int(tim2_h) * 3600) + (int(tim2_m) * 60) + int(tim2_s))*1000))*90
                    z = len(l)
                    if z <= 10:
                        z = 1
                    elif z > 10 and z <= 20:
                        z = 3
                    else:
                        z = 5
                    t3 = t1 + (90000 * z)
                    if t3 < t2:
                        t2 = t3
                    #print("-")
                elif l[2] == ":": #00:00:00
                    tim1_h = int(l[0:2])
                    tim1_m = int(l[3:5])
                    tim1_s = int(l[6:8])
                    t1 = ((((int(tim1_h) * 3600) + (int(tim1_m) * 60) + int(tim1_s))*1000))*90
                    l = l[9:]
                    if len(l)==0:continue
                    l = l.decode('windows-1250').encode('utf-8')
                    l = l.replace('/','')
                    l = l.replace('|','\n')
                    #ustalenie czasu wyswietlania napisow
                    seek=o.tell()
                    ll = o.readline()
                    if len(ll) == 0:break
                    o.seek(seek)
                    tim2_h = int(ll[0:1])
                    tim2_m = int(ll[2:4])
                    tim2_s = int(ll[5:7])
                    t2 = ((((int(tim2_h) * 3600) + (int(tim2_m) * 60) + int(tim2_s))*1000))*90
                    z = len(l)
                    if z <= 10:
                        z = 1
                    elif z > 10 and z <= 20:
                        z = 3
                    else:
                        z = 5
                    t3 = t1 + (90000 * z)
                    if t3 < t2:
                        t2 = t3
                    #print("-")
                #mpl2
                elif l[0] == "[":
                    t1 = int(l[1:l.find(']')])
                    l = l[l.find(']')+1:]
                    t2 = int(l[1:l.find(']')])
                    l = l[l.find(']')+1:]
                    if len(l)==0:continue
                    l = l.decode('windows-1250').encode('utf-8')
                    l = l.replace('/','')
                    l = l.replace('|','\n')
                    t1 = t1 * 9000
                    t2 = t2 * 9000
                    #print(t1)
                    #print(t2)
                    #print(l)
                #mdvd
                elif l[0] == "{":
                    t1 = int(l[1:l.find('}')])
                    l = l[l.find('}')+1:]
                    t2 = int(l[1:l.find('}')])
                    l = l[l.find('}')+1:]
                    if len(l)==0:continue
                    l = l.decode('windows-1250').encode('utf-8')
                    l = l.replace('/','')
                    l = l.replace('|','\n')
                    t1 = t1 * self.frameone * 100
                    t2 = t2 * self.frameone * 100
                    t1 = int(t1) * 900
                    t2 = int(t2) * 900
                    #print(t1)
                    #print(t2)
                    #print(l)
                else:
                    continue
                l = self.clearTags(l)
                self.subtitle.append([int(nr),t1,t2,l])
                nr = nr + 1
            o.close()
        except IOError as e:
            self.subtitle = []
            o.close()
            print("Error loadtxt")
            self.session.open(MessageBox,"Error load subtitle !!!",  MessageBox.TYPE_ERROR, timeout=5)

    def loadsrt(self, encoding='utf-8'):
        self.subtitle = []
        printDEBUG("[FP] Load subtitle SRT as %s" %encoding)
        try:
            if path.exists(self.opensubtitle):
                #o = open(self.opensubtitle,'r')
                o = codecs.open(self.opensubtitle, 'r', encoding, 'replace')
                while True:
                    nr = o.readline().replace("\r\n","\n")
                    if len(nr) == 0:break
                    if nr == "\n": continue
                    nr = nr.strip()
                    if not nr.isdigit(): continue #>>>>>first row in a sequence has to be number of subtitle
                    tim = o.readline().replace("\r\n","\n")
                    if len(tim) == 0:break
                    tim = tim.strip()
                    #printDEBUG(tim)
                    l1 = o.readline().replace("\r\n","\n")
                    if len(l1) == 0:break
                    l1 = l1.strip()
                    l2 = o.readline().replace("\r\n","\n")
                    if len(l2) == 0:break
                    if not l2 == "\n":
                        l2 = l2.strip()
                        l = l1 + "\n" + l2
                        l3 = o.readline().replace("\r\n","\n")
                        if len(l3) == 0:break
                        if not l3 == "\n":
                            l3 = l3.strip()
                            l = l1 + "\n " + l2 + "\n" + l3
                            l4 = o.readline().replace("\r\n","\n")
                            if len(l4) == 0:break
                            if not l4 == "\n":
                                l4 = l4.strip()
                                l = l1 + "\n " + l2 + "\n" + l3 + "\n" + l4
                                n = o.readline().replace("\r\n","\n")
                                if len(n) == 0:break
                    else:
                        l = l1
                    l = self.clearTags(l)
                    tim1=tim.split(' ')[0]
                    tim1_h = tim1.split(':')[0]
                    tim1_m = tim1.split(':')[1]
                    tim1_s = tim1.split(':')[2].split(',')[0]
                    tim1_ms = tim1.split(':')[2].split(',')[1]
                    tim_1 = ((((int(tim1_h) * 3600) + (int(tim1_m) * 60) + int(tim1_s))*1000)+int(tim1_ms))*90
                    tim2=tim.split('>')[1].strip()
                    tim2_h = tim2.split(':')[0]
                    tim2_m = tim2.split(':')[1]
                    tim2_s = tim2.split(':')[2].split(',')[0]
                    tim2_ms = tim2.split(':')[2].split(',')[1]
                    tim_2 = ((((int(tim2_h) * 3600) + (int(tim2_m) * 60) + int(tim2_s))*1000)+int(tim2_ms))*90
                    self.subtitle.append([int(nr),tim_1,tim_2,l])
                o.close()
        except Exception as e:
            self.subtitle = []
            try: printDEBUG("Error %s loadding subtitle id %d ('%s' > '%s'" % (str(e),int(nr),tim1,tim2) )
            except: printDEBUG("Error %s loadding subtitle id %d" % (str(e),int(nr)) )
            try:
                o.close()
            except:
                pass
            self.session.open(MessageBox,"Error load subtitle !!!",  MessageBox.TYPE_ERROR, timeout=5)

    def __getSeekable(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return None
        return service.seek()

    def GetCurrentPosition(self):
        seek = self.__getSeekable()
        if seek is None:
            return None
        r = seek.getPlayPosition()
        if r[0]:
            return None
        return long(r[1])

    def GetCurrentLength(self):
        seek = self.__getSeekable()
        if seek is None:
            return None
        r = seek.getLength()
        if r[0]:
            return None
        return long(r[1])

    def getSeek(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return None
        seek = service.seek()
        if seek is None or not seek.isCurrentlySeekable():
            return None
        return seek

    def doSeek(self, pts):
        print("..- doSeek Start %d" % (pts/90000))
        seekable = self.getSeek()
        if seekable is None:
            return
        print("..- doSeek %d" % (pts/90000))
        seekable.seekTo(pts)

    def doSeekRelative(self, pts):
        if self.enablesubtitle:
            self.timer.stop()
        print("..- doSeekRelative Start %d" % (pts/90000))
        seekable = self.getSeek()
        if seekable is None:
            return
        print("..- doSeekRelative %d" % (pts/90000))
        seekable.seekRelative(pts<0 and -1 or 1, abs(pts))
        self.nrsubtitle = 0 #reset position
        self.setTextForAllLInes("")
        self.ShowJump(pts/90000)
        if self.enablesubtitle:
            if pts<0: self.nrsubtitle = -1 #skip abs(self.nrsubtitle) number of timerEvent calls
            self.timer.start(200, False)

    def FastF30s(self):
        if self.stateplay == "Play":
            self.doSeekRelative(30 * 90000)

    def FastF120s(self):
        if self.stateplay == "Play":
            self.doSeekRelative(2 * 60 * 90000)

    def FastF300s(self):
        if self.stateplay == "Play":
            self.doSeekRelative(5 * 60 * 90000)

    def BackF30s(self):
        if self.stateplay == "Play":
            self.doSeekRelative(- 15 * 90000)

    def BackF120s(self):
        if self.stateplay == "Play":
            self.doSeekRelative(- 2 * 60 * 90000)

    def BackF300s(self):
        if self.stateplay == "Play":
            self.doSeekRelative(- 5 * 60 * 90000)

##################################################################### SEEK SUBTITLES >>>>>>>>>>
    def SeekSubtitles(self, position):
        self.seeksubtitle = self.seeksubtitle + position
        self.setTextForAllLInes(str(self.seeksubtitle)+" sek")
        self.nrsubtitle = 0 #reset position
        self.setTextForAllLInes("")
        self.ShowJump(position, True)

    def SeekUpSubtitles(self):
        self.SeekSubtitles(+0.5)

    def SeekDownSubtitles(self):
        self.SeekSubtitles(-0.5)

    def ToggleSubtitles(self):
        if self.enablesubtitle == True:
            self.enablesubtitle = False
            self.setTextForAllLInes("")
        else:
            self.enablesubtitle = True

    def HelpScreen(self):
        self.session.open(MessageBox,PluginName + ' ' + PluginInfo +"\n\n"+ KeyMapInfo,  MessageBox.TYPE_INFO)

    def SelectAudio(self):
        from Screens.AudioSelection import AudioSelection
        self.session.openWithCallback(self.audioSelected, AudioSelection, infobar=self)

    def getCurrentServiceSubtitle(self):
        return False
      
    def audioSelected(self, ret=None):
        print("[AdvancedFreePlayer infobar::audioSelected]", ret)

    def aspectChange(self):
        printDBG('Aspect Ratio [%r]' % self.aspectratiomode)
        if self.aspectratiomode == '0':  # 4:3 Letterbox
            eAVSwitch.getInstance().setAspectRatio(2)
            self.aspectratiomode = '2'
            self.statusScreen.setStatus("16:9 Bestfit")
            return
        elif self.aspectratiomode == '2': # 16:9 Bestfit
            eAVSwitch.getInstance().setAspectRatio(1)
            self.aspectratiomode = '1'
            self.statusScreen.setStatus("4:3 PanScan")
        elif self.aspectratiomode == '1': # 4:3 PanScan
            eAVSwitch.getInstance().setAspectRatio(0)
            self.aspectratiomode = '0'
            self.statusScreen.setStatus("4:3 Letterbox")
########################################################################################### START functions
    def setTextForAllLInes(self, text):
        textWidth = 0
        text = text.strip()
        if text == '':
            self["afpSubtitles"].setText('')
            self["afpSubtitles"].hide()
        else:
            linesNO = text.count('\n') + 1
            if linesNO == 1:
                textWidth = len(text)
            else:
                for line in text.split('\n'):
                    tempLen = len(line)
                    if tempLen > textWidth:
                        textWidth = tempLen 
                        
            printDEBUG(text)
            self["afpSubtitles"].setText(text.encode('utf-8'))
            textWidth *= int(self.fontsize * 0.75) # The best would be to calculate real width, but don't know how to do it. :(
            center = int( (self.currentWidth - textWidth) /2 )
            self["afpSubtitles"].instance.resize(eSize(textWidth, linesNO * self.SubtitleLineHeight) )
            self["afpSubtitles"].instance.move(ePoint(center, self.fontpos ) )
            self["afpSubtitles"].show()

    def isNotFontLine(self, component):
        if self["afpSubtitles"] is component:
            return False
        return True

    def ExitPlayer(self):
        def DeleteFile(f2d):
            if path.exists(f2d):
                try:
                    remove(f2d)
                except:
                    printDEBUG("Error deleting %s" % f2d)
                
        self.stateplay = "Stop"
        try:
            self.timer.stop()
        except:
            pass
        try:
            LastPosition = self.GetCurrentPosition()
            Movielength = self.GetCurrentLength()
            PercentagePlayed =  int( LastPosition / float(Movielength) * 100)
        except:
            LastPosition = 0
            PercentagePlayed = 0
            Movielength = 0
        self.session.nav.stopService()
        printDEBUG ("Played %d%%, last position=%d" % (PercentagePlayed,LastPosition))
        DeleteFile('/tmp/afpsubs.srt')
        DeleteFile('/tmp/afpsubs.txt')
        if self.URLlinkName == '' and not access(self.openmovie, W_OK):
            printDEBUG("No access to delete local file '%s'" % self.openmovie)
        elif self.URLlinkName != '' and not access(self.URLlinkName, W_OK):
            printDEBUG("No access to delete URLink '%s'" % self.URLlinkName)
        elif myConfig.DeleteFileQuestion.value == True or (PercentagePlayed >= int(myConfig.DeleteWhenPercentagePlayed.value) and \
            int(myConfig.DeleteWhenPercentagePlayed.value) >0) and self.openmovie.find('iptv_buffering') != -1:
            printDEBUG(self.openmovie)
            def ExitRet(ret):
                if ret:
                    if self.URLlinkName == '':
                        if myConfig.MoveToTrash == True:
                            try:
                                printDEBUG("Executing 'mv -f \"%s/%s.*\" %s'" %(myDir,myFile,myConfig.TrashFolder.value))
                                ClearMemory() #some tuners (e.g. nbox) with small amount of RAM have problems with next command
                                system('mv -f "%s/%s*" "%s/";(sleep 5;rm -f "%s/%s*" "%s/") &' %(myDir,myFile,myConfig.TrashFolder.value, myDir,myFile,myConfig.TrashFolder.value))
                            except Exception:
                                printDEBUG("Error executing system>move files engine")
                        else:
                            myDir = path.dirname(self.openmovie)
                            myFile = getNameWithoutExtension(path.basename(self.openmovie)) #To delete all files e.g. txt,jpg,eit,etc
                            DeleteFile(self.openmovie)
                            DeleteFile(self.opensubtitle)
                            DeleteFile(myDir + '/' + myFile + ".jpg")
                            DeleteFile(myDir + '/' + myFile + ".eit")
                            DeleteFile(myDir + '/' + myFile + ".txt")
                            DeleteFile(self.openmovie + ".ap")
                            DeleteFile(self.openmovie + ".meta")
                            DeleteFile(self.openmovie + ".sc")
                            DeleteFile(self.openmovie + ".cuts")
                            try:
                                printDEBUG("Executing 'rm -f \"%s/%s.*\"'" %(myDir,myFile))
                                ClearMemory() #some tuners (e.g. nbox) with small amount of RAM have problems with next command
                                system('rm -f "%s/%s*";(sleep 5;rm -f "%s/%s*") &' %(myDir,myFile, myDir,myFile))
                            except Exception:
                                printDEBUG("Error executing system>delete files engine")
                            
                    else:
                        if myConfig.MoveToTrash == True:
                            printDEBUG("Moving %s" % self.URLlinkName)
                            try:
                                ClearMemory() #some tuners (e.g. nbox) with small amount of RAM have problems with next command
                                system('mv -f "%s" "%s/"' %(self.URLlinkName, myConfig.TrashFolder.value))
                            except Exception:
                                printDEBUG("Error executing system>move files engine")
                        else:
                            printDEBUG("Deleting %s" % self.URLlinkName)
                            DeleteFile(self.URLlinkName)
                else:
                    if self.URLlinkName == '':
                        setCut(self.openmovie + ".cuts", LastPosition, Movielength)
                    else:
                        setCut(self.URLlinkName + ".cuts", LastPosition, Movielength)
            self.session.openWithCallback(ExitRet, MessageBox, _("Delete this movie?"), timeout=10, default=False)
        else:
            if self.URLlinkName == '':
                setCut(self.openmovie + ".cuts", LastPosition, Movielength)
            else:
                setCut(self.URLlinkName + ".cuts", LastPosition, Movielength)
        self.close()

##################################################################### RELOADING SUBTITLES >>>>>>>>>>
    def dmnapisubsCallback(self, answer=None):
        printDEBUG("SelectSubtitles:dmnapiCallback")
        if answer:
            with open('/tmp/afpsubs.srt','w') as mysrt:
                mysrt.write(answer)
                mysrt.close
            self.opensubtitle = '/tmp/afpsubs.srt'
            self.loadsrt()
            self.enablesubtitle = True
            
        self.play()
        
    def SelectSubtitles(self):
                
        self.pause(False)
        try:
            from Plugins.Extensions.DMnapi.DMnapisubs import DMnapisubs
            self.session.openWithCallback(self.dmnapisubsCallback, DMnapisubs, self.openmovie, save = False)
        except:
            printDEBUG("Exception loading DMnapi!!!")

##################################################################### CHANGE FONT SIZE >>>>>>>>>>
    def setFontSize(self, fontSize):
        if self.opensubtitle == '':
            return
        self.fontsize = self.fontsize + fontSize
        if self.fontsize < 10:
            self.fontsize = 10
        elif  self.fontsize > 80:
            self.fontsize = 80
        self["afpSubtitles"].instance.setFont(gFont(self.fonttype_list[self.fonttype_nr], self.fontsize))
        self.SubtitleLineHeight= int(fontRenderClass.getInstance().getLineHeight(self["afpSubtitles"].instance.getFont()))
        self.setTextForAllLInes(_("Font %s\nSize %s\nLine3") % (self.fonttype_list[self.fonttype_nr],self.fontsize))

    def SetSmallerFont(self):
        self.setFontSize( -2 )

    def SetBiggerFont(self):
        self.setFontSize(2)

##################################################################### TOGGLE INFOBAR >>>>>>>>>>

    def ToggleInfobar(self, inPause=False): #### old info
        def RetFromInfobar( ret = None):
            if ret:
                if ret == 'togglePause':
                    self.togglePause()
                elif ret == 'StopPlayer':
                    self.ExitPlayer()
                elif ret == 'unPause':
                    self.play()
                  
        self.session.openWithCallback(RetFromInfobar,AdvancedFreePlayerInfobar,isPause = inPause)
        return
##################################################################### TOGGLE FONT BACKGROUND >>>>>>>>>>
    def toggleFontBackground(self):
        if self.opensubtitle == '':
            return
        self.fontbackground_nr = self.fontbackground_nr + 1
        if self.fontbackground_nr == len(self.backgroundcolor_list):
            self.fontbackground_nr = 0
        self["afpSubtitles"].instance.setBackgroundColor(parseColor(self.backgroundcolor_list[self.fontbackground_nr]))
        self.setTextForAllLInes(_("Background ")+str(self.fontbackground_nr))
      
##################################################################### TOGGLE FONT COLOR >>>>>>>>>>
    def ToggleFontColor(self):
        if self.opensubtitle == '':
            return
        self.fontcolor_nr = self.fontcolor_nr + 1
        if self.fontcolor_nr == len(self.fontcolor_list):
            self.fontcolor_nr = 0
        self["afpSubtitles"].instance.setForegroundColor(parseColor(self.fontcolor_list[self.fontcolor_nr]))

        self.setTextForAllLInes(_("Color ")+str(self.fontcolor_nr))

##################################################################### TOGGLE FONT  >>>>>>>>>>
    def ToggleFont(self):
        if self.opensubtitle == '':
            return
        self.fonttype_nr = self.fonttype_nr + 1
        if self.fonttype_nr == len(self.fonttype_list):
            self.fonttype_nr = 0
        self["afpSubtitles"].instance.setFont(gFont(self.fonttype_list[self.fonttype_nr], self.fontsize))

        self.setTextForAllLInes(self.fonttype_list[self.fonttype_nr])

##################################################################### TOGGLE PAUSE >>>>>>>>>>
    def togglePause(self):
        if self.stateplay == "Play":
            self.pause()
        elif self.stateplay == "Pause":
            self.play()

    def pause(self, ShowInfobar = True ):
        if not self.stateplay == "Play":
            return
        cs = self.session.nav.getCurrentService()
        if cs is None:
            return
        pauseable = cs.pause()
        if pauseable is None:
            return
        pauseable.pause()
        self.stateplay = "Pause"
        if myConfig.InfobarOnPause.value == True and ShowInfobar == True:
            self.ToggleInfobar(inPause=True)
            return

    def play(self, ret = None):
        if not self.stateplay == "Pause":
            return
        cs = self.session.nav.getCurrentService()
        if cs is None:
            return
        pauseable = cs.pause()
        if pauseable is None:
            return
        pauseable.unpause()
        self.stateplay = "Play"

##################################################################### MOVE SUBTITLES UP/DOWN >>>>>>>>>>
    def updateSubtitlePosition(self, fotpos):
        if self.enablesubtitle == True:
            self.fontpos = self.fontpos + fotpos
            #print("pos y = ",self.fontpos)
            self.setTextForAllLInes(_("Line1\nLine2\nLine3"))

    def MoveSubsUp(self):
        self.updateSubtitlePosition(-5)

    def MoveSubsDown(self):
        self.updateSubtitlePosition(+5)

    def createSummary(self):
        return AdvancedFreePlayerLCD

##################################################################### LCD Screens <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class AdvancedFreePlayerLCD(Screen): 
    skin = LoadSkin('AdvancedFreePlayerLCD')
    
##################################################################### Status Screen <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class StatusScreen(Screen):
    def __init__(self, session):
        self.delayTimer = eTimer()
        self.delayTimer.callback.append(self.hideStatus)
        self.delayTimerDelay = 1500

        self.skin = \
            """
            <screen name="StatusScreen" position="40,30" size="250,90" zPosition="0" backgroundColor="transparent" flags="wfNoBorder">
                    <widget name="status" position="0,0" size="250,70" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="green" />
            </screen>"""

        Screen.__init__(self, session)
        self.stand_alone = True
        print('initializing status display')
        self['status'] = Label('')
        self.onClose.append(self.__onClose)

    def setStatus(self, text, color='green'):
        self['status'].setText(text)
        self['status'].instance.setForegroundColor(parseColor(color))
        self.show()
        self.delayTimer.start(self.delayTimerDelay, True)

    def hideStatus(self):
        self.hide()
        self['status'].setText('')

    def __onClose(self):
        self.delayTimer.stop()
        del self.delayTimer
