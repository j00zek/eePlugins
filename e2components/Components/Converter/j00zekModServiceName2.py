# -*- coding: utf-8 -*-
#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
#
# Extended ServiceName Converter for Enigma2 Dreamboxes (ServiceName2.py)
# Coded by vlamo (c) 2011
#
# Version: 0.4 (03.06.2011 18:40)
# Version: 0.5 (08.09.2012) add Alternative numbering mode support - Dmitry73 & 2boom
# Version: 0.6 (19.10.2012) add stream mapping
# Version: 0.7 (19.09.2013) add iptv info - nikolasi & 2boom
# Version: 0.8 (29.10.2013) add correct output channelnumner - Dmitry73
# Version: 0.9 (18.11.2013) code fix and optimization - Taapat & nikolasi
# Version: 1.0 (04.12.2013) code fix and optimization - Dmitry73
# Version: 1.1 (06-17.12.2013) small cosmetic fix - 2boom
# Version: 1.2 (25.12.2013) small iptv fix - MegAndretH
# Version: 1.3 (27.01.2014) small iptv fix - 2boom
# Version: 1.4 (30.06.2014) fix iptv reference - 2boom
# Version: 1.5 (04.07.2014) fix iptv reference cosmetic - 2boom
# Version: 1.6 (14.10.2014) add Tricolor Sibir prov - 2boom
# Version: 1.7 (10.03.2015) remove Tricolor Sibir prov - 2boom
# Version: 1.8 (15.03.2015) add custom provname - 2boom
# Version: 1.9 (31.07.2015) add custom provname for custom name channel- 2boom
# Version: 2.0 (29.08.2015) custom provname fix - 2boom
# Version: 2.1 (07.01.2019) add DVB-T2 DVB-C2 system - Sirius
# Version: 2.2 (07.01.2019) remove iptv provname add iptv list /etc/enigma2/iptvprov.list - Vasiliks
# Version: 2.3 (15.01.2019) add terrestrial description - ikrom
# Version: 2.3 (23.01.2020) add returning Name & event & progress - j00zek

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekModHex2strColor import Hex2strColor, clr
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceReference, eServiceCenter, eTimer, getBestPlayableServiceReference, eEPGCache
from time import time, localtime, strftime
import NavigationInstance
import os

try:
    from Components.Renderer.ChannelNumber import ChannelNumberClasses
    correctChannelNumber = True
except:
    correctChannelNumber = False

#if enabled log into /tmp/e2components.log
DBG = False
if DBG: from Components.j00zekComponents import j00zekDEBUG 

class j00zekModServiceName2(Converter, object):
    NAME = 0
    NUMBER = 1
    BOUQUET = 2
    PROVIDER = 3
    REFERENCE = 4
    ORBPOS = 5
    TPRDATA = 6
    SATELLITE = 7
    ALLREF = 8
    FORMAT = 9
    USE_VFD_CFG = 10
    USE_CFG = 11

#Format description:
# %A - AllRef           E.g. 1:0:1:3DD3:640:13E:820000:0:0:0
# %B - Bouquet name     E.g. PL, aktualizacja 07-01-2020
# %b -                  E.g. ?
# %c -                  E.g. ?
# %D - TIME             E.g. 07:18
# %d - TIME             E.g. 7:18 
# %E - Event Name       E.g. Fakty
# %e - Event progress%  E.g. ?
# %F - frequency        E.g. 11508
# %f -                  E.g. 3/4
# %g -                  E.g. ? 
# %h -                  E.g. ? 
# %i -                  E.g. Auto
# %M -                  E.g. 8PSK
# %m -                  E.g. ? 
# %N - Channel Name     E.g. TVN7 HD
# %n - Channel Number   E.g. 8
# %l -                  E.g. ?
# %O -                  E.g. 13.0
# %o -                  E.g. Auto
# %P - Provider         E.g. TVN
# %p - polarisation     E.g. V
# %R - Reference        E.g. 1:0:1:3DD3:640:13E:820000:0:0:0::TVN7 HD
# %r -                  E.g. 0.20
# %S - Satellite Name   E.g. 13.0E Hotbird 13B/13C/13E
# %s -                  E.g. DVB-S2
# %T -                  E.g. 13.0°E 11508 V 27500 3/4
# %t -                  E.g. Satelita
# %Y -                  E.g. 27500
# Example of definition >%F  %Y %p  %f  %s  %M (%O)<

