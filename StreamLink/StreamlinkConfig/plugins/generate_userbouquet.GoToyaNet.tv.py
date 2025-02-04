# -*- coding: utf-8 -*-
#
#   Coded by j00zek
#

import sys
import os
import urllib2
import re

preferedTypes4idDict = {'51656539': '&prefertype=mpd',
                        '51449546': '&prefertype=mpd',
                        '51161266': '&prefertype=mpd',
                          }
                          
def getUrl(url): #1-1 z wtyczki do kodi
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def get_tvpLiveStreams(url='http://tvpstream.vod.tvp.pl'): #1-1 z wtyczki do kodi
    data=getUrl(url)
    #livesrc="http://tvpstream.vod.tvp.pl/sess/tvplayer.php?object_id=%s"
    livesrc="http://tvp_player.php?object_id=%s"
    img = re.compile('data-video-id=[\'"](\d+)[\'"]\s+title=[\'"](.*?)[\'"].*?data-stationname=[\'"](.*?)[\'"].+?<img src=[\'"](.*?)[\'"]',re.DOTALL).findall(data)
    out=[]
    for id,title,channel,imgalt in img:
        #out.append({'title':'[B][COLOR orange]'+channel+'[/COLOR][/B]'+' '+title,'img':imgalt,
        #            'url':livesrc % id})
        out.append({'title':channel, 'id':id , 'descr':title,'img':imgalt, 'url':livesrc % id}) #j00zek dla e2 suche dane
    return out

def _generate_E2bouquet(bouquet_name, file_name, frameWork, streamlinkURL):
    if file_name == '':
        print('Ustaw nazwę pliku docelowego!')
        return

    #get channels list
    channelsList = get_tvpLiveStreams()
    
    #generate bouquet
    from channelsMappings import name2serviceDict, name2nameDict
    from datetime import date

    print('Generuje bukiet dla %s ...' % frameWork)
    open("/tmp/wpBouquet.log", "a").write('Generuje bukiet dla %s ...\n' % frameWork)
    data = '#NAME %s aktualizacja %s\n' % (bouquet_name, date.today().strftime("%d-%m-%Y"))
    for item in channelsList:
        #print item
        title = str(item.get('title', ''))
        id = str(item.get('id', ''))
        prefer_stream_type = preferedTypes4idDict.get(id,'')
        descr = str(item.get('descr', ''))
        img = str(item.get('img', ''))
        if title == '':
            if 'All live from Poland' in descr:
                title = 'Poland In'
            elif 'Msze ' in descr:
                title = 'TVP Msze święte z Jasnej Góry'
            elif 'Wilno' in descr:
                title = 'TVP Wilno'
            elif id == '51161266':
                title = 'TVP Kultura2'
            elif id == '51449546':
                title = 'TVP ferie'
            elif id == '51251441':
                title = 'TVP Polonia'
            else:
                title = descr
                
        lcaseTitle = title.lower().replace(' ','')
        video_url = item.get('url', '').replace(':','%3a')
        if title != '' and video_url != '':
            video_url += prefer_stream_type
            standardReference = '%s:0:1:0:0:0:0:0:0:0' % frameWork
            #mapowanie po znalezionych kanalach w bukietach
            ServiceID = name2serviceDict.get(name2nameDict.get(lcaseTitle, lcaseTitle) , standardReference)
            if ServiceID.startswith(standardReference):
                #print("\t- Brak mapowania referencji kanału dla EPG %s" % item)
                print("\t- Brak mapowania referencji kanału  %s (%s/%s) dla EPG" % (title, lcaseTitle, id))
            if not ServiceID.startswith(frameWork):
                ServiceIDlist = ServiceID.split(':')
                ServiceIDlist[0] = frameWork
                ServiceID = ':'.join(ServiceIDlist)
            data += '#SERVICE %s:%s%s:%s\n' % (ServiceID, streamlinkURL, video_url, title)
            data += '#DESCRIPTION %s\n' % (title)

    with open(file_name, 'w') as f:
        f.write(data.encode('utf-8'))
        f.close()

    print('Wygenerowano bukiet do pliku %s' % file_name)
    f = open('/etc/enigma2/bouquets.tv','r').read()
    if not os.path.basename(file_name) in f:
        print('Dodano bukiet do listy')
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
        filename        = '/etc/enigma2/userbouquet.GoToyaNet.tv'
        streamlinkURL   = 'http%3a//127.0.0.1%3a8088/'
        frameWork       =  "4097"
        
    if str(frameWork) == "0":
        frameWork = "4097"

    bname = filename.replace('/etc/enigma2/','').replace('userbouquet.','')[:-3] + ' (%s)' % frameWork
    if 0:
        _generate_E2bouquet(bname, filename, frameWork, streamlinkURL)
    else:
        print('NIE SKONCZONE - NIE DZIALA')
