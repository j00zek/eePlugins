# -*- coding: utf-8 -*-
#
#  Bitrate converter
#
#  Coded by COoLoSER 2013
#
#  Part getting AudioCodec is from AslanExtraInfo
#  which was shamelessly copied from pliExpertInfo and edit by (aslan2006)
#
#  Generally I learn enigma2 on others converters and plugins. Thanks to whole community
#  I don't take credits for solutions found in this plugin, it's just composition of
#  codes found on web and sources on tuner
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, eTimer, eServiceReference, eEPGCache
from Components.Element import cached
from Tools.Directories import fileExists

import re

class j00zekModExtraInfo(Converter, object):
    PROV_CA_ID = 1
    NETCARD_INFO = 2
    CRYPT_INFO = 3
    TEMPERATURE = 4
    PROV_ID = 5
    CAID_ID = 6
    PROV_CA_SOURCE = 7
    AUDIO_CODEC = 8
    SID = 9
    TRANSPONDER = 11
    SOURCE = 12

    #constructor
    def __init__(self, type):
        Converter.__init__(self, type)
        self.type = {
            "ProvCaid": self.PROV_CA_ID,
            "ExtraEcm": self.NETCARD_INFO,
            "CryptInfo": self.CRYPT_INFO,
            "Temperature": self.TEMPERATURE,
            "ProvID": self.PROV_ID,
            "CaidID": self.CAID_ID,
            "sid": self.SID,
            "ProvID_CaidID_Source": self.PROV_CA_SOURCE,
            "AudioCodec": self.AUDIO_CODEC,
            "TransponderType": self.TRANSPONDER,
            "Source": self.SOURCE
        }[type]
        self.pat_caid = re.compile('CaID (.*),')
        self.DynamicTimer = eTimer()
        self.DynamicTimer.callback.append(self.doSwitch)

######################
#utils functions
######################
    #converts hex number to decimal numer. Hex is given as string
    def hex_str2dec(self, str):
        ret = 0
        try:
            ret = int(re.sub("0x","",str),16)
        except:
            pass
        return ret

    #normalize hex value, converts it to string and converts it as 4 digit string
    def norm_hex(self, str):
        return "%04x" % self.hex_str2dec(str)

