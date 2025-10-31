#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Coded by j00zek
#

import os
import re
import sys

DBG=False
if __name__ == '__main__':
    if DBG:
        print('installBouquet >>>')
        for arg in sys.argv:
            print(arg)
    if len(sys.argv) >=4:
        bouquetFileName = sys.argv[1]
        Port = sys.argv[2]
        framework = sys.argv[3]
        useWrappers = sys.argv[4]
        print(useWrappers)
        fw = open('/etc/enigma2/%s' % bouquetFileName,'w')
        sf = open('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/IPTVbouquets/%s' % bouquetFileName,'r')
        while True:
            line = sf.readline()
            if not line:
                break
            if line.startswith('#SERVICE '):
                line = line[9:]
                items = line.split(':', 1)

                if not useWrappers:
                    items[1] = items[1].replace('YT-DLP%3a//',streamlinkURL).replace('YT-DL%3a//',streamlinkURL).replace('streamlink%3a//',streamlinkURL)
                elif 'YT-DL' in items[1] or 'streamlink%3a//' in items[1]:
                    items[0] = '4097' #wrappery tylko z oryginalnym frameworkiem

                if str(framework) != "0":
                    items[0] = framework
                fw.write('#SERVICE %s' % ':'.join(items))
            elif line.strip() != '':
                fw.write(line)
        fw.close()
        print('Utworzono bukiet %s z rendererem %s' % (bouquetFileName,framework))
        #dodanie do listy bukietow
        msg = ''
        for TypBukietu in('/etc/enigma2/bouquets.tv','/etc/enigma2/bouquets.radio'):
            if TypBukietu.endswith('.radio') and bouquetFileName.endswith('.tv'):
                continue
            if os.path.exists(TypBukietu):
                f = open(TypBukietu,'r').read()
                if not os.path.basename(bouquetFileName) in f:
                    if not f.endswith('\n'):
                        f += '\n'
                    f += '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % os.path.basename(bouquetFileName)
                    msg = 'Dodano bukiet do listy'
                    open(TypBukietu,'w').write(f)
        print(msg)
