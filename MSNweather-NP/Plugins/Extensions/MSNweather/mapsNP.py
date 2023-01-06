# -*- coding: utf-8 -*-
"""
#######################################################################
#
#    webMaps addon designed for skin BlackHarmony
#    Coded by j00zek (c)2019-2023
#
#     
####################################################################### 
"""

DBG = True

from . import _
from Plugins.Extensions.MSNweather.version import Version #ATV6.5 import error workarround
from Plugins.Extensions.MSNweather.debug import printDEBUG

from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.j00zekAccellPixmap import j00zekAccellPixmap
from Components.Sources.StaticText import StaticText
from datetime import datetime
from enigma import getDesktop, ePoint, eSize, eTimer
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
import os, requests, sys, time, re

PyMajorVersion = sys.version_info.major

if PyMajorVersion >= 3:
    unicode = str
    from urllib.request import urlretrieve as urllib_urlretrieve
    from urllib.parse import unquote as urllib_unquote, quote as urllib_quote
else: #py2
    from urllib import urlretrieve as urllib_urlretrieve, unquote as urllib_unquote, quote as urllib_quote

import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

import uuid
os.system('rm -rf /tmp/.tpsc*')
_MD_ = '/tmp/.tpsc%s' % uuid.uuid4().hex

def decodeHTML(text):
    text = text.replace('%lf', '. ').replace('&#243;', 'ó')
    text = text.replace('&#176;', '°').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'").replace('&#65282;', '"').replace('&#xFF02;', '"')
    text = text.replace('&#228;', 'ä').replace('&#196;', 'Ă').replace('&#246;', 'ö').replace('&#214;', 'Ö').replace('&#252;', 'ü').replace('&#220;', 'Ü').replace('&#223;', 'ß')
    return text

def downloadWebPage(webURL, doUnquote = False , HEADERS={}):
    try:
        if len(HEADERS) == 0:
        #Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0
        #Exceeded 30 redirects
            #used previously: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0
            #Mozilla/5.0 (Android 7.0; Mobile; rv:54.0) Gecko/54.0 Firefox/54.0
            #Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.14977

            HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                        'Accept-Charset': 'utf-8', 
                        'Content-Type': 'text/html; charset=utf-8'
                      }
        resp = requests.get(webURL, headers=HEADERS, timeout=5)
        webContent = resp.content
        webHeader = resp.headers
        if doUnquote == True:
            webContent =  urllib_unquote(webContent)
            webContent = decodeHTML(webContent)
    except Exception as e:
        print("EXCEPTION '%s' in downloadWebPage() for %s" % (str(e), webURL) )
        webContent = ''

    return webContent

def motionMaps(mapType, dirname):
    if 1:
        Maps = {'temperature_today': 'maptype=temperature&mapsubtype=today', 'precipitation_forecast': 'maptype=precipitation&mapsubtype=forecast', 
           'satellite_observation': 'maptype=satellite&mapsubtype=observation', 
           'clouds_forecast': 'maptype=clouds&mapsubtype=forecast'}
        URL = Maps.get(mapType, None)
        retVal = 'General Error'
        ImagesToDownloadList = []
        actualPNGs = []
        if URL is None:
            return (_('Error wrong input data'), ImagesToDownloadList)
        import re
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        fileprefix = mapType[:1]
        URL = 'http://www.msn.com/en-us/weather/fullscreenmaps?region=europe&%s' % URL
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763', 
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 
               'Accept-Encoding': 'deflate, br', 
               'Accept-Language': 'en-US,en;q=0.8', 
               'Connection': 'keep-alive'}
        try:
            HTML = downloadWebPage(webURL = URL, doUnquote = True, HEADERS = hdr)
            if DBG:
                open("/tmp/.MSNdata/mapsNP.HTML", "w").write(HTML)
            Images = re.findall('data-images="\\[(.*?)\\]"[ ]*data-boundinfo=', HTML, re.S)[0]
            ImagesList = re.findall('(http.*?.png)', Images, re.S)
        except Exception as e:
            printDEBUG('motionMaps()', str(e), 'mapsNP.log', DBG)
            open("/tmp/.MSNdata/mapsNP.HTML", "w").write(HTML)
            return ( _('Error sychronizing web data'), [] )

        if len(ImagesList) < 1:
            return ( _('Error analyzing web data'), [] )
        for imgURL in ImagesList:
            try:
                filename = '%s_20%s.png' % (fileprefix, imgURL.split('-20')[1].split('-')[0])
                filename = filename.replace('.png.png', '.png')
                FullFilePath = '%s/%s' % (dirname, filename)
                ImagesToDownloadList.append((FullFilePath, imgURL))
                actualPNGs.append(filename)
            except Exception:
                return (
                 _('Error sychronizing webMaps data'), [])

            try:
                filename = '%s_20%s.png' % (fileprefix, imgURL.split('-20')[1].split('-')[0])
                actualPNGs.append(filename)
                FullFilePath = '%s/%s' % (dirname, filename)
            except Exception:
                return (
                 _('Error sychronizing webMaps data'), [])

        if len(actualPNGs) > 0:
            for f in os.listdir(dirname):
                if f.startswith(fileprefix) and f.endswith('.png') and f not in actualPNGs and os.path.isfile('%s/%s' % (dirname, f)):
                    os.remove('%s/%s' % (dirname, f))

        retVal = mapType
        ImagesToDownloadList.sort()
        return (_(retVal), ImagesToDownloadList)