######################
#getter functions
######################
    def getExpertInfo(self, theId):
        expertString = ("  ")
        fileString = ""
        try:
            fp = open("/tmp/share.info", "r")
            while 1:
                currentLine = fp.readline()
                if (currentLine == ""):
                    break
                foundIdIndex = currentLine.find(("id:" + theId))
                if (foundIdIndex is not -1):
                    fileString = currentLine
                    break

                atIndex = fileString.find(" at ")
                cardIndex = fileString.find(" Card ")
                if ((atIndex is not -1) and (cardIndex is not -1)):
                    addy = fileString[(atIndex + 4):cardIndex]
                    addyLen = len(addy)
                    if (addyLen > 15):
                        addy = ((addy[:9] + "*") + addy[(addyLen - 5):])
                        expertString = (expertString + addy)
                expertString = ((expertString + "  BoxId:") + theId)
                distIndex = fileString.find("dist:")
                if (distIndex is not -1):
                    expertString = (((expertString + " ") + "D:") + fileString[(distIndex + 5)])
                levelIndex = fileString.find("Lev:")
                if (levelIndex is not -1):
                    expertString = (((expertString + " ") + "L:") + fileString[(levelIndex + 4)])
        except:
            print("Infobar")
        return expertString

    def isGParameter(self, boxId, caId):
        isInGParameter = ""
        try:
            caId = caId[2:]
            fp = open("/usr/keys/cwshare.cfg", "r")
            while 1:
                currentLine = fp.readline()
                if (currentLine == ""):
                    break
                line = currentLine.strip()
                if (line[:2] == "G:"):
                    rightCurlyIndex = line.find("}")
                    line = line[:rightCurlyIndex]
                    line = line[2:]
                    line = line.strip(" {}\n")
                    (c, b,) = line.split(" ")
                    c = c[:4]
                    if ((c == caId) and (b == boxId)):
                        isInGParameter = (isInGParameter + "(G)")
            fp.close()
            return isInGParameter
        except:
            return isInGParameter

    def getCryptSystemName(self, caID):
        caID=int(caID, 16)
        if ((caID>=0x0100) and (caID<=0x01FF)):
            syID="Seca Mediaguard"
        elif((caID>=0x0500) and (caID<=0x05FF)):
            syID="Viaccess"
        elif((caID>=0x0600) and (caID<=0x06FF)):
            syID="Irdeto"
        elif((caID>=0x0900) and (caID<=0x09FF)):
            syID="NDS Videoguard"
        elif((caID>=0x0B00) and (caID<=0x0BFF)):
            syID="Conax"
        elif((caID>=0x0D00) and (caID<=0x0DFF)):
            syID="Cryptoworks"
        elif((caID>=0x0E00) and (caID<=0x0EFF)):
            syID="PowerVu"
        elif((caID>=0x1700) and (caID<=0x17FF)):
            syID="Betacrypt"
        elif((caID>=0x1800) and (caID<=0x18FF)):
            syID="Nagravision"
        elif((caID>=0x2200) and (caID<=0x22FF)):
            syID="Codicrypt"
        elif((caID>=0x2600) and (caID<=0x26FF)):
            syID="EBU Biss"
        elif((caID>=0x4A00) and (caID<=0x4AFF)):
            syID="DreamCrypt"
        elif((caID>=0x5500) and (caID<=0x55FF)):
            syID="Griffin"
        elif((caID>=0xA100) and (caID<=0xA1FF)):
            syID="RusCrypt"
        else:
            syID="Other"
        return syID

    def createAudioCodec(self):
        service = self.source.service
        audio = service.audioTracks()
        if audio:
            try:
                ct = audio.getCurrentTrack()
                i = audio.getTrackInfo(ct)
                languages = i.getLanguage()
                if "pol" in languages or "Polish" in languages or "pl" in languages:
                    languages = "Polski"
                elif "org" in languages:
                    languages = "Oryginalny"
                description = i.getDescription();
                return description + " " + languages
            except:
                return "nieznany"

    def getTemperature(self):
        temp = ''
        unit = ''
        try:
            f = open('/proc/stb/sensors/temp0/value', 'rb')
            temp = f.readline().strip()
            f.close()
            f = open('/proc/stb/sensors/temp0/unit', 'rb')
            unit = f.readline().strip()
            f.close()
            tempinfo = str(temp) + ' \xc2\xb0' + str(unit)
            return tempinfo
        except:
            pass

    def getCryptInfo(self):
        isCrypted = info.getInfo(iServiceInformation.sIsCrypted)
        #f.write("Is crypted="+str(isCrypted)+"\n")
        if isCrypted == 1:
            id_ecm = "" 
            caID = ""
            syID = ""
            try:
                file = open ( "/tmp/ecm.info", "r" )
            except:
                #f.write("returns (0)="+"NULL"+"\n")
                return ""
            while True:
                #Spliting with : character
                line = file.readline().strip()
                if line == "":
                    break
                x = line.split(':',1)
                if x[0] == "caid":
                    #Works for CCcam
                    caID = x[1].strip()
                    sysID = self.getCryptSystemName(caID)
                    #f.write("returns (1)="+sysID+"\n")
                    return sysID
                else:
                    #check for mgcamd
                    cellmembers = line.split()
                    for x in range(len(cellmembers)):
                        if ("ECM" in cellmembers[x]):
                            if x<=(len(cellmembers)):
                                caID = cellmembers[x+3] # detekcja 0100,1801
                                caID = caID.strip(",;.:-*_<>()[]{}")
                                sysID = self.getCryptSystemName(caID)
                                #f.write("returns (2)="+sysID+"\n")
                                return sysID
        else:
            #f.write("returns (3)="+"FTA"+"\n")
            #return "FTA"
            return ""


    def getStreamInfo(self, ltype):
#        print "============> getText PROV_CA_ID"
        try:
            file = open ( "/tmp/ecm.info", "r" )
        except:
            return ""
        ee = 0
        caid = "0000"
        provid = "0000"
        while True:
            line = file.readline().strip()
            if line == "":
                break
            x = line.split(':',1)
            mo = self.pat_caid.search(line)
            if mo:
                caid = mo.group(1)
            if x[0] == "prov":
                y = x[1].strip().split(',')
                provid = y[0]
            if x[0] == "provid":
                provid = x[1].strip()
            if x[0] == "caid":
                caid = x[1].strip()
        file.close()

        if self.hex_str2dec(caid) == 0:
            return " "
        else:
            if (ltype == self.PROV_CA_ID):
                return ( " " + self.norm_hex(caid) + " " + self.norm_hex(provid))
            elif (ltype == self.PROV_ID):
                return self.norm_hex(provid)
            elif (ltype == self.CAID_ID):
                return self.norm_hex(caid)
        return ""
    
    def getSourceInfo(self, ltype):
