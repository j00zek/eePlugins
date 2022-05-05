import os

streamlinkDict = {}

def getE2config( CFGname, CFGdefault = "noCFG" ):
    global streamlinkDict
    if len(streamlinkDict) == 0:
        streamlinkDict["Loaded"] = 0
        if os.path.isfile('/etc/enigma2/settings'):
            with open('/etc/enigma2/settings', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('config.plugins.streamlinksrv.') and '=' in line:
                        cfg = line.split('=')
                        val = cfg[1]
                        if val.isdigit():
                            val = int(val)
                        elif val == 'true':
                            val = True
                        elif val == 'false':
                            val = False
                        streamlinkDict[cfg[0].replace('config.plugins.streamlinksrv.','')] = val
                        streamlinkDict["Loaded"] += 1
                f.close()
    return streamlinkDict.get(CFGname.replace('config.plugins.streamlinksrv.',''), CFGdefault)
