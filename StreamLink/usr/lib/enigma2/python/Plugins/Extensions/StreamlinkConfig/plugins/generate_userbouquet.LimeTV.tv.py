#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Coded by j00zek
#

import os
import re
import sys

from datetime import date

def doLog(txt, append = 'a' ):
    print str(txt)
    open("/tmp/LimeTVBouquet.log", append).write(str(txt) + '\n')

def clearContent(WebContent, startTag, endTag):
    i = WebContent.index(startTag)
    WebContent = WebContent[i:]
    i = WebContent.index(endTag)
    WebContent = WebContent[:i]
    return WebContent

def getList( retList, WebContent, reFindString ): #getList([], nowContent, '<span>(.*?)</span>.*<ul>')
    FC = re.findall(reFindString, WebContent, re.S)
    if FC:
        for i in FC:
            retList.append(i)
    return retList

def generate_E2bouquet(bouquet_name, file_name, frameWork, streamlinkURL):
    doLog('Generuje bukiet %s do pliku %s ...' % (bouquet_name,file_name), 'w')
    
    mainURL = 'https://limehd.tv/'
    #get channels list
    import requests
    response = requests.get(mainURL)
    
    webPage = response.content
    webPage = clearContent( webPage, '<ul class="inner channels-data">', '</ul>' )
    channelsRecords = getList([], webPage, '<li (.*?)</li>') # returns each channel data as one item
    channelsList = []
    for channel in channelsRecords:
        #getList(channelsList, channel, "href=\"/([^\"]*)\".*Player\.online[^']*'([^']+)'")
        getList(channelsList, channel, "href=\"/([^\"]*)\".*img alt=\"([^\"]*)\"")

    #generate bouquet

    doLog('Generuje bukiet dla %s ...' % bouquet_name)
    open("/tmp/LimeTVBouquet.log", "a").write('Generuje bukiet dla %s ...\n' % frameWork)
    data = '#NAME %s aktualizacja %s\n' % (bouquet_name, date.today().strftime("%d-%m-%Y"))
    for item in channelsList:
        title=item[0]
        info=item[1]
        if not 'closed-channel' in info:
            Reference = '%s:0:1:0:0:0:0:0:0:0' % frameWork
            #data += '#SERVICE %s:%s%s%s:%s\n' % (ServiceID, streamlinkURL, params['video_url'].replace(':','%3a') , title)
            #data += '#SERVICE %s:%s:%s\n' % (Reference, url, title)
            data += '#SERVICE %s:%s%s%s:%s (%s)\n' % (Reference, streamlinkURL, mainURL.replace(':','%3a'), title, title, info)
            data += '#DESCRIPTION %s (%s)\n' % (title, info)

    with open(file_name, 'w') as f:
        f.write(data.encode('utf-8'))
        f.close()

    doLog('Tworzenie bukietu zakończone')
    f = open('/etc/enigma2/bouquets.tv','r').read()
    if not os.path.basename(file_name) in f:
        doLog('Dodano bukiet do listy')
        if not f.endswith('\n'):
            f += '\n'
        f += '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % os.path.basename(file_name)
        open('/etc/enigma2/bouquets.tv','w').write(f)

if __name__ == '__main__':
    if len(sys.argv) >=5:
        filename        = sys.argv[1]
        streamlinkURL   = 'http%3a//127.0.0.1%3a' + sys.argv[4] + '/'
        frameWork       = sys.argv[5]
    else:
        filename        = '/etc/enigma2/userbouquet.LimeTV.tv'
        streamlinkURL   = 'http%3a//127.0.0.1%3a8088/'
        frameWork       =  "4097"

    bname = filename.replace('/etc/enigma2/','').replace('userbouquet.','')[:-3] + ' (%s)' % frameWork
    generate_E2bouquet(bname, filename, frameWork, streamlinkURL)