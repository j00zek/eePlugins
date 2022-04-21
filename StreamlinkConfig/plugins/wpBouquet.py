# -*- coding: utf-8 -*-
#
#   Based on Kodi plugin.video.pilot.wp by c0d34fun licensed under GNU GENERAL PUBLIC LICENSE. Version 2, June 1991
#   Coded by j00zek
#

import sys
import os

from wpConfig import headers
from wpConfig import params #'login_url', 'main_url', 'video_url', 'close_stream_url'
from wpConfig import data
from wpConfig import getCookie, saveCookie

def _generate_E2bouquet():
    def doLog(txt, append = 'a' ):
        print(txt)
        open("/tmp/wpBouquet.log", append).write(txt + '\n')
      
    doLog('', 'w')
    if file_name == '':
        doLog('Ustaw nazwę pliku docelowego!')
        return

    #login
    StoredCookie = getCookie()
    if not StoredCookie:
        StoredCookie = _login()
        if not StoredCookie:
            doLog('Nieudane logowanie. Sprawdź login i hasło w ustawieniach wtyczki.')
            return

    #get channels list
    import requests
    headers.update({'Cookie': StoredCookie})
    response = requests.get(
            params['main_url'],
            verify=False,
            headers=headers,
          ).json()
    
    channelsList = response.get('data', [])

    #generate bouquet
    from channelsMappings import name2serviceDict, name2service4wpDict, name2nameDict
    from datetime import date

    doLog('Generuje bukiet dla %s ...' % frameWork)
    open("/tmp/wpBouquet.log", "a").write('Generuje bukiet dla %s ...\n' % frameWork)
    data = '#NAME PILOT.WP.PL aktualizacja %s\n' % date.today().strftime("%d-%m-%Y")
    for item in channelsList:
        #print item
        if item.get('access_status', '') != 'unsubscribed':
            id = item.get('id', None)
            title = item.get('name', '').strip()
            lcaseTitle = title.lower().replace('ś','s').replace('ń','n').replace(' ','')
            standardReference = '%s:0:1:0:0:0:0:0:0:0' % frameWork
            #mapowanie bezpośrednie zdefiniowane dla wp
            ServiceID = name2service4wpDict.get(title , standardReference)
            if ServiceID.startswith(standardReference):
                ServiceID = name2serviceDict.get(name2nameDict.get(lcaseTitle, lcaseTitle) , standardReference)
            #mapowanie po znalezionych kanalach w bukietach
                if ServiceID.startswith(standardReference):
                    doLog("\t- Brak mapowania referencji kanału  %s (%s) dla EPG" % (title, lcaseTitle))
            if not ServiceID.startswith(frameWork):
                ServiceIDlist = ServiceID.split(':')
                ServiceIDlist[0] = frameWork
                ServiceID = ':'.join(ServiceIDlist)
            data += '#SERVICE %s:%s%s%s:%s\n' % (ServiceID, streamlinkURL, params['video_url'].replace(':','%3a') , id, title)
            data += '#DESCRIPTION %s\n' % (title)

    with open(file_name, 'wb') as f:
        f.write(data.encode('utf-8'))
        f.close()

    doLog('Wygenerowano bukiet do pliku %s' % file_name)
    f = open('/etc/enigma2/bouquets.tv','r').read()
    if not os.path.basename(file_name) in f:
        doLog('Dodano bukiet do listy')
        if not f.endswith('\n'):
            f += '\n'
        f += '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % os.path.basename(file_name)
        open('/etc/enigma2/bouquets.tv','w').write(f)

def _login():
    def cookiesToString(cookies):
        try:
            return "; ".join([str(x) + "=" + str(y) for x, y in cookies.get_dict().items()])
        except Exception as e:
            print(str(e))
        return None
      
    import requests
        
    response = requests.post(
            params['login_url'],
            json=data,
            verify=False,
            headers=headers
        )

    meta = response.json().get('_meta', None)
    if meta is not None:
        if meta.get('error', {}).get('name', None) is not None:
            return None
        
    saveCookie(cookiesToString(response.cookies))
    return getCookie()

if __name__ == '__main__':
    if len(sys.argv) >=5:
        file_name = sys.argv[1]
        #print 'filename' , file_name
        #print path + file_name
        data['login'] = sys.argv[2]
        #print 'username' , data['login']
        data['password'] = sys.argv[3]
        #print 'password' , data['password']
        streamlinkURL = 'http%%3a//127.0.0.1%%3a%s/' % sys.argv[4]
        frameWork = sys.argv[5]
        #print frameWork
        _generate_E2bouquet()
    elif len(sys.argv) == 2 and sys.argv[1] == 'checkLogin':
        if _login():
            print('Zalogowano poprawnie\n\n')
        else:
            print('Nieudane logowanie. Sprawdź login i hasło w ustawieniach wtyczki.\n\n')
