import os

streamlinkDict = {}

#### get user configs ####
def readCFG(cfgName, defVal = ''):
    retValue = defVal
    for cfgPath in ['/j00zek/streamlink_defaults/','/hdd/User_Configs']:
        if os.path.exists(os.path.join(cfgPath, cfgName)):
            retValue = open(os.path.join(cfgPath, cfgName), 'r').readline().strip()
            break
    return retValue

def getE2config( CFGname, CFGdefault = "noCFG" ):
    global streamlinkDict
    if len(streamlinkDict) == 0:
        streamlinkDict["Loaded"] = 0
        if os.path.isfile('/etc/enigma2/settings'):
            with open('/etc/enigma2/settings', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('config.plugins.streamlinkSRV.') and '=' in line:
                        cfg = line.split('=')
                        val = cfg[1]
                        if val.isdigit():
                            val = int(val)
                        elif val == 'true':
                            val = True
                        elif val == 'false':
                            val = False
                        streamlinkDict[cfg[0].replace('config.plugins.streamlinkSRV.','')] = val
                        streamlinkDict["Loaded"] += 1
                f.close()
    retVal = streamlinkDict.get(CFGname.replace('config.plugins.streamlinkSRV.',''), CFGdefault)
    if retVal == CFGdefault:
        retVal = readCFG(CFGname.replace('config.plugins.streamlinkSRV.',''), CFGdefault)
    return retVal