class MSNweatherMaps(Screen):
    def __init__(self, session, currForecaCity=_('Unknown')):
        self.DEBUG('INIT', '__init__ >>>')
        self.session = session
        self.currForecaCity = currForecaCity
        posX = 0
        posY = 0
        offsetX = 60
        offsetY = 50
        WindowWidth = getDesktop(0).size().width()
        WindowHeight = getDesktop(0).size().height()
        mapsWidthOrg = 1132
        mapsHeightOrg = 1122
        posXmaps = 30
        posYmaps = 0
        mapsHeight = WindowHeight - 2 * posYmaps
        mapsWidth = int(float(mapsHeight) / float(mapsHeightOrg) * mapsWidthOrg)
        infoY = posY + offsetY * 3
        infoX = posXmaps + mapsWidth + 20
        infoH = 40
        infoW = WindowWidth - infoX - offsetX
        infoLines = 2
        infoFont = int(0.75 * infoH)
        TimeInfoY = infoY + infoH * infoLines + 20
        TimeInfoX = infoX
        TimeInfoH = 35
        TimeInfoW = WindowWidth - infoX - offsetX
        TimeInfoLines = 2
        TimeInfoFont = int(0.75 * infoH)
        scaleW = 680
        scaleH = 50
        if infoW > scaleW:
            scaleX = WindowWidth - offsetX - scaleW - int((infoW - scaleW) / 2)
        else:
            scaleX = WindowWidth - offsetX - scaleW
        scaleY = WindowHeight - scaleH - offsetY
        keysWidth = 200
        keysHeight = 30
        keysFont = int(0.75 * keysHeight)
        keysSpace = 10
        posXkeys = WindowWidth - offsetX - keysWidth
        posYkeys = scaleY - offsetY
        titleText = 'MSNweatherMaps by j00zek %s' % Version
        self.skin = '<screen name="MSNweatherMaps" position="%s,%s" size="%s,%s" title=" ">\n' % (posX, posY, WindowWidth, WindowHeight)
        self.skin += '<eLabel text=" " position="%s,%s" size="%s,%s" backgroundColor="#000000" transparent="0"/>\n' % (posX, posY, WindowWidth, WindowHeight)
        self.skin += '<eLabel text="%s" position="%s,%s" size="%s,%s" font="Roboto_HD; 27" halign="right" backgroundColor="#FF000000" transparent="1"/>\n' % (titleText, offsetX, offsetY, WindowWidth - 2 * offsetX, WindowHeight - 2 * offsetY)
        self.skin += '<eLabel text=" " position="%s,%s" size="%s,%s" font="Roboto_HD; 27" halign="left" backgroundColor="#FF222222" transparent="0"/>\n' % (posXmaps, posYmaps, mapsWidth, mapsHeight)
        self.skin += '<widget name="BackgroundMap" position="%s,%s" zPosition="1" size="%s,%s" alphatest="blend" transparent="0" />\n' % (posXmaps, posYmaps, mapsWidth, mapsHeight)
        self.skin += '<widget name="MotionMap" position="%s,%s" zPosition="2" size="%s,%s" alphatest="blend" transparent="1" />\n' % (posXmaps, posYmaps, mapsWidth, mapsHeight)
        self.skin += '<widget name="ScaleMotionMap" position="%s,%s" zPosition="3" size="%s,%s" alphatest="blend" transparent="1" />\n' % (posXmaps, posYmaps, mapsWidth, mapsHeight)
        self.skin += '<widget name="Info" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="center" font="Regular;%s" transparent="1" foregroundColor="yellow" />\n' % (infoX, infoY, infoW, infoH * infoLines, infoFont)
        self.skin += '<widget name="TimeInfo" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="center" font="Regular;%s" transparent="1" foregroundColor="grey" />\n' % (TimeInfoX, TimeInfoY, TimeInfoW, TimeInfoH, TimeInfoFont)
        self.skin += '<ePixmap pixmap="BlackHarmony/buttons/key_1.png" position="%s,%s" size="35,27" alphatest="blend"/>\n' % (posXkeys - 40, posYkeys - 5 * (keysHeight + keysSpace))
        self.skin += '<widget name="key_1" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="left" font="Regular;%s" transparent="1" foregroundColor="white" />' % (posXkeys, posYkeys - 5 * (keysHeight + keysSpace), keysWidth, keysHeight, keysFont)
        self.skin += '<ePixmap pixmap="BlackHarmony/buttons/key_9.png" position="%s,%s" size="35,27" alphatest="blend"/>\n' % (posXkeys - 40, posYkeys - 4 * (keysHeight + keysSpace))
        self.skin += '<widget name="key_9" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="left" font="Regular;%s" transparent="1" foregroundColor="white" />' % (posXkeys, posYkeys - 4 * (keysHeight + keysSpace), keysWidth, keysHeight, keysFont)
        #self.skin += '<ePixmap pixmap="BlackHarmony/buttons/red.png" position="%s,%s" size="35,27" alphatest="blend"/>\n' % (posXkeys - 40, posYkeys - 3 * (keysHeight + keysSpace))
        self.skin += '<widget name="key_red" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="left" font="Regular;%s" transparent="1" foregroundColor="white" />' % (posXkeys, posYkeys - 3 * (keysHeight + keysSpace), keysWidth, keysHeight, keysFont)
        #self.skin += '<ePixmap pixmap="BlackHarmony/buttons/green.png" position="%s,%s" size="35,27" alphatest="blend"/>\n' % (posXkeys - 40, posYkeys - 2 * (keysHeight + keysSpace))
        self.skin += '<widget name="key_green" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="left" font="Regular;%s" transparent="1" foregroundColor="white" />\n' % (posXkeys, posYkeys - 2 * (keysHeight + keysSpace), keysWidth, keysHeight, keysFont)
        #self.skin += '<ePixmap pixmap="BlackHarmony/buttons/yellow.png" position="%s,%s" size="35,27" alphatest="blend"/>\n' % (posXkeys - 40, posYkeys - 1 * (keysHeight + keysSpace))
        self.skin += '<widget name="key_yellow" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="left" font="Regular;%s" transparent="1" foregroundColor="white" />\n' % (posXkeys, posYkeys - 1 * (keysHeight + keysSpace), keysWidth, keysHeight, keysFont)
        #self.skin += '<ePixmap pixmap="BlackHarmony/buttons/blue.png" position="%s,%s" size="35,27" alphatest="blend"/>\n' % (posXkeys - 40, posYkeys)
        self.skin += '<widget name="key_blue" position="%s,%s" zPosition="3" size="%s,%s" valign="center" halign="left" font="Regular;%s" transparent="1" foregroundColor="white" />\n' % (posXkeys, posYkeys, keysWidth, keysHeight, keysFont)
        self.skin += '<widget name="ScalePic" position="%s,%s" zPosition="5" size="%s,%s" alphatest="blend" transparent="1" />\n' % (scaleX, scaleY, scaleW, scaleH)
        self.skin += '</screen>\n'
        Screen.__init__(self, session)
        self['setupActions'] = ActionMap(['MSNweatherMapsActions'], {'keyCancel': self.cancel, 
           'keyOk': self.keyOk, 
           'keyRed': self.keyRed, 
           'keyGreen': self.keyGreen, 
           'keyYellow': self.keyYellow, 
           'keyBlue': self.keyBlue, 
           'key9': self.key9, 
           'key1': self.key1}, -2)
        self.setTitle(_('Weather maps'))
        self['BackgroundMap'] = Pixmap()
        self['MotionMap'] = Pixmap()
        self['ScaleMotionMap'] = j00zekAccellPixmap()
        self['ScalePic'] = Pixmap()
        self['Info'] = Label()
        self['TimeInfo'] = Label()
        self['key_red'] = Label() #Label(_('Temperature'))
        self['key_green'] = Label() #Label(_('Precipation'))
        self['key_yellow'] = Label() #Label(_('Satellite'))
        self['key_blue'] = Label() #Label(_('Cloud'))
        self['key_9'] = Label(_('Storms'))
        self['key_1'] = Label(_('meteogram'))
        self.onLayoutFinish.append(self.__onLayoutFinish)
        self.onShown.append(self.__onShown)
        self.onClose.append(self.__onClose)
        self.ImagesToDownloadList = []
        self.motionMapsList = []
        self.motionMapCurrIndex = 0
        self.motionMapsDir = _MD_
        self.showMotionMapTimer = eTimer()
        self.showMotionMapTimer.callback.append(self.showMotionMap)
        self.currentMotionMaps = None
        self.loadMotionMapsTimer = eTimer()
        self.loadMotionMapsTimer.callback.append(self.loadMotionMap)
        return

    def DEBUG(self, myFUNC='', myText=''):
        if DBG or config.plugins.MSNweatherNP.DebugEnabled.value:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG(myFUNC, myText, 'mapsNP.log', DBG)

    def __onLayoutFinish(self):
        self.DEBUG('__onLayoutFinish >>>')
        self.showIcon('BackgroundMap', '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/BackgroundMap.png')
        self.hideIcon('MotionMap')
        self.hideIcon('ScalePic')
        self.hideIcon('ScaleMotionMap')

    def __onClose(self):
        self.showMotionMapTimer.stop()
        self.loadMotionMapsTimer.stop()

    def __onShown(self):
        self.DEBUG('__onShown >>>')

    def delayedOnShown(self):
        self.DEBUG('delayedOnShown >>>')

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()

    def hideIcon(self, widgetName):
        self[widgetName].hide()

    def showIcon(self, widgetName, picFile=''):
        if os.path.exists(picFile):
            try:
                self[widgetName].updateIcon(picFile)
            except Exception:
                try:
                    self[widgetName].instance.setPixmap(LoadPixmap(path=picFile))
                except Exception:
                    self[widgetName].hide()

            self[widgetName].show()
        else:
            self[widgetName].hide()

    def keyRed(self):
        self.DEBUG('keyRed >>>')
        self['Info'].text = _("Downloading today's temperature maps...")
        self.showIcon('ScalePic', '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/scale_T_680x50.png')
        self.initiateLoadMotionMap('temperature_today')

    def keyGreen(self):
        self.DEBUG('keyGreen >>>')
        self['Info'].text = _('Downloading precipitation forecast maps...')
        self.showIcon('ScalePic', '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/scale_P_680x50.png')
        self.initiateLoadMotionMap('precipitation_forecast')

    def keyYellow(self):
        self.DEBUG('keyYellow >>>')
        self['Info'].text = _('Downloading satellite observation maps...')
        self.hideIcon('ScalePic')
        self.initiateLoadMotionMap('satellite_observation')

    def keyBlue(self):
        self.DEBUG('keyBlue >>>')
        self['Info'].text = _('Downloading clouds forecast maps...')
        self.hideIcon('ScalePic')
        self.initiateLoadMotionMap('clouds_forecast')

    def key9(self):
        self.DEBUG('key9 >>>')
        self['Info'].text = _('Loading storms maps...')
        self.hideIcon('ScalePic')
        self.initiateMotionMapFromFolder('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons', 'storms_', 'Storms observations')

    def key1(self):
        self.DEBUG('key1 >>>')
        self.showMotionMapTimer.stop()
        self.loadMotionMapsTimer.stop()
        self.hideIcon('ScalePic')
        self.hideIcon('MotionMap')
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/meteogram.png'):
            self['Info'].text = _('5 days meteogram for:')
            self['TimeInfo'].text = self.currForecaCity
            self.hideIcon('BackgroundMap')
            self.showIcon('ScaleMotionMap', '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/meteogram.png')
        else:
            self['Info'].text = _('meteogram not available, check configuration')

    def initiateMotionMapFromFolder(self, dirname, filePrefix, infoTXT):
        self.showMotionMapTimer.stop()
        self.loadMotionMapsTimer.stop()
        self.ImagesToDownloadList = []
        self.motionMapsList = []
        self.motionMapCurrIndex = 0
        self.hideIcon('MotionMap')
        self.hideIcon('ScaleMotionMap')
        self.showIcon('BackgroundMap', '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/BackgroundMap.png')
        for f in os.listdir(dirname):
            if f.startswith(filePrefix) and f.endswith('.png') and os.path.isfile('%s/%s' % (dirname, f)):
                self.motionMapsList.append(('%s/%s' % (dirname, f), ''))

        if len(self.motionMapsList) > 0:
            self.motionMapsList.sort()
            self.showMotionMapTimer.start(50, True)
        self['Info'].text = _(infoTXT)

    def downloadMap(self, MapFile):
        self.DEBUG('downloadMap(MapFile="%s") >>>' % MapFile)
        MapsToDownload = []
        MapsToDownload.append(MapFile)
        if self.motionMapCurrIndex + 1 < len(self.ImagesToDownloadList):
            MapFile = self.ImagesToDownloadList[(self.motionMapCurrIndex + 1)][0]
            if not os.path.exists(MapFile):
                MapsToDownload.append(MapFile)
        for currMapFile in MapsToDownload:
            if not os.path.exists(currMapFile):
                try:
                    filedata = downloadWebPage(webURL = self.ImagesToDownloadList[self.motionMapCurrIndex][1], doUnquote = False)
                    with open(currMapFile, 'wb') as (f):
                        f.write(filedata)
                except Exception:
                    self.DEBUG('Error sychronizing webMaps data')

    def showMotionMap(self):
        start_time = time.time()
        self.showMotionMapTimer.stop()
        self.DEBUG('showMotionMap loading img-id="%s"' % self.motionMapCurrIndex)
        if len(self.ImagesToDownloadList) > 0:
            currMapFile = self.ImagesToDownloadList[self.motionMapCurrIndex][0]
            self.downloadMap(currMapFile)
            currMotionMapWidget = 'MotionMap'
        elif len(self.motionMapsList) > 0:
            currMapFile = self.motionMapsList[self.motionMapCurrIndex][0]
            currMotionMapWidget = 'ScaleMotionMap'
        else:
            currMapFile = 'NotAvailable'
        self.DEBUG('showMotionMap loading img="%s"' % currMapFile)
        if os.path.exists(currMapFile) and os.path.isfile(currMapFile):
            self.showIcon(currMotionMapWidget, currMapFile)
            picName = os.path.basename(currMapFile)[os.path.basename(currMapFile).find('_') + 1:-4]
            try:
                picDate = '%s:%s %s/%s/%s' % (picName[8:10], picName[10:12], picName[6:8], picName[4:6], picName[:4])
            except Exception:
                picDate = picName

            self['TimeInfo'].text = picDate
        self.motionMapCurrIndex += 1
        if len(self.ImagesToDownloadList) > 0 and self.motionMapCurrIndex >= len(self.ImagesToDownloadList) or len(self.motionMapsList) > 0 and self.motionMapCurrIndex >= len(self.motionMapsList):
            self.motionMapCurrIndex = 0
        elapsed_time = int((time.time() - start_time) * 1000)
        self.showMotionMapTimer.start(1000, True)
        self.DEBUG('showMotionMap elapsed_time="%s" ms' % elapsed_time)

    def initiateLoadMotionMap(self, currentMotionMaps):
        self.showMotionMapTimer.stop()
        self.loadMotionMapsTimer.stop()
        self.hideIcon('MotionMap')
        self.hideIcon('ScaleMotionMap')
        self.showIcon('BackgroundMap', '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/BackgroundMap.png')
        self.currentMotionMaps = currentMotionMaps
        self.loadMotionMapsTimer.start(50, True)

    def loadMotionMap(self):
        self.loadMotionMapsTimer.stop()
        self.ImagesToDownloadList = []
        self.motionMapsList = []
        self.motionMapCurrIndex = 0
        self['Info'].text, self.ImagesToDownloadList = motionMaps(self.currentMotionMaps, self.motionMapsDir)
        self.DEBUG('loadMotionMap %s maps found' % len(self.ImagesToDownloadList))
        if len(self.ImagesToDownloadList) > 0:
            self.showMotionMapTimer.start(50, True)
