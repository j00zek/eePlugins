# -*- coding: utf-8 -*-
#
#   Based on Kodi plugin.video.pilot.wp by c0d34fun licensed under GNU GENERAL PUBLIC LICENSE. Version 2, June 1991
#   Coded by j00zek
#

import sys
import os
from channelsMappings import name2serviceDict, name2service4wpDict, name2nameDict

def doLog(txt, append = 'a' ):
    print(txt)
    open("/tmp/StreamlinkConfig.log", append).write('_assignRefsInBouquet: ' + txt + '\n')

def _assignRefsInBouquet():
    doLog('szukam poprawnych referencji dla kanałów IPTV w bukiecie %s ...' % bouquetFileName)
    corrected = ''
    with open(bouquetFileName, 'r') as fn:
        content = fn.readlines()
        fn.close()
        for line in content:
            line = line.strip() 
            if line.startswith('#SERVICE ') and 'https' in line:
                LineP2 = line[9:]
                Parts = LineP2.split(':')
                if len(Parts) >= 12:
                    title = Parts[11].strip()
                    lcaseTitle = title.lower().replace('ś','s').replace('ń','n').replace(' ','')
                    ServiceID = name2serviceDict.get(name2nameDict.get(lcaseTitle, lcaseTitle) , '')
                    if ServiceID != '':
                        ServiceIDlist = ServiceID.split(':')
                        for idx in [2,3,4,5,6,7,8,9]:
                            Parts[idx] = ServiceIDlist[idx]
                        ServiceID = ':'.join(Parts)
                        line = '#SERVICE %s' % ServiceID
                print(line)
            corrected += '%s\n' % line

    return
    with open(bouquetFileName, 'wb') as f:
        f.write(data.encode('utf-8'))
        f.close()

    doLog('Wygenerowano bukiet do pliku %s' % bouquetFileName)
    f = open('/etc/enigma2/bouquets.tv','r').read()
    if not os.path.basename(bouquetFileName) in f:
        doLog('Dodano bukiet do listy')
        if not f.endswith('\n'):
            f += '\n'
        f += '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % os.path.basename(bouquetFileName)
        open('/etc/enigma2/bouquets.tv','w').write(f)

def _assignFrameworkInBouquet():
    doLog('TBD Zmieniam renderer wideo na %s dla kanałów IPTV w bukiecie %s ...' % (changeType, bouquetFileName))

def _assignStreamlinkInBouquet():
    doLog('TBD Zmieniam renderer wideo na %s dla kanałów IPTV w bukiecie %s ...' % (changeType, bouquetFileName))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        doLog('za mało danych wejsciowych')
    else:
        bouquetFileName = os.path.join('/etc/enigma2', sys.argv[1])
        selectedOption = sys.argv[2]
        #doLog('selectedOption="%s"' % selectedOption)
        if selectedOption == 'e': #Try to find correct reference to enable EPG
            _assignRefsInBouquet()
        else:
            changeType = sys.argv[3]
            if selectedOption == 'f': #Try to find correct reference to enable EPG
                _assignFrameworkInBouquet()
            elif selectedOption == 'sl': #Try to find correct reference to enable EPG
                _assignStreamlinkInBouquet()
            else:
                doLog('nieznana opcja :(')
