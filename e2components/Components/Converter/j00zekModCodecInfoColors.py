# -*- coding: UTF-8 -*-
#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached
import os
from Tools.ISO639 import LanguageCodes
# stream type to codec map
codec_data = {
    -1: "N/A",
    0: "MPEG2",
    1: "AVC",
    2: "H263",
    3: "VC1",
    4: "MPEG4-VC",
    5: "VC1-SM",
    6: "MPEG1",
    7: "HEVC",
    8: "VP8",
    9: "VP9",
    10: "XVID",
    11: "N/A 11",
    12: "N/A 12",
    13: "DIVX 3.11",
    14: "DIVX 4",
    15: "DIVX 5",
    16: "AVS",
    17: "N/A 17",
    18: "VP6",
    19: "N/A 19",
    20: "N/A 20",
    21: "SPARK",
}

def addspace(text):
    if text:
        text += " "
    return text

class j00zekModCodecInfoColors(Poll, Converter, object):

    xAPID = 0
    xVPID = 1
    xSID = 2
    xONID = 3
    xTSID = 4
    sCAIDs = 5
    yAll = 6
    xAll = 7
    xVTYPE = 8
    Provider = 9
    Ecmpid = 10
    Caid = 11
    Provid = 12
    Resolution = 13
    AudioCodec = 14
    VideoCodec = 15           
    
    
    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.type, self.interesting_events = {
                "xAPID": (self.xAPID, (iPlayableService.evUpdatedInfo,)),
                "xVPID": (self.xVPID, (iPlayableService.evUpdatedInfo,)),
                "xSID": (self.xSID, (iPlayableService.evUpdatedInfo,)),
                "xONID": (self.xONID, (iPlayableService.evUpdatedInfo,)),
                "xTSID": (self.xTSID, (iPlayableService.evUpdatedInfo,)),
                "sCAIDs": (self.sCAIDs, (iPlayableService.evUpdatedInfo,)),
                "yAll": (self.yAll, (iPlayableService.evUpdatedInfo,)),
                "xAll": (self.xAll, (iPlayableService.evUpdatedInfo,)),
                "xVTYPE": (self.xVTYPE, (iPlayableService.evUpdatedInfo,)),
                "Resolution": (self.Resolution, (iPlayableService.evUpdatedInfo,)),
                "Provider": (self.Provider, (iPlayableService.evUpdatedInfo,)),
                "Ecmpid": (self.Ecmpid, (iPlayableService.evUpdatedInfo,)),
                "Provid": (self.Provid, (iPlayableService.evUpdatedInfo,)),                                
                "Caid": (self.Caid, (iPlayableService.evUpdatedInfo,)),
                "AudioCodec": (self.AudioCodec, (iPlayableService.evUpdatedInfo,)),
                "VideoCodec": (self.VideoCodec, (iPlayableService.evUpdatedInfo,)),
             }[type]
        self.poll_interval = 1000
        self.poll_enabled = True
        self.txt_naim = {'0500:HTB+': '040600', '0500:HTB+ LIGHT': '040610', '0500:HTB+ ВОСТОК': '023D00', '4AE0:TRICOLORTV': '000000', '2710:TRICOLORTV': '000019'}


    def createVideoCodec(self, info):
        return codec_data.get(info.getInfo(iServiceInformation.sVideoType), "N/A")
        
    def getServiceInfoString(self, info, what, convert = lambda x: "%d" % x):
        v = info.getInfo(what)
        if v == -1:
            return "N/A"
        if v == -2:
            return info.getInfoString(what)
        # v == -3 now use only for caids
        # i don't know how it work with another parametrs
        # now i made for returning values as hex string separated by space
        # may be better use convert for formating output but it TBA 
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

    @cached
    def getText(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return ""
        if self.type == self.xAPID:
            try:
                return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sAudioPID))
            except Exception:
                return "N/A"
        elif self.type == self.xVTYPE:
            return ("MPEG2", "MPEG4", "MPEG1", "MPEG4-II", "VC1", "VC1-SM", "HEVC", "")[info.getInfo(iServiceInformation.sVideoType)]
        elif self.type == self.xVPID:
            try:
                return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sVideoPID))
            except Exception:
                return "N/A"
        elif self.type == self.xSID:
            try:
                return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sSID))
            except Exception:
                return "N/A"
        elif self.type == self.xTSID:
            try:
                return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sTSID))
            except Exception:
                return "N/A"
        elif self.type == self.xONID:
            try:
                return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sONID))
            except Exception:
                return "N/A"
        elif self.type == self.sCAIDs:
            try:
                return self.getServiceInfoString(info, iServiceInformation.sCAIDs)
            except Exception:
                return "N/A"
        elif self.type == self.Ecmpid:                       
            name = ""
            if (info.getInfo(iServiceInformation.sIsCrypted) == 1):
                name = self.getEcmpid()
                if name == "":
                    caidpids = info.getInfoObject(iServiceInformation.sCAIDPIDs)
                    if len(caidpids) != 0:
                        for x in range(0, len(caidpids)):
                            name = '%0.4X' % int(caidpids[0][1])
            return name
        elif self.type == self.Caid:
            name = ""
            if (info.getInfo(iServiceInformation.sIsCrypted) == 1):
                name = self.getCaid()
                if name == "":
                    caidpids = info.getInfoObject(iServiceInformation.sCAIDPIDs)
                    if len(caidpids) != 0:
                        for x in range(0, len(caidpids)):
                            name = '%0.4X' % int(caidpids[0][0])
            return name
        elif self.type == self.Provid:
            text = ""
            name = ""
            caid = ""
            if (info.getInfo(iServiceInformation.sIsCrypted) == 1):
                text = self.getProvid()
                if text == "":
                    caidpids = info.getInfoObject(iServiceInformation.sCAIDPIDs)
                    if len(caidpids) != 0:
                        for x in range(0, len(caidpids)):
                            caid = '%0.4X' % int(caidpids[0][0])
                    prov = self.getServiceInfoString(info, iServiceInformation.sProvider).upper()
                    name = '%s:%s' % (caid, prov)
                    text = self.txt_naim.get(name, "000000")
            return text
        elif self.type == self.yAll:
            try:
                return "SID: %0.4X  VPID: %0.4X  APID: %0.4X  TSID: %0.4X  ONID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sVideoPID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)), int(self.getServiceInfoString(info, iServiceInformation.sTSID)), int(self.getServiceInfoString(info, iServiceInformation.sONID)))
            except Exception:
                try:
                    return "SID: %0.4X  APID: %0.4X  TSID: %0.4X  ONID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)), int(self.getServiceInfoString(info, iServiceInformation.sTSID)), int(self.getServiceInfoString(info, iServiceInformation.sONID)))
                except Exception:
                    return " "
        elif self.type == self.xAll:
            try:
                return "SID: %0.4X  VPID: %0.4X APID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sVideoPID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)))
            except Exception:
                try:
                    return "SID: %0.4X  APID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)))
                except Exception:
                    return " "
        elif self.type == self.Resolution:
            xres = info.getInfo(iServiceInformation.sVideoWidth)
            if xres == -1:
                return " "
            yres = info.getInfo(iServiceInformation.sVideoHeight)
            mode = ( 'i', 'p', ' ')[info.getInfo(iServiceInformation.sProgressive)]
            fps = str((info.getInfo(iServiceInformation.sFrameRate) + 500) / 1000)
            return '\c00289496' + str(xres) + '\c00??;?00x\c00289496' + str(yres) + '\c00??;?00' + mode + '\c00!!;!00' + fps
            #c00?25=41 - dark red
            #c00389416 - dark green
            #c00289496 - blue
            #c00!!;!00 - light green
            #c00??;?00 - light yellow
            #c00ww;w00 - lemon
            #c00?25=01 - orange
        elif self.type == self.AudioCodec:
                        return self.createAudioCodec()
        elif self.type == self.VideoCodec:
                        return self.createVideoCodec(info)
        elif self.type == self.Provider:
            return self.getServiceInfoString(info, iServiceInformation.sProvider).upper()
        return ""

    text = property(getText)

    def createAudioCodec(self):
        service = self.source.service
        audio = service.audioTracks()
        ecm = None
        info = {}
        if audio:
            try:
                ct = audio.getCurrentTrack()
                i = audio.getTrackInfo(ct)
                languages = i.getLanguage()
                if "pol" in languages or "polish" in languages or "pl" in languages:
                    languages = _("Polish")
                if "eng" in languages or "Englisch" in languages or "en" in languages:
                    languages = _("English")
                if "de" in languages or "Deutsch" in languages or "deu" in languages or "ger" in languages:
                    languages = _("German")
                if "fra" in languages or "french" in languages or "fre" in languages or "fr" in languages:
                    languages = _("French")
                elif "spa" in languages:
                    languages = _("Spanish")
                elif "swe" in languages:
                    languages = _("Swedish")
                elif "ita" in languages:
                    languages = _("Italian")
                elif "ukr" in languages:
                    languages = _("Ukrainian")
                elif "rus" in languages:
                    languages = _("Russian")
                elif "org" in languages:
                    languages = _("Original")
                elif "mis" in languages:
                    languages = _("Miscellaneous languages")
                elif "qaa" in languages:
                    languages = _("Reserved")
                elif "und" in languages:
                    languages = _("Undetermined")
                description = i.getDescription();
                return '\c00??;?00' + description + " " + languages
            except Exception:
                return _("unknown")
        
        def getEcmpid(self):
            textvalue = ''
            service = self.source.service
            if service:
                info = service and service.info()
                if info:
                    if info.getInfoObject(iServiceInformation.sCAIDs):
                        ecm_info = self.ecmfile()
                        if ecm_info:
                            pid = ecm_info.get('pid', '')
                            pid = pid.lstrip('0x')
                            pid = pid.upper()
                            pid = pid.zfill(4)
                            textvalue = '%s' % pid
            return textvalue

        def getCaid(self):
            textvalue = ''
            service = self.source.service
            if service:
                info = service and service.info()
                if info:
                    if info.getInfoObject(iServiceInformation.sCAIDs):
                        ecm_info = self.ecmfile()
                        if ecm_info:
                            caid = ecm_info.get('caid', '')
                            caid = caid.lstrip('0x')
                            caid = caid.upper()
                            caid = caid.zfill(4)
                            textvalue = '%s' % caid
            return textvalue

        def getProvid(self):
            textvalue = ''
            service = self.source.service
            if service:
                info = service and service.info()
                if info:
                    if info.getInfoObject(iServiceInformation.sCAIDs):
                        ecm_info = self.ecmfile()
                        if ecm_info:
                            provider = ecm_info.get('prov', '')
                            provider = provider.lstrip('0x')
                            provider = provider.upper()
                            provider = provider.zfill(6)
                            textvalue = '%s' % provider
            return textvalue

        def ecmfile(self):
            ecm = None
            info = {}
            service = self.source.service
            if service:
                frontendInfo = service.frontendInfo()
                if frontendInfo:
                    try:
                       ecmpath = '/tmp/ecm%s.info' % frontendInfo.getAll(False).get('tuner_number')
                       ecmf = open(ecmpath, 'rb')
                       ecm = ecmf.readlines()
                    except Exception:
                        try:
                            ecmf = open('/tmp/ecm.info', 'rb')
                            ecm = ecmf.readlines()
                        except Exception:
                            pass

        if ecm:
            for line in ecm:
                x = line.lower().find("msec")
                #ecm time for mgcamd and oscam
                if x != -1:
                    info["ecm time"] = line[0:x+4]
                else:
                    item = line.split(":", 1)
                    if len(item) > 1:
                      #wicard block
                      if item[0] == "Provider":
                          item[0] = "prov"
                          item[1] = item[1].strip()[2:]
                      elif item[0] == "ECM PID":
                          item[0] = "pid"
                      elif item[0] == "response time":
                          info["source"] = "net"
                          it_tmp = item[1].strip().split(" ")
                          info["ecm time"] = "%s msec" % it_tmp[0]
                          info["reader"] = it_tmp[-1].strip('R0[').strip(']')
                          y = it_tmp[-1].find('[')
                          if y !=-1:
                              info["server"] = it_tmp[-1][:y]
                              info["protocol"] = it_tmp[-1][y+1:-1]
                          y = it_tmp[-1].find('(')
                          if y !=-1:
                              info["server"] = it_tmp[-1].split("(")[-1].split(":")[0]
                              info["port"] = it_tmp[-1].split("(")[-1].split(":")[-1].rstrip(")")
                              info["reader"] = it_tmp[-2]
                          elif y == -1:
                              item[0] = "source"
                              item[1] = "sci"
                          if it_tmp[-1].find('emu') >-1 or it_tmp[-1].find('cache') > -1 or it_tmp[-1].find('card') > -1 or it_tmp[-1].find('biss') > -1:
                              item[0] = "source"
                              item[1] = "emu"
                      elif item[0] == "hops":
                          item[1] = item[1].strip("\n")
                      elif item[0] == "system":
                          item[1] = item[1].strip("\n")
                      elif item[0] == "provider":
                          item[1] = item[1].strip("\n")
                      elif item[0][:2] == 'cw'or item[0] =='ChID' or item[0] == "Service": 
                          pass
                          #mgcamd new_oscam block
                      elif item[0] == "source":
                          if item[1].strip()[:3] == "net":
                              it_tmp = item[1].strip().split(" ")
                              info["protocol"] = it_tmp[1][1:]
                              info["server"] = it_tmp[-1].split(":",1)[0]
                              info["port"] = it_tmp[-1].split(':',1)[1][:-1]
                              item[1] = "net"
                      elif item[0] == "prov":
                          y = item[1].find(",")
                          if y != -1:
                              item[1] = item[1][:y]
                          #old oscam block
                      elif item[0] == "reader":
                          if item[1].strip() == "emu":
                              item[0] = "source"
                      elif item[0] == "from":
                          if item[1].strip() == "local":
                              item[1] = "sci"
                              item[0] = "source"
                          else:
                              info["source"] = "net"
                              item[0] = "server"
                          #cccam block
                      elif item[0] == "provid":
                          item[0] = "prov"
                      elif item[0] == "using":
                          if item[1].strip() == "emu" or item[1].strip() == "sci":
                              item[0] = "source"
                          else:
                              info["source"] = "net"
                              item[0] = "protocol"
                      elif item[0] == "address":
                          tt = item[1].find(":")
                          if tt != -1:
                              info["server"] = item[1][:tt].strip()
                              item[0] = "port"
                              item[1] = item[1][tt+1:]
                          info[item[0].strip().lower()] = item[1].strip()
                      else:
                          if not "caid" in info:
                              x = line.lower().find("caid")
                              if x != -1:
                                  y = line.find(",")
                                  if y != -1:
                                      info["caid"] = line[x+5:y]
                          if not "pid" in info:
                              x = line.lower().find("pid")
                              if x != -1:
                                  y = line.find(" =")
                                  z = line.find(" *")
                                  if y != -1:
                                      info["pid"] = line[x+4:y]
                                  elif z != -1:
                                      info["pid"] = line[x+4:z]
            ecmf.close()
        return info       

    def changed(self, what):
        if what[0] == self.CHANGED_SPECIFIC:
            if what[1] == iPlayableService.evStart or what[1] == iPlayableService.evVideoSizeChanged or what[1] == iPlayableService.evUpdatedInfo:
                Converter.changed(self, what)
        elif what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
            Converter.changed(self, what)
        elif what[0] == self.CHANGED_POLL:
            self.downstream_elements.changed(what)
