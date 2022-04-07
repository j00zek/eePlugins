#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
# BlackHarmonyServiceInfoEX >j00zekModServiceInfoEX
# Copyright (c) 2boom 2013-14
# v.1.4.0 27.04.2014
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# 26.11.2018 add terrestrial and cable type mod by Sirius
# 01.12.2018 fix video codec mod by Sirius

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from enigma import iServiceInformation, iPlayableService
from Components.config import config
from Components.Element import cached

DBG = False
if DBG: 
    try: from Components.j00zekComponents import j00zekDEBUG
    except Exception: DBG = False

stream_codec = {-1: ' ', 0: 'MPEG2', 1: 'MPEG4', 2: 'MPEG1', 3: 'MPEG4-II', 4: 'VC1', 5: 'VC1-SM', 6: 'HEVC', 7: ' '}
WIDESCREEN = [3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10]

class j00zekModServiceInfoEX(Poll, Converter, object):
    apid = 0
    vpid = 1
    sid = 2
    onid = 3
    tsid = 4
    prcpid = 5
    caids = 6
    pmtpid = 7
    txtpid = 8
    xres = 9
    yres = 10
    atype = 11
    vtype = 12
    avtype = 13
    fps = 14
    tbps = 15
    vsize = 16
    ttype = 17
    format = 18
    XRES = 19
    YRES = 20
    IS_WIDESCREEN = 21
    HAS_TELETEXT = 22
    IS_MULTICHANNEL = 23
    IS_CRYPTED = 24
    SUBSERVICES_AVAILABLE = 25
    AUDIOTRACKS_AVAILABLE = 26
    SUBTITLES_AVAILABLE = 27
    EDITMODE = 28
    FRAMERATE = 29
    IS_FTA = 30
    HAS_HBBTV = 31
    IS_SATELLITE = 32
    IS_CABLE = 33
    IS_TERRESTRIAL = 34
    IS_STREAMTV = 35
    IS_SATELLITE_S = 36
    IS_SATELLITE_S2 = 37
    IS_CABLE_C = 38
    IS_CABLE_C2 = 39
    IS_TERRESTRIAL_T = 40
    IS_TERRESTRIAL_T2 = 41
    volume = 42
    volumedata = 43
    resolution = 44
    videoinfo = 45
    
    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        if type == "apid":
            self.type = self.apid
        elif type == "vpid":
            self.type = self.vpid
        elif type == "sid":
            self.type = self.sid
        elif type == "onid":
            self.type = self.onid
        elif type == "tsid":
            self.type = self.tsid
        elif type == "prcpid":
            self.type = self.prcpid
        elif type == "caids":
            self.type = self.caids
        elif type == "pmtpid":
            self.type = self.pmtpid
        elif type == "txtpid":
            self.type = self.txtpid
        elif type == "tsid":
            self.type = self.tsid
        elif type == "xres":
            self.type = self.xres
        elif type == "yres":
            self.type = self.yres
        elif type == "Resolution":
            self.type = self.resolution
        elif  type == "atype":
            self.type = self.atype
        elif  type == "vtype":
            self.type = self.vtype
        elif  type == "avtype":
            self.type = self.avtype
        elif  type == "fps":
            self.type = self.fps
        elif  type == "tbps":
            self.type = self.tbps
        elif type == "vsize":
            self.type = self.vsize
        elif type == "VideoInfo":
            self.type = self.videoinfo
        elif type == "ttype":
            self.type = self.ttype
        elif  type == "VideoWidth":
            self.type = self.XRES
        elif  type == "VideoHeight":
            self.type = self.YRES
        elif  type == "IsWidescreen":
            self.type = self.IS_WIDESCREEN
        elif  type == "HasTelext":
            self.type = self.HAS_TELETEXT
        elif  type == "IsMultichannel":
            self.type = self.IS_MULTICHANNEL
        elif  type == "IsCrypted":
            self.type = self.IS_CRYPTED
        elif  type == "IsFta":
            self.type = self.IS_FTA
        elif  type == "HasHBBTV":
            self.type = self.HAS_HBBTV
        elif  type == "SubservicesAvailable":
            self.type = self.SUBSERVICES_AVAILABLE
        elif  type == "AudioTracksAvailable":
            self.type = self.AUDIOTRACKS_AVAILABLE
        elif  type == "SubtitlesAvailable":
            self.type = self.SUBTITLES_AVAILABLE
        elif  type == "Editmode":
            self.type = self.EDITMODE
        elif  type == "Framerate":
            self.type = self.FRAMERATE
        elif  type == "IsSatellite":
            self.type = self.IS_SATELLITE
        elif  type == "IsSatelliteS":
            self.type = self.IS_SATELLITE_S
        elif  type == "IsSatelliteS2":
            self.type = self.IS_SATELLITE_S2
        elif  type == "IsCable":
            self.type = self.IS_CABLE
        elif type == "IsCableC":
            self.type = self.IS_CABLE_C
        elif type == "IsCableC2":
            self.type = self.IS_CABLE_C2
        elif  type == "IsTerrestrial":
            self.type = self.IS_TERRESTRIAL
        elif type == "IsTerrestrialT":
            self.type = self.IS_TERRESTRIAL_T
        elif type == "IsTerrestrialT2":
            self.type = self.IS_TERRESTRIAL_T2
        elif  type == "IsStreamTV":
            self.type = self.IS_STREAMTV
        elif  type == "IsVolume":
            self.type = self.volume
        elif  type == "IsVolumeData":
            self.type = self.volumedata
        else: 
            self.type = self.format
            self.sfmt = type[:]
        self.poll_interval = 1000
        self.poll_enabled = True
        
    def getServiceInfoString2(self, info, what, convert = lambda x: "%d" % x):
        v = info.getInfo(what)
        if v == -3:
            t_objs = info.getInfoObject(what)
            if t_objs and (len(t_objs) > 0):
                ret_val=""
                for t_obj in t_objs:
                    ret_val += "%.4X " % t_obj
                return ret_val[:-1]
            else:
                return ""
        return convert(v)
        
    def getServiceInfoString(self, info, what, convert = lambda x: "%d" % x):
        v = info.getInfo(what)
        if v == -1:
            return "N/A"
        if v == -2:
            return info.getInfoString(what)
        return convert(v)

        
    @cached
    def getText(self):
        self.stream = { 'apid':"N/A", 'vpid':"N/A", 'sid':"N/A", 'onid':"N/A", 'tsid':"N/A", 'prcpid':"N/A", 'caids':"FTA",
                        'pmtpid':"N/A", 'txtpid':"N/A", 'xres':" ", 'yres':" ", 'resolution':" " ,'videoinfo':" ", 'atype':" ",
                        'vtype':" ", 'avtype':" ", 'fps':" ", 'tbps':" ", 'vsize':" ", 'ttype':""}
        streaminfo = ""
        array_caids = []
        service = self.source.service
        info = service and service.info()
        if not info:
            return ""
        
        if self.getServiceInfoString(info, iServiceInformation.sAudioPID) != "N/A":
            self.stream['apid'] = "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sAudioPID))
        if self.getServiceInfoString(info, iServiceInformation.sVideoPID) != "N/A":
            self.stream['vpid'] = "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sVideoPID))
        if self.getServiceInfoString(info, iServiceInformation.sSID) != "N/A":
            self.stream['sid'] = "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sSID))
        if self.getServiceInfoString(info, iServiceInformation.sONID) != "N/A":
            self.stream['onid'] = "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sONID))
        if self.getServiceInfoString(info, iServiceInformation.sTSID) != "N/A":
            self.stream['tsid'] = "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sTSID))
        if self.getServiceInfoString(info, iServiceInformation.sPCRPID) != "N/A":
            self.stream['prcpid'] = "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sPCRPID))
        if self.getServiceInfoString(info, iServiceInformation.sPMTPID) != "N/A":
            self.stream['pmtpid'] = self.getServiceInfoString(info, iServiceInformation.sPMTPID)
        if self.getServiceInfoString(info, iServiceInformation.sTXTPID) != "N/A":
            self.stream['txtpid'] = self.getServiceInfoString(info, iServiceInformation.sTXTPID)
        caidinfo = self.getServiceInfoString2(info, iServiceInformation.sCAIDs)
        for caid in caidinfo.split():
            array_caids.append(caid)
        self.stream['caids'] = ' '.join(str(x) for x in set(array_caids))
        if self.getServiceInfoString(info, iServiceInformation.sVideoHeight) != "N/A":
            self.stream['yres'] = self.getServiceInfoString(info, iServiceInformation.sVideoHeight) + ("i", "p", "")[info.getInfo(iServiceInformation.sProgressive)]
        if self.getServiceInfoString(info, iServiceInformation.sVideoWidth) != "N/A":
            self.stream['xres'] = self.getServiceInfoString(info, iServiceInformation.sVideoWidth)
        if self.getServiceInfoString(info, iServiceInformation.sVideoWidth) != "N/A" and self.getServiceInfoString(info, iServiceInformation.sVideoHeight) != "N/A":
            self.stream['resolution'] = self.getServiceInfoString(info, iServiceInformation.sVideoWidth) + "x" + self.getServiceInfoString(info, iServiceInformation.sVideoHeight)
        audio = service.audioTracks()
        if audio:
            if audio.getCurrentTrack() > -1:
                self.stream['atype'] = str(audio.getTrackInfo(audio.getCurrentTrack()).getDescription()).replace(",","")
        try:
            self.stream['vtype'] = ("MPEG2", "MPEG4", "MPEG1", "MPEG4-II", "VC1", "VC1-SM", "")[info.getInfo(iServiceInformation.sVideoType)]
            self.stream['avtype'] = ("MPEG2/", "MPEG4/", "MPEG1/", "MPEG4-II/", "VC1/", "VC1-SM/", "")[info.getInfo(iServiceInformation.sVideoType)] + self.stream['atype']
        except Exception:
            self.stream['vtype'] = ""
            self.stream['avtype'] = ""
            
        if self.getServiceInfoString(info, iServiceInformation.sFrameRate, lambda x: "%d" % ((x+500)/1000)) != "N/A":
            self.stream['fps'] = self.getServiceInfoString(info, iServiceInformation.sFrameRate, lambda x: "%d" % ((x+500)/1000))
        if self.getServiceInfoString(info, iServiceInformation.sTransferBPS, lambda x: "%d kB/s" % (x/1024)) != "N/A":
            self.stream['tbps'] = self.getServiceInfoString(info, iServiceInformation.sTransferBPS, lambda x: "%d kB/s" % (x/1024))
        self.tpdata = info.getInfoObject(iServiceInformation.sTransponderData)
        if self.tpdata:
            self.stream['ttype'] = self.tpdata.get('tuner_type', '')
            if service.streamed() is None:
                if self.stream['ttype'] == 'DVB-S' and self.tpdata.get('system', 0) == 1:
                    self.stream['ttype'] = 'DVB-S2'
                elif self.stream['ttype'] == 'DVB-C' and self.tpdata.get('system', 0) == 1:
                    self.stream['ttype'] = 'DVB-C2'
                elif self.stream['ttype'] == 'DVB-T' and self.tpdata.get('system', 0) == 1:
                    self.stream['ttype'] = 'DVB-T2'
        else:
            self.stream['ttype'] = 'IPTV'
        
        if self.type == self.apid:
            streaminfo = self.stream['apid']
        elif self.type == self.vpid:
            streaminfo = self.stream['vpid']
        elif self.type == self.sid:
            streaminfo = self.stream['sid']
        elif self.type == self.onid:
            streaminfo = self.stream['onid']
        elif self.type == self.tsid:
            streaminfo = self.stream['tsid']
        elif self.type == self.prcpid:
            streaminfo = self.stream['prcpid']
        elif self.type == self.caids:
            streaminfo = self.stream['caids']
        elif self.type == self.pmtpid:
            streaminfo = self.stream['pmtpid']
        elif self.type == self.txtpid:
            streaminfo = self.stream['txtpid']
        elif self.type == self.tsid:
            streaminfo = self.stream['tsid']
        elif self.type == self.xres:
            streaminfo = self.stream['xres']
        elif self.type == self.yres:
            streaminfo = self.stream['yres']
        elif self.type == self.resolution:
            streaminfo = self.stream['resolution']
        elif self.type == self.atype:
            streaminfo = self.stream['atype']
        elif self.type == self.vtype:
            streaminfo = self.stream['vtype']
        elif self.type == self.avtype:
            streaminfo = self.stream['avtype']
        elif self.type == self.fps:
            streaminfo = self.stream['fps']
        elif self.type == self.tbps:
            streaminfo = self.stream['tbps']
        elif self.type == self.ttype:
            streaminfo = self.stream['ttype']
        elif self.type == self.volume:
            streaminfo = _('Vol: %s') % config.audio.volume.value
        elif self.type == self.volumedata:
            streaminfo = '%s' % config.audio.volume.value
        elif self.type == self.vsize:
            streaminfo = self.stream['xres'] + 'x' + self.stream['yres'] + self.stream['fps']
        elif self.type == self.videoinfo:
            streaminfo = self.stream['vtype'] + ", " + self.stream['xres'] + 'x' + self.stream['yres'] + ", " +  self.stream['fps'] + " fps"
        elif self.type == self.format:
            tmp = self.sfmt[:]
            for param in tmp.split():
                if param != '':
                    if param[0] != '%':
                        streaminfo += param 
                    else:
                        streaminfo += ' ' + self.stream[param.strip('%')] + '  '
        return streaminfo
        
    text = property(getText)
    
    @cached
    def getValue(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return -1
        if self.type == self.XRES:
            return info.getInfo(iServiceInformation.sVideoWidth)
        if self.type == self.YRES:
            return info.getInfo(iServiceInformation.sVideoHeight)
        if self.type == self.FRAMERATE:
            return info.getInfo(iServiceInformation.sFrameRate)
        return -1

    value = property(getValue)
    
    @cached
    def getBoolean(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return False
        self.tpdata = info.getInfoObject(iServiceInformation.sTransponderData)
        if self.tpdata:
            type = self.tpdata.get('tuner_type', '')
            if service.streamed() is None: system = self.tpdata.get('system', 0)
            else: system = 'IPTV'
            if DBG: j00zekDEBUG('[j00zekModServiceInfoEX:getBoolean] tuner_type=%s, system = %s' % (type, system) ) 
        else:
            type = 'IP-TV'
        if self.type == self.HAS_TELETEXT:
            tpid = info.getInfo(iServiceInformation.sTXTPID)
            return tpid != -1
        elif self.type == self.IS_MULTICHANNEL:
            audio = service.audioTracks()
            if audio:
                n = audio.getNumberOfTracks()
                idx = 0
                while idx < n:
                    i = audio.getTrackInfo(idx)
                    description = i.getDescription();
                    if "AC3" in description or "AC-3" in description or "DTS" in description:
                        return True
                    idx += 1
            return False
        elif self.type == self.IS_CRYPTED:
            return info.getInfo(iServiceInformation.sIsCrypted) == 1
        elif self.type == self.IS_FTA:
            return info.getInfo(iServiceInformation.sIsCrypted) == 0
        elif self.type == self.IS_WIDESCREEN:
            return info.getInfo(iServiceInformation.sAspect) in WIDESCREEN
        elif self.type == self.SUBSERVICES_AVAILABLE:
            subservices = service.subServices()
            return subservices and subservices.getNumberOfSubservices() > 0
        elif self.type == self.HAS_HBBTV:
            try:
                return info.getInfoString(iServiceInformation.sHBBTVUrl) != ""
            except Exception:
                return False
        elif self.type == self.AUDIOTRACKS_AVAILABLE:
            audio = service.audioTracks()
            return audio and audio.getNumberOfTracks() > 1
        elif self.type == self.SUBTITLES_AVAILABLE:
            subtitle = service and service.subtitle()
            subtitlelist = subtitle and subtitle.getSubtitleList()
            if subtitlelist:
                return len(subtitlelist) > 0
        elif self.type == self.EDITMODE:
            return hasattr(self.source, "editmode") and not not self.source.editmode
        elif self.type == self.IS_SATELLITE:
            if type == 'DVB-S':
                return True
        elif self.type == self.IS_CABLE:
            if type == 'DVB-C':
                return True
        elif self.type == self.IS_TERRESTRIAL:
            if type == 'DVB-T':
                return True
        elif self.type == self.IS_STREAMTV:
            if service.streamed() is not None:
                return True
        elif self.type == self.IS_SATELLITE_S:
            if type == 'DVB-S' and service.streamed() is None:
                if self.tpdata.get('system', 0) is 0:
                    return True
        elif self.type == self.IS_SATELLITE_S2:
            if type == 'DVB-S' and service.streamed() is None:
                if self.tpdata.get('system', 0) is 1:
                    return True
        elif self.type == self.IS_CABLE_C:
            if type == 'DVB-C' and service.streamed() is None:
                if self.tpdata.get('system', 0) is 0:
                    return True
        elif self.type == self.IS_CABLE_C2:
            if type == 'DVB-C' and service.streamed() is None:
                if self.tpdata.get('system', 0) is 1:
                    return True
        elif self.type == self.IS_TERRESTRIAL_T:
            if type == 'DVB-T' and service.streamed() is None:
                if self.tpdata.get('system', 0) is 0:
                    return True
        elif self.type == self.IS_TERRESTRIAL_T2:
            if type == 'DVB-T' and service.streamed() is None:
                if self.tpdata.get('system', 0) is 1:
                    return True
        return False
    
    boolean = property(getBoolean)

    def changed(self, what):
        if what[0] == self.CHANGED_SPECIFIC:
            if what[1] == iPlayableService.evVideoSizeChanged or what[1] == iPlayableService.evUpdatedInfo:
                Converter.changed(self, what)
        elif what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
            Converter.changed(self, what)
        elif what[0] == self.CHANGED_POLL:
            self.downstream_elements.changed(what)

