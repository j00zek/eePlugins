#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Coded by j00zek
#

import os
import re
import sys
import requests
from urllib.parse import quote as urllib_quote, unquote as urllib_unquote
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

DBG=False

def ensure_str(string2decode):
    if isinstance(string2decode, bytes):
        return string2decode.decode('utf-8', 'ignore')
    return string2decode

def downloadWebPage(webURL, newHEADERS = None):
        def decodeHTML(text):
            text = text.replace('&#243;', 'ó')
            text = text.replace('&#176;', '°').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
            text = text.replace('&#228;', 'ä').replace('&#196;', 'Ă').replace('&#246;', 'ö').replace('&#214;', 'Ö').replace('&#252;', 'ü').replace('&#220;', 'Ü').replace('&#223;', 'ß')
            return text
        
        webContent = ''
        try:
            if newHEADERS is None:
                HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                        'Accept-Charset': 'utf-8', 
                        'Content-Type': 'text/html; charset=utf-8'
                      }
            else:
                HEADERS = newHEADERS
            resp = requests.get(webURL, headers=HEADERS, timeout=5)
            webContent = ensure_str(resp.content)
            webHeader = resp.headers
            #webContent = urllib_unquote(webContent)
            webContent = decodeHTML(webContent)
            #print("webHeader: %s" % resp.headers )
        except Exception as e:
            print("EXCEPTION '%s' in downloadWebPage() for %s" % (str(e), webURL) )
            webContent = ''
        return ensure_str(webContent)

if __name__ == '__main__':
    if DBG:
        print('downloadBouquet >>>')
        for arg in sys.argv:
            print(arg)
    if len(sys.argv) >=4:
        bouquetFileName = sys.argv[1]
        bouquetURL = sys.argv[2]
        streamlinkURL = 'http%%3a//127.0.0.1%%3a%s/' % sys.argv[3]
        framework = sys.argv[4]
        if sys.argv[5] == 'False' or sys.argv[5] == 'n':
            useWrappers = False
        else:
            useWrappers = True
        fw = open('/etc/enigma2/%s' % bouquetFileName,'w')
        #fw = open('/tmp/%s' % bouquetFileName,'w')
        sf = downloadWebPage(bouquetURL)
        open("/tmp/downloadBouquet.log", "a").write(sf)
        sfLines = sf.split('\n')
        for line in sfLines:
            if line.startswith('#SERVICE '):
                line = line[len('#SERVICE '):]
                items = line.split(':', 1)
                if str(framework) != "0":
                    items[0] = framework
                if not useWrappers:
                    items[1] = items[1].replace('YT-DLP%3a//',streamlinkURL).replace('YT-DL%3a//',streamlinkURL).replace('streamlink%3a//',streamlinkURL)
                elif 'YT-DL' in items[1] or 'streamlink%3a//' in items[1]:
                    items[0] = '4097' #wrappery tylko z oryginalnym frameworkiem
                fw.write('#SERVICE %s\n' % ':'.join(items))
            elif line.strip() != '':
                fw.write('%s\n' % line)
        fw.close()
        print('Pobrano bukiet %s z rendererem %s' % (bouquetFileName,framework))
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