#%cY yellow
    
    def __init__(self, type):
        Converter.__init__(self, type)
        
        self.colors = (0x0000FF00, 0x00FFFF00, 0x007F7F7F) # tuner active, busy, available colors
        self.epgQuery = eEPGCache.getInstance().lookupEventTime
        if DBG: j00zekDEBUG('[j00zekModServiceName2:__init__] >>> type=%s' % type) 
        if type == "Name" or not len(str(type)):
            self.type = self.NAME
        elif type == "Number":
            self.type = self.NUMBER
        elif type == "Bouquet":
            self.type = self.BOUQUET
        elif type == "Provider":
            self.type = self.PROVIDER
        elif type == "Reference":
            self.type = self.REFERENCE
        elif type == "OrbitalPos":
            self.type = self.ORBPOS
        elif type == "TpansponderInfo":
            self.type = self.TPRDATA
        elif type == "Satellite":
            self.type = self.SATELLITE
        elif type == "AllRef":
            self.type = self.ALLREF
        elif type == 'UseVFDcfg':
            self.type = self.USE_VFD_CFG
        elif type == 'UseCFG':
            self.type = self.USE_CFG
        else:
            self.type = self.FORMAT
            self.sfmt = type[:]
        try:
            if (self.type == self.NUMBER or (self.type == self.FORMAT or self.type == self.USE_CFG or self.type == self.USE_VFD_CFG and '%n' in self.sfmt)) and correctChannelNumber:
                ChannelNumberClasses.append(self.forceChanged)
        except:
            pass
        self.refstr = self.isStream = self.ref = self.info = self.what = self.tpdata = None
        self.Timer = eTimer()
        self.Timer.callback.append(self.neededChange)
        self.IPTVcontrol = self.isAdditionalService(type=0)
        self.AlternativeControl = self.isAdditionalService(type=1)

    def isAdditionalService(self, type=0):
        def searchService(serviceHandler, bouquet):
            istype = False
            servicelist = serviceHandler.list(bouquet)
            if not servicelist is None:
                while True:
                    s = servicelist.getNext()
                    if not s.valid(): break
                    if not (s.flags & (eServiceReference.isMarker|eServiceReference.isDirectory)):
                        if type:
                            if s.flags & eServiceReference.isGroup:
                                istype = True
                                return istype
                        else:
                            if "%3a//" in s.toString().lower(): 
                                istype = True
                                return istype
            return istype

        isService = False
        serviceHandler = eServiceCenter.getInstance()
        if not config.usage.multibouquet.value:
            service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
            rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(service_types_tv)
        else:
            rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        bouquet = eServiceReference(rootstr)
        if not config.usage.multibouquet.value:
            isService = searchService(serviceHandler, bouquet)
        else:
            bouquetlist = serviceHandler.list(bouquet)
            if not bouquetlist is None:
                while True:
                    bouquet = bouquetlist.getNext()
                    if not bouquet.valid(): break
                    if bouquet.flags & eServiceReference.isDirectory:
                        isService = searchService(serviceHandler, bouquet)
                        if isService: break
        return isService 

    def getServiceNumber(self, ref):
        def searchHelper(serviceHandler, num, bouquet):
            servicelist = serviceHandler.list(bouquet)
            if not servicelist is None:
                while True:
                    s = servicelist.getNext()
                    if not s.valid(): break
                    if not (s.flags & (eServiceReference.isMarker|eServiceReference.isDirectory)):
                        num += 1
                        if s == ref: return s, num
            return None, num

        if isinstance(ref, eServiceReference):
            isRadioService = ref.getData(0) in (2,10)
            lastpath = isRadioService and config.radio.lastroot.value or config.tv.lastroot.value
            if 'FROM BOUQUET' not in lastpath:
                if 'FROM PROVIDERS' in lastpath:
                    return 'P', 'Provider'
                if 'FROM SATELLITES' in lastpath:
                    return 'S', 'Satellites'
                if ') ORDER BY name' in lastpath:
                    return 'A', 'All Services'
                return 0, 'N/A'
            try:
                acount = config.plugins.NumberZapExt.enable.value and config.plugins.NumberZapExt.acount.value or config.usage.alternative_number_mode.value
            except:
                acount = False
            rootstr = ''
            for x in lastpath.split(';'):
                if x != '': rootstr = x
            serviceHandler = eServiceCenter.getInstance()
            if acount is True or not config.usage.multibouquet.value:
                bouquet = eServiceReference(rootstr)
                service, number = searchHelper(serviceHandler, 0, bouquet)
            else:
                if isRadioService:
                    bqrootstr = '1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet'
                else:
                    bqrootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
                number = 0
                cur = eServiceReference(rootstr)
                bouquet = eServiceReference(bqrootstr)
                bouquetlist = serviceHandler.list(bouquet)
                if not bouquetlist is None:
                    while True:
                        bouquet = bouquetlist.getNext()
                        if not bouquet.valid(): break
                        if bouquet.flags & eServiceReference.isDirectory:
                            service, number = searchHelper(serviceHandler, number, bouquet)
                            if not service is None and cur == bouquet: break
            if not service is None:
                info = serviceHandler.info(bouquet)
                name = info and info.getName(bouquet) or ''
                return number, name
        return 0, ''

    def getProviderName(self, ref):
        if isinstance(ref, eServiceReference):
            from Screens.ChannelSelection import service_types_radio, service_types_tv
            typestr = ref.getData(0) in (2,10) and service_types_radio or service_types_tv
            pos = typestr.rfind(':')
            rootstr = '%s (channelID == %08x%04x%04x) && %s FROM PROVIDERS ORDER BY name' %(typestr[:pos+1],ref.getUnsignedData(4),ref.getUnsignedData(2),ref.getUnsignedData(3),typestr[pos+1:])
            provider_root = eServiceReference(rootstr)
            serviceHandler = eServiceCenter.getInstance()
            providerlist = serviceHandler.list(provider_root)
            if not providerlist is None:
                while True:
                    provider = providerlist.getNext()
                    if not provider.valid(): break
                    if provider.flags & eServiceReference.isDirectory:
                        servicelist = serviceHandler.list(provider)
                        if not servicelist is None:
                            while True:
                                service = servicelist.getNext()
                                if not service.valid(): break
                                if service == ref:
                                    info = serviceHandler.info(provider)
                                    return info and info.getName(provider) or "Unknown"
        return ""

    def getTransponderInfo(self, info, ref, fmt):
        result = ""
        if self.tpdata is None:
            if ref:
                self.tpdata = ref and info.getInfoObject(ref, iServiceInformation.sTransponderData)
            else:
                self.tpdata = info.getInfoObject(iServiceInformation.sTransponderData)
            if not isinstance(self.tpdata, dict):
                self.tpdata = None
                return result
        if self.isStream:
            type = 'IP-TV'
        else:
            type = self.tpdata.get('tuner_type', '')
        if not fmt or fmt == 'T':
            if type == 'DVB-C':
                fmt = ["t ","F ","Y ","i ","f ","M"]    #(type frequency symbol_rate inversion fec modulation)
            elif type == 'DVB-T':
                if ref:
                    fmt = ["O ","F ","h ","m ","g ","c"]    #(orbital_position code_rate_hp transmission_mode guard_interval constellation)
                else:
                    fmt = ["t ","F ","h ","m ","g ","c"]    #(type frequency code_rate_hp transmission_mode guard_interval constellation)
            elif type == 'IP-TV':
                return _("Streaming")
            else:
                fmt = ["O ","F ","p ","Y ","f"]        #(orbital_position frequency polarization symbol_rate fec)
        for line in fmt:
            f = line[:1]
            if f == 't':    # %t - tuner_type (dvb-s/s2/c/t)
                if type == 'DVB-S':
                    result += _("Satellite")
                elif type == 'DVB-C':
                    result += _("Cable")
                elif type == 'DVB-T':
                    result += _("Terrestrial")
                elif type == 'IP-TV':
                    result += _('Stream-tv')
                else:
                    result += 'N/A'
            elif f == 's':    # %s - system (dvb-s/s2/c/t)
                if type == 'DVB-S':
                    x = self.tpdata.get('system', 0)
                    result += x in list(range(2)) and {0:'DVB-S',1:'DVB-S2'}[x] or ''
                elif type == 'DVB-C':
                    x = self.tpdata.get('system', 0)
                    result += x in list(range(2)) and {0:'DVB-C',1:'DVB-C2'}[x] or ''
                elif type == 'DVB-T':
                    x = self.tpdata.get('system', 0)
                    result += x in list(range(2)) and {0:'DVB-T',1:'DVB-T2'}[x] or ''
                else:
                    result += type
            elif f == 'F':    # %F - frequency (dvb-s/s2/c/t) in KHz
                if type in ('DVB-S','DVB-C','DVB-T'):
                   result += '%d'% round(self.tpdata.get('frequency', 0) / 1000.0) 
            elif f == 'f':    # %f - fec_inner (dvb-s/s2/c/t)
                if type in ('DVB-S','DVB-C'):
                    x = self.tpdata.get('fec_inner', 15)
                    result += x in list(range(10))+[15] and {0:'Auto',1:'1/2',2:'2/3',3:'3/4',4:'5/6',5:'7/8',6:'8/9',7:'3/5',8:'4/5',9:'9/10',15:'None'}[x] or ''
                elif type == 'DVB-T':
                    x = self.tpdata.get('code_rate_lp', 5)
                    result += x in list(range(6)) and {0:'1/2',1:'2/3',2:'3/4',3:'5/6',4:'7/8',5:'Auto'}[x] or ''
            elif f == 'i':    # %i - inversion (dvb-s/s2/c/t)
                if type in ('DVB-S','DVB-C','DVB-T'):
                    x = self.tpdata.get('inversion', 2)
                    result += x in list(range(3)) and {0:'On',1:'Off',2:'Auto'}[x] or ''
            elif f == 'O':    # %O - orbital_position (dvb-s/s2)
                if type == 'DVB-S':
                    x = self.tpdata.get('orbital_position', 0)
                    result += x > 1800 and "%d.%d°W"%((3600-x)/10, (3600-x)%10) or "%d.%d°E"%(x/10, x%10)
                elif type == 'DVB-T':
                    x = self.tpdata.get('system', 0)
                    result += x in list(range(2)) and {0:'DVB-T',1:'DVB-T2'}[x] or ''
                elif type == 'DVB-C':
                    result += 'DVB-C'
                elif type == 'Iptv':
                    result += 'Stream'
            elif f == 'M':    # %M - modulation (dvb-s/s2/c)
                x = self.tpdata.get('modulation', 1)
                if type == 'DVB-S':
                    result += x in list(range(4)) and {0:'Auto',1:'QPSK',2:'8PSK',3:'QAM16'}[x] or ''
                elif type == 'DVB-C':
                    result += x in list(range(6)) and {0:'Auto',1:'QAM16',2:'QAM32',3:'QAM64',4:'QAM128',5:'QAM256'}[x] or ''
            elif f == 'p':    # %p - polarization (dvb-s/s2)
                if type == 'DVB-S':
                    x = self.tpdata.get('polarization', 0)
                    result += x in list(range(4)) and {0:'H',1:'V',2:'L',3:'R'}[x] or '?'
            elif f == 'Y':    # %Y - symbol_rate (dvb-s/s2/c)
                if type in ('DVB-S','DVB-C'):
                    result += '%d'%(self.tpdata.get('symbol_rate', 0) / 1000)
            elif f == 'r':    # %r - rolloff (dvb-s2)
                if not self.isStream:
                    x = self.tpdata.get('rolloff')
                    if not x is None:
                        result += x in list(range(3)) and {0:'0.35',1:'0.25',2:'0.20'}[x] or ''
            elif f == 'o':    # %o - pilot (dvb-s2)
                if not self.isStream:
                    x = self.tpdata.get('pilot')
                    if not x is None:
                        result += x in list(range(3)) and {0:'Off',1:'On',2:'Auto'}[x] or ''
            elif f == 'c':    # %c - constellation (dvb-t)
                if type == 'DVB-T':
                    x = self.tpdata.get('constellation', 3)
                    result += x in list(range(4)) and {0:'QPSK',1:'QAM16',2:'QAM64',3:'Auto'}[x] or ''
            elif f == 'l':    # %l - code_rate_lp (dvb-t)
                if type == 'DVB-T':
                    x = self.tpdata.get('code_rate_lp', 5)
                    result += x in list(range(6)) and {0:'1/2',1:'2/3',2:'3/4',3:'5/6',4:'7/8',5:'Auto'}[x] or ''
            elif f == 'h':    # %h - code_rate_hp (dvb-t)
                if type == 'DVB-T':
                    x = self.tpdata.get('code_rate_hp', 5)
                    result += x in list(range(6)) and {0:'1/2',1:'2/3',2:'3/4',3:'5/6',4:'7/8',5:'Auto'}[x] or ''
            elif f == 'm':    # %m - transmission_mode (dvb-t)
                if type == 'DVB-T':
                    x = self.tpdata.get('transmission_mode', 2)
                    result += x in list(range(3)) and {0:'2k',1:'8k',2:'Auto'}[x] or ''
            elif f == 'g':    # %g - guard_interval (dvb-t)
                if type == 'DVB-T':
                    x = self.tpdata.get('guard_interval', 4)
                    result += x in list(range(5)) and {0:'1/32',1:'1/16',2:'1/8',3:'1/4',4:'Auto'}[x] or ''
            elif f == 'b':    # %b - bandwidth (dvb-t)
                if type == 'DVB-T':
                    x = self.tpdata.get('bandwidth', 1)
                    result += x in list(range(4)) and {0:'8 MHz',1:'7 MHz',2:'6 MHz',3:'Auto'}[x] or ''
            elif f == 'e':    # %e - hierarchy_information (dvb-t)
                if type == 'DVB-T':
                    x = self.tpdata.get('hierarchy_information', 4)
                    result += x in list(range(5)) and {0:'None',1:'1',2:'2',3:'4',4:'Auto'}[x] or ''
            result += line[1:]
        return result

    def getSatelliteName(self, ref):
        if isinstance(ref, eServiceReference):
            orbpos = ref.getUnsignedData(4) >> 16
            if orbpos == 0xFFFF: #Cable
                return _("Cable")
            elif orbpos == 0xEEEE: #Terrestrial
                try:
                    nimfile = open('/proc/bus/nim_sockets')
                    current_slot = None
                    for line in nimfile:
                        if not line:
                            break
                        line = line.strip()
                        if line.startswith('NIM Socket'):
                            parts = line.split(' ')
                            current_slot = int(parts[2][:-1])
                    if not current_slot is None:
                        from Components.NimManager import nimmanager
                        return str(nimmanager.getTerrestrialDescription(current_slot))
                except Exception:
                    pass
                return _("Terrestrial")
            else: #Satellite
                orbpos = ref.getData(4) >> 16
                if orbpos < 0: orbpos += 3600
                try:
                    from Components.NimManager import nimmanager
                    return str(nimmanager.getSatDescription(orbpos))
                except:
                    dir = ref.flags & (eServiceReference.isDirectory|eServiceReference.isMarker)
                    if not dir:
                        refString = ref.toString().lower()
                        if refString.startswith("-1"):
                            return ''
                        elif refString.startswith("1:134:"):
                            return _("Alternative")
                        elif refString.startswith("4097:"):
                            return _("Internet")
                        else:
                            return orbpos > 1800 and "%d.%d°W"%((3600-orbpos)/10, (3600-orbpos)%10) or "%d.%d°E"%(orbpos/10, orbpos%10)
        return ""

    def getIPTVProvider(self, refstr):
        if os.path.isfile('/etc/enigma2/iptvprov.list'):
            with open('/etc/enigma2/iptvprov.list', "r") as f:
                for d in f.readlines():
                    if d.split(',')[0] in refstr:
                        return d.split(',')[1].strip()
        if 'tvshka' in refstr:
            return "SCHURA"
        elif 'udp/239.0.1' in refstr:
            return "Lanet"
        elif 'kirito.la.net.ua' in refstr:
            return "Lanet"
        elif '3a7777' in refstr:
            return "IPTVNTV"
        elif 'KartinaTV' in refstr:
            return "KartinaTV"
        elif 'Megaimpuls' in refstr:
            return "MEGAIMPULSTV"
        elif 'Newrus' in refstr:
            return "NEWRUSTV"
        elif 'Sovok' in refstr:
            return "SOVOKTV"
        elif 'Rodnoe' in refstr:
            return "RODNOETV"
        elif '238.1.1.' in refstr:
            return "Matrix"
        elif 'cdnet' in refstr:
            return "NonameTV"
        elif 'unicast' in refstr:
            return "StarLink"
        elif 'udp/239.255.2.' in refstr:
            return "Planeta"
        elif 'udp/233.7.70.' in refstr:
            return "Rostelecom"
        elif 'udp/239.1.1.' in refstr:
            return "Real"
        elif 'udp/238.0.' in refstr or 'udp/233.191.' in refstr:
            return "Triolan"
        elif '%3a8208' in refstr:
            return "MovieStar"
        elif 'udp/239.0.0.' in refstr:
            return "Trinity"
        elif 'udp/239.100.' in refstr or 'udp/233.252.8.' in refstr or 'udp/225.225.225.' in refstr or 'udp/225.1.' in refstr:
            return "Volia TV"
        elif '.cn.ru' in refstr or 'novotelecom' in refstr:
            return "Novotelecom"
        elif 'www.youtube.com' in refstr:
            return "www.youtube.com"
        elif '.torrent-tv.ru' in refstr:
            return "torrent-tv.ru"
        elif 'tv.lifelink.ru' in refstr:
            return "tv.lifelink.ru"
        elif 'sat-elit.net' in refstr:
            return "iptv.sat-elit.net"
        elif '//91.201.' in refstr:
            return "www.livehd.tv"
        elif 'web.tvbox.md' in refstr:
            return "web.tvbox.md"
        elif 'live-p12' in refstr:
            return "PAC12"
        elif '%3a1234' in refstr:
            return "IPTV1"
        elif 'itv.world' in refstr:
            return "itv world"
        elif 'cableguy' in refstr:
            return "Cableguy IPTV"
        elif '4097' in refstr or '5001' in refstr or '5002' in refstr:
            return "StreamTV"
        return ""

    def getPlayingref(self, ref):
        playingref = None
        if NavigationInstance.instance:
            playingref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
        if not playingref:
            playingref = eServiceReference()
        return playingref

    def resolveAlternate(self, ref):
        nref = getBestPlayableServiceReference(ref, self.getPlayingref(ref))
        if not nref:
            nref = getBestPlayableServiceReference(ref, eServiceReference(), True)
        return nref

    def getReferenceType(self, refstr, ref):
        if ref is None:
            if NavigationInstance.instance:
                playref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                if playref:
                    refstr = playref.toString() or ''
                    prefix = ''
                    if refstr.startswith("4097:"):
                        prefix += "GStreamer "
                    if '%3a//' in refstr:
                        sref = ' '.join(refstr.split(':')[10:])
                        refstr = prefix + sref
                    else:
                        sref = ':'.join(refstr.split(':')[:10])
                        refstr = prefix + sref
        else:
            if refstr != '':
                prefix = ''
                if refstr.startswith("1:7:"):
                    if 'FROM BOUQUET' in refstr:
                        prefix += "Bouquet "
                    elif '(provider == ' in refstr:
                        prefix += "Provider "
                    elif '(satellitePosition == ' in refstr:
                        prefix += "Satellit "
                    elif '(channelID == ' in refstr:
                        prefix += "Current tr "
                elif refstr.startswith("1:134:"):
                    prefix += "Alter "
                elif refstr.startswith("1:64:"):
                    prefix += "Marker "
                elif refstr.startswith("4097:"):
                    prefix += "GStreamer "
                if self.isStream:
                    if self.refstr:
                        if '%3a//' in self.refstr:
                            sref = ' '.join(self.refstr.split(':')[10:])
                        else:
                            sref = ':'.join(self.refstr.split(':')[:10])
                    else:
                        sref = ' '.join(refstr.split(':')[10:])
                    return prefix + sref
                else:
                    if self.refstr:
                        sref = ':'.join(self.refstr.split(':')[:10])
                    else:
                        sref = ':'.join(refstr.split(':')[:10])
                    return prefix + sref
        return refstr

    @cached
    def getText(self):
        if DBG: j00zekDEBUG('[j00zekModServiceName2:getText] >>> self.type=%s' % self.type) 
        service = self.source.service
        if isinstance(service, iPlayableServicePtr):
            info = service and service.info()
            ref = None
        else: # reference
            info = service and self.source.info
            ref = service
        if not info: return ""
        if ref:
            refstr = ref.toString()
        else:
            refstr = info.getInfoString(iServiceInformation.sServiceref)
        if refstr is None:
            refstr = ''
        if self.AlternativeControl: 
            if ref and refstr.startswith("1:134:") and self.ref is None:
                nref = self.resolveAlternate(ref)
                if nref:
                    self.ref = nref
                    self.info = eServiceCenter.getInstance().info(self.ref)
                    self.refstr = self.ref.toString()
                    if not self.info: return ""
        if self.IPTVcontrol:
            if '%3a//' in refstr or (self.refstr and '%3a//' in self.refstr) or refstr.startswith("4097:"):
                self.isStream = True
        if self.type == self.NAME:
            name = ref and (info.getName(ref) or 'N/A') or (info.getName() or 'N/A')
            prefix = ''
            if self.ref:
                prefix = " (alter)"
            name += prefix
            return name.replace('\xc2\x86', '').replace('\xc2\x87', '')
        elif self.type == self.NUMBER:
            try:
                service = self.source.serviceref
                num = service and service.getChannelNum() or None
            except:
                num = None
            if num:
                return str(num)
            else:
                num, bouq = self.getServiceNumber(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
                return num and str(num) or ''
        elif self.type == self.BOUQUET:
            num, bouq = self.getServiceNumber(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
            return bouq
        elif self.type == self.PROVIDER:
            tmpprov = tmpsat = ''
            if self.isStream:
                if self.refstr and ('%3a//' in self.refstr or '%3a//' in self.refstr):
                    return self.getIPTVProvider(self.refstr)
                return self.getIPTVProvider(refstr)
            else:
                if self.ref:
                    tmpprov += self.getProviderName(self.ref)
                if ref:
                    tmpprov += self.getProviderName(ref)
                else: 
                    tmpprov += info.getInfoString(iServiceInformation.sProvider) or ''
            if self.ref and self.info:
                tmpsat +=  self.getTransponderInfo(self.info, self.ref, 'O')
            else:
                tmpsat += self.getTransponderInfo(info, ref, 'O')
            if 'tricolor' in tmpprov.lower() and tmpsat.startswith('56'):
                return '%s %s' % (tmpprov, 'Sibir')
            else:
                return tmpprov
        elif self.type == self.REFERENCE:
            if self.refstr:
                return self.refstr
            return refstr
        elif self.type == self.ORBPOS:
            if self.isStream:
                return "Stream"
            else:
                if self.ref and self.info:
                    return self.getTransponderInfo(self.info, self.ref, 'O')
                return self.getTransponderInfo(info, ref, 'O')
        elif self.type == self.TPRDATA:
            if self.isStream:
                return _("Streaming")
            else:
                if self.ref and self.info:
                    return self.getTransponderInfo(self.info, self.ref, 'T')
                return self.getTransponderInfo(info, ref, 'T')
        elif self.type == self.SATELLITE:
            if self.isStream:
                return _("Internet")
            else:
                if self.ref:
                    return self.getSatelliteName(self.ref)
            #test#
                return self.getSatelliteName(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
        elif self.type == self.ALLREF:
            tmpref = self.getReferenceType(refstr, ref)
            if 'Bouquet' in tmpref or 'Satellit' in tmpref or 'Provider' in tmpref:
                return ' '
            elif '%3a' in tmpref:
                return ':'.join(refstr.split(':')[:10])
            return tmpref
        elif self.type == self.FORMAT or self.type == self.USE_VFD_CFG  or self.type == self.USE_CFG:
            if self.type == self.USE_VFD_CFG:
                self.sfmt = config.plugins.j00zekCC.snVFDtype.value[:]
                if DBG: j00zekDEBUG('[j00zekModServiceName2:getText] snVFDtype=%s' % self.sfmt)
            elif self.type == self.USE_CFG:
                self.sfmt = config.plugins.j00zekCC.snINFOtype.value[:]
                if DBG: j00zekDEBUG('[j00zekModServiceName2:getText] snINFOtype=%s' % self.sfmt)
            num = bouq = ''
            tmp = self.sfmt[:].split("%")
            if tmp:
                ret = tmp[0]
                tmp.remove(ret)
            else:
                return ""
            for line in tmp:
                LineSpilitChar = 1
                f = line[:LineSpilitChar]
                colDef = line[1:].strip()
                if f == 'c' and colDef in ('Y','R','G','B','Gray'):
                    ret += clr.get(colDef, Hex2strColor(0x00e6e6e6))
                    LineSpilitChar += len(colDef)
                elif f == 'N':      # %N - Name
                    name = ref and (info.getName(ref) or 'N/A') or (info.getName() or 'N/A')
                    postfix = ''
                    if self.ref:
                        postfix = " (alter)"
                    name += postfix
                    ret += name.replace('\xc2\x86', '').replace('\xc2\x87', '')
                elif f == 'n':    # %n - Number
                    try:
                        service = self.source.serviceref
                        num = service and service.getChannelNum() or None
                    except:
                        num = None
                    if num:
                        ret += str(num)
                    else:
                        num, bouq = self.getServiceNumber(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
                        ret += num and str(num) or ''
                elif f == 'B':    # %B - Bouquet
                    num, bouq = self.getServiceNumber(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
                    ret += bouq
                elif f == 'P':    # %P - Provider
                    if self.isStream:
                        if self.refstr and '%3a//' in self.refstr:
                            ret += self.getIPTVProvider(self.refstr)
                        else:
                            ret += self.getIPTVProvider(refstr)
                    else:
                        if self.ref:
                            ret += self.getProviderName(self.ref)
                        else:
                            if ref:
                                ret += self.getProviderName(ref)
                            else: 
                                ret += info.getInfoString(iServiceInformation.sProvider) or ''
                elif f == 'R':    # %R - Reference
                    if self.refstr:
                        ret += self.refstr
                    else:
                        ret += refstr
                elif f == 'S':    # %S - Satellite Name
                    if self.isStream:
                        ret += _("Internet")
                    else:
                        if self.ref:
                            ret += self.getSatelliteName(self.ref)
                        else:
                            ret += self.getSatelliteName(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
                elif f == 'A':    # %A - AllRef
                    tmpref = self.getReferenceType(refstr, ref)
                    if 'Bouquet' in tmpref or 'Satellit' in tmpref or 'Provider' in tmpref:
                        ret += ' '
                    elif '%3a' in tmpref:
                        ret += ':'.join(refstr.split(':')[:10])
                    else:
                        ret += tmpref
                elif f == 'E':    # %E - Event Name
                    act_event = info and info.getEvent(0)
                    if not act_event and info:
                        refstr = info.getInfoString(iServiceInformation.sServiceref)
                        act_event = self.epgQuery(eServiceReference(refstr), -1, 0)
                    if not act_event is None:
                        ret += act_event.getEventName()
                elif f == 'e':    # %e - Event Progress in %
                    act_event = info and info.getEvent(0)
                    if not act_event and info:
                        refstr = info.getInfoString(iServiceInformation.sServiceref)
                        act_event = self.epgQuery(eServiceReference(refstr), -1, 0)
                    if not act_event is None:
                        eventDuration = act_event.getDuration()
                        eventProgress = int(time()) - act_event.getBeginTime()
                        if eventDuration > 0 and eventProgress >= 0:
                            if eventProgress > eventDuration:
                                eventProgress = eventDuration
                            ret += '%s%%' % int(100 * eventProgress / eventDuration)
                elif f == 'D':    # %D
                    ret += strftime('%H:%M',localtime()) 
                elif f == 'd':    # %d
                    ret += strftime('%-H:%M',localtime()) 
                #the rest
                elif f in 'TtsFfiOMpYroclhmgb':
                    if self.ref:
                        ret += self.getTransponderInfo(self.info, self.ref, f)
                    else:
                        ret += self.getTransponderInfo(info, ref, f)
                ret += line[LineSpilitChar:]
                if DBG: j00zekDEBUG("[j00zekModServiceName2:getText] >>> after '%s' ret='%s'" % (f,ret))
            return '%s'%(ret.replace('N/A', '').strip())

    text = property(getText)

    def neededChange(self):
        if self.what:
            Converter.changed(self, self.what)
            self.what = None

    def forceChanged(self, what):
        if what == True:
            self.refstr = self.isStream = self.ref = self.info = self.tpdata = None
            Converter.changed(self, (self.CHANGED_ALL,))
            self.what = None

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
            self.refstr = self.isStream = self.ref = self.info = self.tpdata = None
            if self.type in (self.NUMBER,self.BOUQUET) or \
                (self.type == self.FORMAT and ('%n' in self.sfmt or '%B' or '%D' in self.sfmt or '%d' in self.sfmt in self.sfmt or '%e' in self.sfmt)):
                self.what = what
                self.Timer.start(1000, True)
            else:
                Converter.changed(self, what)