#        print "============> getText NETCARD_INFO"
        try:
            file = open ( "/tmp/ecm.info", "r" )
        except:
            return ""
        boxidString = ""
        caIdString = ""
        using = ""
        address = ""
        network = ""
        ecmtime = ""
        hops = ""
        reader = ""
        ee = 0
        while True:
            #Spliting with : character
            line = file.readline().strip()
            if line == "":
                break
            x = line.split(':',1)
            if x[0] == "source":
                address = x[1].strip()
                ee = 2 # mgcamd
            if x[0] == "using":
                using = x[1].strip()
                if using == "CCcam-s2s":
                    using = "CCcam"
                ee = 1 # CCcam
            if x[0] == "ecm time":
                ecmtime = x[1].strip()
                ecmtime = ((" TIME: ") + ecmtime)
                ee = 1 # CCcam
            if x[0] == "hops":
                hops = x[1].strip()
                hops = ((" HOPS: ") + hops)
                ee = 1 # CCcam
            if x[0] == "decode":
                address = x[1].strip()
                boxidIndex = line.find("prov")
                caidIndex = line.find("CaID")
                caIdString = line[(caidIndex + 7):(caidIndex + 11)]
                if (boxidIndex is not -1):
                    boxidString = currentLine[(boxidIndex + 6):(boxidIndex + 10)]
                ee = 3 # Gbox and evocamd
            if x[0] == "address":
                address = x[1].strip()
            if x[0] == "from":
                address = x[1].strip()
            if x[0] == "network":
                network = x[1].strip()
            #if x[0] == "reader":
                #reader = " Reader: "+x[1].strip()

            #spliting for mgcamd only
            if ecmtime == "":
                x = line.split("--", 1)
                msecIndex = x[0].find("msec")
                if (msecIndex is not -1):
                    ecmtime = x[0].strip()
                    ecmtime = " TIME: "+ ecmtime
        file.close()

        if(ee == 1):
            emuExpertString = ((((((" ") + using)  + " " + address)  + " " + network) + reader + " " + hops + "  ") + ecmtime + " s ")
        else: 
            emuExpertString = (((((((" ") + using) + " " + address)  + " " + network) + reader + " " + ecmtime + " ") + (self.getExpertInfo(boxidString)) + " ") + self.isGParameter(boxidString, caIdString))
        return emuExpertString

    def getTransponderType(self, info):
        transponder = info.getInfoObject(iServiceInformation.sTransponderData)
        tunerType=""
        if isinstance(transponder, dict):
            tunerType = transponder['tuner_type']
            if tunerType == "DVB-S" and transponder['system']==1:
                tunerType = "DVB-S2"
        return tunerType

    @cached
    def getText(self):
        self.DynamicTimer.start(500)
        service = self.source.service
        info = service and service.info()
        
        if not info:
            return ""
        
        nazwaemu = "CI"
        if (self.type == self.PROV_CA_ID or self.type == self.PROV_ID or self.type == self.CAID_ID) and (info.getInfo(iServiceInformation.sIsCrypted)==1):
            return self.getStreamInfo(self.type)
            
        elif (self.type == self.NETCARD_INFO) and (info.getInfo(iServiceInformation.sIsCrypted)==1):
            return self.getSourceInfo(self.type)
            
        elif (self.type == self.PROV_CA_SOURCE) and (info.getInfo(iServiceInformation.sIsCrypted)==1):
            first = self.getStreamInfo(self.PROV_CA_ID)
            second = self.getSourceInfo(self.NETCARD_INFO)
            if ( len(second.strip())>0 ):
                first = first+"  From:"+second
            return first
        elif (self.type == self.SOURCE) and (info.getInfo(iServiceInformation.sIsCrypted)==1):
            return self.getSourceInfo(self.NETCARD_INFO)
            
        elif (self.type == self.CRYPT_INFO):
            return self.getCryptInfo()
        elif (self.type == self.TEMPERATURE):
            return self.getTemperature()
        elif (self.type == self.AUDIO_CODEC):
            return self.createAudioCodec()
        elif (self.type == self.TRANSPONDER):
            return self.getTransponderType(info)
        elif (self.type == self.SID):
            sidValue = info.getInfo(iServiceInformation.sSID)
            if not sidValue:
                return ""
            return "%0.4X" % int(sidValue)

        return ""

    text = property(getText)

    def changed(self, what):
        self.what = what
        Converter.changed(self, what)

    def doSwitch(self):
        self.DynamicTimer.stop()
        Converter.changed(self, self.what)

