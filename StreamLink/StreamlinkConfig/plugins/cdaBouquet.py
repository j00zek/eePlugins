# -*- coding: utf-8 -*-
#
#   Based on Kodi plugin.video.cdaplMB. by mbebe licensed under GNU GENERAL PUBLIC LICENSE. Version 2, June 1991
#   Coded by j00zek
#

import sys, os, re, json, base64, math, random
import time

import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

from cdaConfig import getJson, getSetting, saveSetting

def _generate_E2bouquet(file_name, frameWork, streamlinkURL):
    def doLog(txt, append = 'a' ):
        print(txt)
        open("/tmp/cdaBouquet.log", append).write(txt + '\n')
      
    doLog('', 'w')

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
    open("/tmp/cdaBouquet.log", "a").write('Generuje bukiet dla %s ...\n' % frameWork)
    data = '#NAME PILOT.CDA.PL aktualizacja %s\n' % date.today().strftime("%d-%m-%Y")
    for item in channelsList:
        #print item
        if item.get('access_status', '') != 'unsubscribed':
            id = item.get('id', None)
            title = item.get('name', '').strip()
            lcaseTitle = title.lower().replace('ś','s').replace('ń','n').replace(' ','')
            standardReference = '%s:0:1:0:0:0:0:0:0:0' % frameWork
            #mapowanie po znalezionych kanalach w bukietach
            ServiceID = name2serviceDict.get(name2nameDict.get(lcaseTitle, lcaseTitle) , standardReference)
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

def LogowanieCda():
    username = getSetting('login')
    password = getSetting('password')  
    refr_token = getSetting('refr_token')  
    if username and password:
        if not refr_token:
            import hashlib
            import hmac
            import base64
            #if sys.version_info >= (3,0,0):
            passw = password.encode('utf-8') if sys.version_info >= (3,0,0) else password
            md5password=hashlib.md5(passw).hexdigest()    
            secret = "s01m1Oer5IANoyBXQETzSOLWXgWs01m1Oer5bMg5xrTMMxRZ9Pi4fIPeFgIVRZ9PeXL8mPfXQETZGUAN5StRZ9P"
            if sys.version_info >= (3,0,0):
                secret = secret.encode('utf-8')
                md5password = md5password.encode('utf-8')
            hashedpassword = base64.b64encode(hmac.new(secret, md5password, digestmod=hashlib.sha256).digest())
            if sys.version_info >= (3,0,0):
                hashedpassword = hashedpassword.decode('utf-8')
            
            hashedpassword = hashedpassword.replace("/","_").replace("+","-").replace("=","")
            params = (
                    ('grant_type', 'password'),
                    ('device_ts',str(int(time.time()))),
                    ('login', username),
                    ('password', hashedpassword),
                    )

            response = getJson(url='https://api.cda.pl/oauth/token', post=True, params=params)#.json()
            tok = response.get('access_token',None)

            if tok:
                setSetting('acc_token',tok)
                refr = response.get('refresh_token',None)
                setSetting('refr_token',username+'|'+refr)
                profil = getProfile()
                return True,profil
                
            else:
                return '',''
        else:
            usr, refr_token=refr_token.split('|')

            if username == usr:

                refr_token = refr_token.split('|')[-1]
                params = (
                        ('grant_type', 'refresh_token'),
                        ('device_ts',str(int(time.time()))),
                        ('refresh_token', refr_token),)
    
                response = getJson(url='https://api.cda.pl/oauth/token', post=True, params=params)#.json()
                tok = response.get('access_token',None)
                if tok:
                    setSetting('acc_token',tok)
                    refr = response.get('refresh_token',None)
                    setSetting('refr_token',username+'|'+refr)
                    profil = getProfile()
                    return True,profil
                elif 'error' in response:
                    setSetting('refr_token','')
                    return LogowanieCda()
                else:
                    return '',''
            else:
                addon.setSetting('refr_token','')
                return LogowanieCda()
    else:
        return '',''
def getProfile():
    vv=''
    response = getJson(url='https://api.cda.pl/user/me', auth=True)#.json()
    response2 = getJson(url='https://api.cda.pl/user/me/premium', auth=True)#.json()
    login_name = response.get('login',None)
    login_id = response.get('id',None)
    setSetting('login_id',str(login_id))

    status = response2.get('status',None)
    if status.get('premium',None) == 'tak':
        wygasa = status.get('wygasa',None)
        wygasa = wygasa if wygasa else ''

        dod = ' [COLOR gold](premium)[/COLOR]'
        if wygasa:
            dod = ' [COLOR gold](premium) do '+ str(wygasa)+'[/COLOR]'
        if status.get('tv_access',None) != 'false':
            tvaccbas = status.get("tv_access_expire_at",None).get("basic",None)  
            tvaccbas = status.get("tv_access_expire_at",None).get("full",None)  
        login_name = login_name+dod#'|premium do '+ str(wygasa)
    return login_name

argsDict = {}

if __name__ == '__main__':
    log,profil = LogowanieCda()
    if log:
        # /usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/cdaBouquet.py /etc/enigma2/userbouquet.cda.tv 8088 0 y 
        file_name = sys.argv[1]
        streamlinkURL = 'http%%3a//127.0.0.1%%3a%s/' % sys.argv[2]
        frameWork = str(sys.argv[3])
        if frameWork == "0":
            frameWork = "4097"
        
        _generate_E2bouquet(file_name, frameWork, streamlinkURL)
    else:
        print('Nieudane logowanie. Sprawdź login i hasło w ustawieniach wtyczki.')
