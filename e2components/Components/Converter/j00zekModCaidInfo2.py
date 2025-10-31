                       
 
#  CaidInfo2 - Converter
#  ver 1.2.7 2025-05-19
#
#  Coded by bigroma & 2boom & j00zek & madhouse
#

                                                                                                                   
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached
from Components.SystemInfo import SystemInfo
from Components.j00zekSkinTranslatedLabels import translate as _
from enigma import iServiceInformation, iPlayableService, eDVBCI_UI, eDVBCIInterfaces
from Tools.Directories import fileExists
import os

DBG = False
if DBG: 
        
    try: from Components.j00zekComponents import j00zekDEBUG
    except Exception: j00zekDEBUG = print
                   

info = {}
old_ecm_mtime = None


class j00zekModCaidInfo2(Poll, Converter, object):
    CAID = 0
    PID = 1
    PROV = 2
    ALL = 3
    IS_NET = 4
    IS_EMU = 5
    CRYPT = 6
    BETA = 7
    CONAX = 8
    CRW = 9
    DRE = 10
    IRD = 11
    NAGRA = 12
    NDS = 13
    SECA = 14
    VIA = 15
    PWR = 16
    VERI = 17
    BETA_C = 18
    CONAX_C = 19
    CRW_C = 20
    DRE_C = 21
    IRD_C = 22
    NAGRA_C = 23
    NDS_C = 24
    SECA_C = 25
    VIA_C = 26
    PWR_C = 27
    VERI_C = 28
    BISS = 29
    BISS_C = 30
    EXS = 31
    EXS_C = 32
    TAN = 33
    TAN_C = 34
    HOST = 35
    DELAY = 36
    FORMAT = 37
    CRYPT2 = 38
    CRD = 39
    CRDTXT = 40
    SHORT = 41
    IS_FTA = 42
    IS_CRYPTED = 43
    my_interval = 2000
    USE_CFG = 44
    
    SOFTCAMNAME = 45
    SOFTCAMFULLNAME = 46
    CAIDS = 47
    ECMFILECONTENT = 48

    def __init__(self, type):
        Poll.__init__(self)
        Converter.__init__(self, type)
        self.currPID = 1000
        self.eDVBCIUIInstance = eDVBCI_UI.getInstance()
        self.eDVBCIUIInstance and self.eDVBCIUIInstance.ciStateChanged.get().append(self.ciModuleStateChanged)
        self.NUM_CI = eDVBCIInterfaces.getInstance() and eDVBCIInterfaces.getInstance().getNumOfSlots()
               
        if DBG: j00zekDEBUG('[j00zekModCaidInfo2:__init__] self.NUM_CI = %s' % str(self.NUM_CI))
                          
        if type == "CAID": self.type = self.CAID
                           
        elif type == "PID": self.type = self.PID
        elif type == "ProvID": self.type = self.PROV
                                 
                             
        elif type == "Delay": self.type = self.DELAY
                            
        elif type == "Host": self.type = self.HOST
                           
        elif type == "Net": self.type = self.IS_NET
                           
        elif type == "Emu": self.type = self.IS_EMU
        elif type == "CryptInfo": self.type = self.CRYPT
                                  
        elif type == "CryptInfo2": self.type = self.CRYPT2
                                   
        elif type == "BetaCrypt": self.type = self.BETA
                                 
        elif type == "ConaxCrypt": self.type = self.CONAX
                                  
        elif type == "CrwCrypt": self.type = self.CRW
                                
        elif type == "DreamCrypt": self.type = self.DRE
                                
        elif type == "ExsCrypt": self.type = self.EXS
                                
        elif type == "IrdCrypt": self.type = self.IRD
                                
        elif type == "NagraCrypt": self.type = self.NAGRA
                                  
        elif type == "NdsCrypt": self.type = self.NDS
                                
        elif type == "SecaCrypt": self.type = self.SECA
                                 
        elif type == "ViaCrypt": self.type = self.VIA
                                
        elif type == "PwuCrypt": self.type = self.PWR
                                
        elif type == "VrmCrypt": self.type = self.VERI
                                 
                               
        elif type == "BetaEcm": self.type = self.BETA_C
                                
        elif type == "ConaxEcm": self.type = self.CONAX_C
                              
        elif type == "CrwEcm": self.type = self.CRW_C
        elif type == "DreamEcm": self.type = self.DRE_C
                                  
                              
        elif type == "ExsEcm": self.type = self.EXS_C
                              
        elif type == "IrdEcm": self.type = self.IRD_C
                                
        elif type == "NagraEcm": self.type = self.NAGRA_C
                              
        elif type == "NdsEcm": self.type = self.NDS_C
                               
        elif type == "SecaEcm": self.type = self.SECA_C
                              
        elif type == "ViaEcm": self.type = self.VIA_C
                              
        elif type == "PwuEcm": self.type = self.PWR_C
                              
        elif type == "VrmEcm": self.type = self.VERI_C
        elif type == "TanCrypt": self.type = self.TAN
                                
                              
        elif type == "TanEcm": self.type = self.TAN_C
        elif type == "BisCrypt": self.type = self.BISS
                                 
                              
        elif type == "BisEcm": self.type = self.BISS_C
                           
        elif type == "Crd": self.type = self.CRD
                              
        elif type == "CrdTxt": self.type = self.CRDTXT
                             
        elif type == "IsFta": self.type = self.IS_FTA
                                 
        elif type == "IsCrypted": self.type = self.IS_CRYPTED
                             
        elif type == "Short": self.type = self.SHORT
        elif type == "Default" or type == "" or type == None or type == "%": self.type = self.ALL
                                
                               
        elif type == "emuname": self.type = self.SOFTCAMNAME
                                   
        elif type == "emuFullName": self.type = self.SOFTCAMFULLNAME
                             
        elif type == "caids": self.type = self.CAIDS
                              
        elif type == "UseCFG": self.type = self.USE_CFG
                               
        elif type == "ecmfile": self.type = self.ECMFILECONTENT
        
        else:
            self.type = self.FORMAT
            self.sfmt = type[:]

        self.systemTxtCaids = {
            "26": "BiSS",
            "01": "Seca Mediaguard",
            "06": "Irdeto",
            "17": "BetaCrypt",
            "55": "BulCrypt",
            "05": "Viaccess",
            "18": "Nagravision",
            "09": "NDS-Videoguard",
            "0B": "Conax",
            "0D": "Cryptoworks",
            "4A": "DRE-Crypt",
            "27": "ExSet",
            "0E": "PowerVu",
            "10": "Tandberg",
            "22": "Codicrypt",
            "07": "DigiCipher",
            "56": "Verimatrix",
            "4B": "DG-Crypt",
            "A1": "Rosscrypt"}

        self.systemCaids = {
            "26": "BiSS",
            "01": "SEC",
            "06": "IRD",
            "55": "BET",
            "17": "BET",
            "05": "VIA",
            "18": "NAG",
            "09": "NDS",
            "0B": "CON",
            "0D": "CRW",
            "27": "EXS",
            "4B": "DRE",
            "4A": "DRE",
            "0E": "PWR",
            "10": "TAN",
            "56": "VERI"}

    @cached
    def getBoolean(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return False

        caids = info.getInfoObject(iServiceInformation.sCAIDs)
        if self.type is self.IS_FTA:
            if caids:
                return False
            return True
        if self.type is self.IS_CRYPTED:
            if caids:
                return True
            return False
        if caids:
            if self.type == self.SECA:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "01":
                        return True
                return False
            if self.type == self.BETA:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "55" or ("%0.4X" % int(caid))[:2] == "17":
                        return True
                return False
            if self.type == self.CONAX:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "0B":
                        return True
                return False
            if self.type == self.CRW:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "0D":
                        return True
                return False
            if self.type == self.DRE:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "4B" or ("%0.4X" % int(caid))[:2] == "4A":
                        return True
                return False
            if self.type == self.EXS:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "27":
                        return True
            if self.type == self.NAGRA:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "18":
                        return True
                return False
            if self.type == self.NDS:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "09":
                        return True
                return False
            if self.type == self.IRD:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "06":
                        return True
                return False
            if self.type == self.VIA:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "05":
                        return True
                return False
            if self.type == self.PWR:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "0E":
                        return True
                return False
            if self.type == self.VERI:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "56":
                        return True
                return False
            if self.type == self.TAN:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "10":
                        return True
                return False
            if self.type == self.BISS:
                for caid in caids:
                    if ("%0.4X" % int(caid))[:2] == "26":
                        return True
                return False
            self.poll_interval = self.my_interval
            self.poll_enabled = True
            ecm_info = self.ecmfile()
            if ecm_info:
                try:
                    caid = ("%0.4X" % int(ecm_info.get("caid", ""), 16))[:2]
                except Exception:
                    return False
                if self.type == self.SECA_C:
                    if caid == "01":
                        return True
                    return False
                if self.type == self.BETA_C:
                    if caid == "17" or caid == "55":
                        return True
                    return False
                if self.type == self.CONAX_C:
                    if caid == "0B":
                        return True
                    return False
                if self.type == self.CRW_C:
                    if caid == "0D":
                        return True
                    return False
                if self.type == self.DRE_C:
                    if caid == "4A" or caid == "4B":
                        return True
                    return False
                if self.type == self.EXS_C:
                    if caid == "27":
                        return True
                    return False
                if self.type == self.NAGRA_C:
                    if caid == "18":
                        return True
                    return False
                if self.type == self.NDS_C:
                    if caid == "09":
                        return True
                    return False
                if self.type == self.IRD_C:
                    if caid == "06":
                        return True
                    return False
                if self.type == self.VIA_C:
                    if caid == "05":
                        return True
                    return False
                if self.type == self.PWR_C:
                    if caid == "0E":
                        return True
                    return False
                if self.type == self.VERI_C:
                    if caid == "56":
                        return True
                    return False
                if self.type == self.TAN_C:
                    if caid == "10":
                        return True
                    return False
                if self.type == self.BISS_C:
                    if caid == "26":
                        return True
                    return False
                #oscam
                reader = ecm_info.get("reader", None)
                #cccam    
                using = ecm_info.get("using", "")
                #mgcamd
                source = ecm_info.get("source", "")
                if self.type == self.CRD:
                    #oscam
                    if source == "sci":
                        return True
                    #wicardd
                    if source != "cache" and source != "net" and source != "emu":
                        return True
                    return False
                source = ecm_info.get("source", "")
                if self.type == self.IS_EMU:
                    return using == "emu" or source == "emu" or source == "card" or reader == "emu" or source.find("card") > -1 or source.find("emu") > -1 or source.find("biss") > -1 or source.find("cache") > -1
                source = ecm_info.get("source", "")
                if self.type == self.IS_NET:
                    if using == "CCcam":
                        return 1
                    else:
                        if source != "cache" and source == "net" and source.find("emu") == -1:
                            return True
                           #return  (source != None and source == "net") or (source != None and source != "sci") or (source != None and source != "emu") or (reader != None and reader != "emu") or (source != None and source != "card") 
                else:
                    return False

        return False

    boolean = property(getBoolean)

    def runningSoftCamName(self, fullName = False):
               
        if DBG: j00zekDEBUG('[j00zekModCaidInfo2:runningSoftCamName] >>> fullName="%s"' % str(fullName) )

        def checkCam(txt):
            for scName in ('oscam_emu', 'oscam', 'cccam', 'mgcam'):
                if scName in procStat.lower():
                    if fullName:
                        return procStat
                    else:
                        return scName
            return None
          
        #trying to use last PID
        try:
            procStat = open(os.path.join("/proc", str(self.currPID), 'stat'), "r").read().split('(')[1].split(')')[0]
            foundSC = checkCam(procStat)
            if not foundSC is None:
                return foundSC
        except Exception as e:
                   
            if DBG: j00zekDEBUG('\t Exception trying to get name of curr.PID= %s : %s' % (os.path.join("/proc", str(self.currPID)), str(e) )) 
        #searching for new PID
        for f in os.listdir("/proc"):
            if os.path.isdir(os.path.join("/proc", f)):
                try:
                    pid = int(f)
                    if pid > self.currPID:
                        procStat = open(os.path.join("/proc", f, 'stat'), "r").read().split('(')[1].split(')')[0]
                        foundSC = checkCam(procStat)
                        if not foundSC is None:
                            self.currPID = pid
                            return foundSC
                except Exception as e:
                           
                    if DBG: j00zekDEBUG('\t Exception trying to analyze %s : %s' % (os.path.join("/proc", f), str(e) )) 
        return _('None SoftCam is running')

    def GetSlotCi(self): #by madhouse
        NUM_CI = SystemInfo["CommonInterface"]
        if NUM_CI and NUM_CI > 0:
            found_caid = False
            service_caids = []
            service_caid_list = []
            caid = '0x0'
            active_slot = -1
            service = self.source.service
            info = service and service.info()
            if info:
                service_caids = info.getInfoObject(iServiceInformation.sCAIDs)
                if service_caids:
                    for service_caid in service_caids:
                        service_caid_list.append((str(hex(int(service_caid)))))
                    for act_slot in range(NUM_CI):
                        ci_caids = []
                        ci_caid_list = []
                        ci_caids = eDVBCIInterfaces.getInstance().readCICaIds(act_slot)
                        if ci_caids:
                            for ci_caid in ci_caids:
                                ci_caid_list.append(str(hex(int(ci_caid))))
                            for service_caid in service_caid_list:
                                if service_caid in ci_caid_list:
                                    found_caid = True
                                    caid = service_caid
                                    active_slot = act_slot
                                    appname = eDVBCI_UI.getInstance().getAppName(act_slot)
                                    break
                            if found_caid:
                                break

            if found_caid:
                appname = str(appname)
            else:
                appname = ""
            ecmline = appname
        return ecmline

    def getCIdata(self, allVisible, showNameOfActive, service_caid_list): #CI data
        CIstring = ""
        appname = ""
        if DBG: j00zekDEBUG('\t service_caid_list="%s"' % str(service_caid_list))
        if self.NUM_CI and self.NUM_CI > 0:
            if self.eDVBCIUIInstance:
                for slot in range(self.NUM_CI):
                    if showNameOfActive:
                        ci_caids = []
                        ci_caid_list = []
                        ci_caids = eDVBCIInterfaces.getInstance().readCICaIds(slot)
                        if ci_caids:
                            for ci_caid in ci_caids:
                                ci_caid_list.append(str(hex(int(ci_caid))))
                        if DBG: j00zekDEBUG('\t ci_caid_list="%s"' % str(ci_caid_list))
                        for service_caid in service_caid_list:
                            if service_caid in ci_caid_list:
                                return r'\c0000ff00' + eDVBCI_UI.getInstance().getAppName(slot)
                    add_num = True
                    if CIstring:
                        CIstring += " "
                    state = self.eDVBCIUIInstance.getState(slot)
                    if state == -1: # EMPTY slot
                        if DBG: j00zekDEBUG('\t slot=%s, state=%s => empty' % (slot,state))
                        if not allVisible:
                            CIstring += ""
                            add_num = False
                        else:
                            CIstring += "\c00??2525"
                    else: #there is something in the slot
                        CIname = eDVBCI_UI.getInstance().getAppName(slot)
                        if state == 0: #reset
                            if DBG: j00zekDEBUG('\t slot=%s, state=%s => reset' % (slot,state))
                            if not allVisible:
                                CIstring += ""
                                add_num = False
                            else:
                                CIstring += r"\c007?7?7?"
                        elif state == 1:
                            if DBG: j00zekDEBUG('\t slot=%s, state=%s => init' % (slot,state))
                            CIstring += r'\c00ffa500' #pomaranczowy
                        elif state == 2:
                            if DBG: j00zekDEBUG('\t slot=%s, state=%s => ready' % (slot,state))
                            CIstring += r'\c0000ff00' #jasno zielony
                            if showNameOfActive:
                                return r'\c0000ff00'+ CIname
                    if add_num:
                        CIstring += "%d" % (slot + 1)
                if CIstring:
                    if showNameOfActive:
                        CIstring = CIname
                    else:
                        CIstring = _("CI slot: ") + CIstring
                    if DBG: j00zekDEBUG('\t CIstring="%s"' % CIstring)
            return CIstring
            
    @cached
    def getText(self):
               
        if DBG: j00zekDEBUG('[j00zekModCaidInfo2:getText] >>>self.type="%s", ciFormat.value="%s"' % (self.type, config.plugins.j00zekCC.ciFormat.value ) ) 
        textvalue = ""
        server = ""
        softCamName = ''
        service = self.source.service
        # name softcam name is independent, so here to always return it when requested
        if self.type == self.USE_CFG:
            if config.plugins.j00zekCC.ciFormat.value == '':
                return self.runningSoftCamName(True)
            elif   '%SCN'  in config.plugins.j00zekCC.ciFormat.value: softCamName = self.runningSoftCamName(False)
                                                            
            elif '%SCFN' in config.plugins.j00zekCC.ciFormat.value: softCamName = self.runningSoftCamName(True)
                                                           
        elif self.type == self.FORMAT:
                                   
            if   '%SCN'  in self.sfmt: softCamName = self.runningSoftCamName(False)
                                      
            elif '%SCFN' in self.sfmt: softCamName = self.runningSoftCamName(True)
        elif self.type == self.SOFTCAMNAME:
            return self.runningSoftCamName()
        elif self.type == self.SOFTCAMFULLNAME:
            return self.runningSoftCamName(True)
        #
        if not service:
            return softCamName
        else:
            info = service and service.info()
            ecm_info = self.ecmfile()
                        
            if not info: return softCamName
            elif not info.getInfoObject(iServiceInformation.sCAIDs): return _('Free-to-air')
                                       
            elif not ecm_info:
                if self.NUM_CI and self.NUM_CI > 0:
                    if 1: #mod by madhouse
                        CIinfo = self.GetSlotCi()
                    else:
                        service_caid_list = []
                        service_caids = info.getInfoObject(iServiceInformation.sCAIDs)
                        if service_caids:
                            for service_caid in service_caids:
                                service_caid_list.append(str(hex(int(service_caid))))
                        CIinfo = self.getCIdata(allVisible = False, showNameOfActive = True, service_caid_list = service_caid_list)
                    if CIinfo == '' and softCamName == '':
                        return _("no data from CI and emulator")
                    elif CIinfo == '':
                        return _("no data from CI")
                                      
                                                                
                    else:
                        return _(CIinfo)
                else:
                    return _("no data from the emulator")
            elif  self.type == self.ECMFILECONTENT: return self.ecmfileContent()
                                            
            elif  self.type == self.CAIDS:
                return '?'
            elif self.type == self.CRYPT2:
                self.poll_interval = self.my_interval
                self.poll_enabled = True
                info = service and service.info()
                if fileExists("/tmp/ecm.info"):
                    try:
                        caid = "%0.4X" % int(ecm_info.get("caid", ""),16)
                        textvalue = "%s" % self.systemTxtCaids.get(caid[:2])
                    except Exception:
                        textvalue =  _('nondecode')
                return textvalue
            else:
                self.poll_interval = self.my_interval
                self.poll_enabled = True
                # caid
                caid = "%0.4X" % int(ecm_info.get("caid", ""),16)
                if self.type == self.CAID:
                    return caid
                # crypt
                if self.type == self.CRYPT:
                    return "%s" % self.systemTxtCaids.get(caid[:2].upper())
                #pid
                try:
                    pid = "%0.4X" % int(ecm_info.get("pid", ""),16)
                except Exception:
                    pid = ""
                if self.type == self.PID:
                    return pid
                # oscam
                try:
                    prov = "%0.6X" % int(ecm_info.get("prov", ""),16)
                except Exception:
                    prov = ecm_info.get("prov", "")
                if self.type == self.PROV:
                    return prov
                if ecm_info.get("ecm time", "").find("msec") > -1:
                    ecm_time = ecm_info.get("ecm time", "")
                else:
                    ecm_time = ecm_info.get("ecm time", "").replace(".","").lstrip("0") + " msec"
                if self.type == self.DELAY:
                    return ecm_time
                #protocol
                protocol = ecm_info.get("protocol", "")
                #port
                port = ecm_info.get("port", "")
                # source    
                source = ecm_info.get("source", "")
                # server
                server = ecm_info.get("server", "")
                # hops
                hops = ecm_info.get("hops", "")
                #system
                system = ecm_info.get("system", "")
                #provider
                provider = ecm_info.get("provider", "")
                # reader
                reader = ecm_info.get("reader", "")
                if self.type == self.CRDTXT:
                    info_card = "False"
                    #oscam
                    if source == "sci":
                        info_card = "True"
                    #wicardd
                    if source != "cache" and source != "net" and source.find("emu") == -1:
                        info_card = "True"
                    return info_card
                if self.type == self.HOST:
                    return server
                if self.type == self.FORMAT or self.type == self.USE_CFG:
                    if self.type == self.USE_CFG:
                        self.sfmt = config.plugins.j00zekCC.ciFormat.value
                    textvalue = ""
                    params = self.sfmt.split(" ")
                            
                    for param in params:
                        if param != '':
                            if param[0] != '%': textvalue += param
                                                  
                            #server
                                               
                            elif param == "%S": textvalue += server
                            #hops
                            elif param == "%H": textvalue += hops
                                                 
                            #system
                            elif param == "%SY": textvalue += system
                                                   
                            #provider
                                                
                            elif param == "%PV": textvalue += provider
                            #port
                            elif param == "%SP": textvalue += port
                                                 
                            #protocol
                                                
                            elif param == "%PR": textvalue += protocol
                            #caid
                            elif param == "%C": textvalue += caid
                                                 
                            #Pid
                            elif param == "%P": textvalue += pid
                                                
                            #prov
                            elif param == "%p": textvalue += prov
                                                 
                            #sOurce
                                               
                            elif param == "%O": textvalue += source
                            #Reader
                                               
                            elif param == "%R": textvalue += reader
                            #ECM Time
                                               
                            elif param == "%T": textvalue += ecm_time
                            #SoftCamName
                                                 
                            elif param == "%SCN": textvalue += softCamName
                            #SoftCamFullName
                                                  
                            elif param == "%SCFN": textvalue += softCamName
                            #tabulator
                            elif param == "%t": textvalue += "\t"
                                                 
                            #new line
                            elif param == "%n": textvalue += "\n"
                                                 
                                                     
                            elif param[1:].isdigit(): textvalue=textvalue.ljust(len(textvalue)+int(param[1:]))
                            
                            if len(textvalue) > 0:
                                if textvalue[-1] != "\t" and textvalue[-1] != "\n":
                                    textvalue+=" "
                    return textvalue[:-1]
                if self.type == self.ALL:
                    if source == "emu":
                        textvalue = "%s - %s (Prov: %s, Caid: %s)" % (source, self.systemTxtCaids.get(caid[:2]), prov, caid)
                    #new oscam ecm.info with port parametr
                    elif reader != "" and source == "net" and port != "": 
                        textvalue = "%s - Prov: %s, Caid: %s, Reader: %s, %s (%s:%s) - %s" % (source, prov, caid, reader, protocol, server, port, ecm_time.replace('msec','ms'))
                    elif reader != "" and source == "net": 
                        textvalue = "%s - Prov: %s, Caid: %s, Reader: %s, %s (%s) - %s" % (source, prov, caid, reader, protocol, server, ecm_time.replace('msec','ms'))
                    elif reader != "" and source != "net": 
                        textvalue = "%s - Prov: %s, Caid: %s, Reader: %s, %s (local) - %s" % (source, prov, caid, reader, protocol, ecm_time.replace('msec','ms'))
                    elif server == "" and port == "" and protocol != "": 
                        textvalue = "%s - Prov: %s, Caid: %s, %s - %s" % (source, prov, caid, protocol, ecm_time.replace('msec','ms'))
                    elif server == "" and port == "" and protocol == "": 
                        textvalue = "%s - Prov: %s, Caid: %s - %s" % (source, prov, caid, ecm_time.replace('msec','ms'))
                    else:
                        try:
                            textvalue = "%s - Prov: %s, Caid: %s, %s (%s:%s) - %s" % (source, prov, caid, protocol, server, port, ecm_time.replace('msec','ms'))
                        except Exception:
                            pass
                if self.type == self.SHORT:
                    if source == "emu":
                        textvalue = "%s - %s (Prov: %s, Caid: %s)" % (source, self.systemTxtCaids.get(caid[:2]), prov, caid)
                    elif server == "" and port == "": 
                        textvalue = "%s - Prov: %s, Caid: %s - %s" % (source, prov, caid, ecm_time.replace('msec','ms'))
                    else:
                        try:
                            textvalue = "%s - Prov: %s, Caid: %s, %s:%s - %s" % (source, prov, caid, server, port, ecm_time.replace('msec','ms'))
                        except Exception:
                            pass
        return textvalue

    text = property(getText)

    def ecmfileContent(self):
               
        if DBG: j00zekDEBUG('[j00zekModCaidInfo2:ecmfileContent] >>>')
        self.poll_interval = self.my_interval
        self.poll_enabled = True
        ecminfo = ""
        try:
            if fileExists("/tmp/ecm.info"):
                with open("/tmp/ecm.info", "r") as ecmfiles:
                    for line in ecmfiles:
                        if line.find("caid:") > -1 or line.find("provider:") > -1 or line.find("provid:") > -1 or line.find("pid:") > -1 or line.find("hops:") > -1  or line.find("system:") > -1 or line.find("address:") > -1 or line.find("using:") > -1 or line.find("ecm time:") > -1:
                            line = line.replace(' ',"").replace(":",": ")
                        if line.find("caid:") > -1 or line.find("pid:") > -1 or line.find("reader:") > -1 or line.find("from:") > -1 or line.find("hops:") > -1  or line.find("system:") > -1 or line.find("Service:") > -1 or line.find("CAID:") > -1 or line.find("Provider:") > -1:
                            line = line.strip('\n') + "  "
                        if line.find("Signature") > -1:
                            line = ""
                        if line.find("=") > -1:
                            line = line.lstrip('=').replace('======', "").replace('\n', "").rstrip() + ', '
                        if line.find("ecmtime:") > -1:
                            line = line.replace("ecmtime:", "ecm time:")
                        if line.find("response time:") > -1:
                            line = line.replace("response time:", "ecm time:").replace("decoded by", "by")
                        if not line.startswith('\n'):
                            if line.find('pkey:') > -1:
                                line = '\n' + line + '\n'
                            ecminfo += line
                    ecmfiles.close()
        except Exception as e:
                   
            if DBG: j00zekDEBUG('\t Exception analyzing content of /tmp/ecm.info : %s' % str(e) )
        return ecminfo
        
    def ecmfile(self):
        global info
        global old_ecm_mtime
        ecm = None
        service = self.source.service
        if service:
            try:
                ecm_mtime = os.stat("/tmp/ecm.info").st_mtime
                if not os.stat("/tmp/ecm.info").st_size > 0:
                    info = {}
                if ecm_mtime == old_ecm_mtime:
                    return info
                old_ecm_mtime = ecm_mtime
                ecmf = open("/tmp/ecm.info", "r")
                ecm = ecmf.readlines()
            except Exception:
                old_ecm_mtime = None
                info = {}
                return info

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
                                if it_tmp[-1].find('emu') >-1 or it_tmp[-1].find('EMU') >-1 or it_tmp[-1].find('cache') > -1 or it_tmp[-1].find('card') > -1 or it_tmp[-1].find('biss') > -1:
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
                                if item[1].lower().find("local") > -1: #some oscams return also number of local
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
        Converter.changed(self, (self.CHANGED_POLL,))

    def ciModuleStateChanged(self, slot):
               
        if DBG: j00zekDEBUG('[j00zekModCaidInfo2:getText] >>>')
        self.changed(True)
