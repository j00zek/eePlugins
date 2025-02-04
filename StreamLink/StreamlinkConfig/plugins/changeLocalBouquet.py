# -*- coding: utf-8 -*-
#
#   Coded by j00zek
#

import sys
import os

def doLog(txt, append = 'a' ):
    print(txt)
    open("/tmp/StreamlinkConfig.log", append).write('_assignRefsInBouquet: ' + txt + '\n')

def _assignFrameworkInBouquet():
    #framework = 0 to nic nie zmieniaj
    doLog('Zmieniam renderer wideo na %s dla kanałów IPTV w bukiecie %s ...' % (nowyFramework, bouquetFileName))
    myOutFile = ''
    counter = 0
    with open(bouquetFileName,'r') as f:
        myInFile = f.readlines()
    for line in myInFile:
        outLine = line
        if line.startswith('#SERVICE '):
            serviceParts = line.replace('#SERVICE ','').split(':')
            if serviceParts[10].strip() != '': # serwis iptv
                if serviceParts[0] != nowyFramework:
                    serviceParts[0] = nowyFramework
                    outLine = '#SERVICE ' + ':'.join(serviceParts)
                    counter += 1
        myOutFile += outLine
    if counter > 0:
        with open(bouquetFileName,'w') as f:
            f.write(myOutFile)
        doLog('Zmieniono framework dla %s serwisów IPTV' % counter)
    else:
        doLog('Nie znaleziono serwisów IPTV lub już korzystają z żądanego frameworka')
    return

def _assignStreamlinkInBouquet():
    doLog('Zmieniam wywoływanie wrappperów na 127.0.0.1:8088 dla kanałów IPTV w bukiecie %s ...' % bouquetFileName)
    myOutFile = ''
    counter = 0
    with open(bouquetFileName,'r') as f:
        myInFile = f.readlines()
    for line in myInFile:
        outLine = line
        if line.startswith('#SERVICE '):
            serviceParts = line.replace('#SERVICE ','').split(':')
            if serviceParts[10].strip() != '': # serwis iptv
                for wrapper in ('YT-DLP%3a//' , 'YT-DL%3a//', 'streamlink%3a//'):
                    if serviceParts[10].startswith(wrapper):
                        outLine = line.replace(wrapper,'http%3a//127.0.0.1%3a8088/')
                        #print(outLine)
                        counter += 1
        myOutFile += outLine
    if counter > 0:
        with open(bouquetFileName,'w') as f:
            f.write(myOutFile)
        doLog('Zmieniono framework dla %s serwisów IPTV' % counter)
    else:
        doLog('Nie znaleziono serwisów IPTV lub już korzystają z żądanego frameworka')
    return

if __name__ == '__main__':
    if len(sys.argv) < 3:
        doLog('za mało danych wejsciowych')
    else:
        bouquetFileName = os.path.join('/etc/enigma2', sys.argv[1])
        selectedOption = sys.argv[2]
        if selectedOption == 'f': #zmiana frameworka
            nowyFramework = sys.argv[3]
            _assignFrameworkInBouquet()
        elif selectedOption == 'w2s': #zmiana wrappera na 127.0.0.1
            _assignStreamlinkInBouquet()
        else:
            doLog('nieznana opcja :(')
