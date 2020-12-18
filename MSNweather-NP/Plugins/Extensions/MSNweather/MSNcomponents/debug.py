from datetime import datetime
from os import path, system

myPATH = '/tmp/.MSNdata'
if not path.exists(myPATH):
    system('mkdir -p %s' % myPATH)
    
def clearLogs():
    system('rm -f %s/*.log)' % myPATH)

def getE2config( CFGname, CFGdefault = "noCFG" ):
    E2config = {}
    if path.isfile('/etc/enigma2/settings'):
        with open('/etc/enigma2/settings', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('config.plugins.MSNweatherNP.') and '=' in line:
                    cfg = line.split('=')
                    val = cfg[1]
                    if val.isdigit():
                        val = int(val)
                    elif val == 'true':
                        val = True
                    elif val == 'false':
                        val = False
                    E2config[cfg[0].replace('config.plugins.MSNweatherNP.','')] = val
            f.close()
    return E2config.get(CFGname.replace('config.plugins.MSNweatherNP.',''), CFGdefault)

def printDEBUG( myFUNC = '' , myText = '' , logFileName = 'MSNweather.log'):
    try:
        from Components.config import config
        printDebugEnabled =  config.plugins.MSNweatherNP.DebugEnabled.value
        printDebugSize = config.plugins.MSNweatherNP.DebugSize.value
    except Exception:
        printDebugEnabled = getE2config('DebugEnabled', False)
        printDebugSize = getE2config('DebugSize', 100000)
    
    if printDebugEnabled or myFUNC == 'devDBG' or 'EXCEPTION' in myFUNC:
        myDEBUGfile = '%s/%s' % (myPATH, logFileName)
        print ("[%s] %s" % (myFUNC,myText))
        if myFUNC == 'INIT':
            if logFileName == 'MSNweather.log':
                system('rm -f %s/aqq.log' % myPATH)
            f = open(myDEBUGfile, 'w')
        else:
            f = open(myDEBUGfile, 'a')
        f.write('[%s] %s%s\n' % (str(datetime.now()), myFUNC, myText))
        f.close
        if path.getsize(myDEBUGfile) > int(printDebugSize):
            system('sed -i -e 1,10d %s' % myDEBUGfile)
