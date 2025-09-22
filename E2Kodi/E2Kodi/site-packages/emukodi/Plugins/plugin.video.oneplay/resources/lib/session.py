# -*- coding: utf-8 -*-
import sys
import xbmcaddon
import xbmcgui

import json
import time 

from resources.lib.api import API
from resources.lib.profiles import get_profile_id, get_account_id, reset_profiles

class Session:
    def __init__(self):
        self.valid_to = -1
        self.load_session()

    def create_session(self):
        self.get_token()
        self.save_session()

    def enable_service(self, serviceid):
        for service in self.services:
            if serviceid == service:
                self.services[service]['enabled'] = 1
            else:
                self.services[service]['enabled'] = 0
        self.save_session()

    def get_token(self):
        addon = xbmcaddon.Addon()
        api = API()
        post = {"payload":{"command":{"schema":"LoginWithCredentialsCommand","email":addon.getSetting('username'),"password":addon.getSetting('password')}}}
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.login.step', data = post, sensitive = True)
        if 'err' in data or 'step' not in data or ('bearerToken' not in data['step'] and data['step']['schema'] != 'ShowAccountChooserStep'):
            xbmcgui.Dialog().notification('Oneplay','Problém při přihlášení', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
        if data['step']['schema'] == 'ShowAccountChooserStep':
            accounts = {}
            accounts_ext = {}
            accounts_data = []
            authToken = data['step']['authToken']
            for account in data['step']['accounts']:
                account_name = account['name'] + '|' + account['extId']
                accounts.update({account['name'] : account['accountId']})
                accounts_ext.update({account_name : account['accountId']})
                accounts_data.append(account_name)
            account = get_account_id(accounts_data)
            if '|' in account:
                accounts = accounts_ext
            post = {"payload":{"command":{"schema":"LoginWithAccountCommand","accountId":accounts[account],"authCode":authToken}}}
            data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.login.step', data = post)   
            if 'err' in data or 'step' not in data or 'bearerToken' not in data['step']:
                xbmcgui.Dialog().notification('Oneplay','Problém při přihlášení', xbmcgui.NOTIFICATION_ERROR, 5000)
                sys.exit()            
        self.token = data['step']['bearerToken']
        deviceId = data['step']['currentUser']['currentDevice']['id']
        post = {"payload":{"id":deviceId,"name":addon.getSetting('deviceid')}}
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.device.change', data = post, session = self)
        post = {"payload":{"screen":"devices"}}
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/setting.display', data = post, session = self)
        if 'err' in data or 'screen' not in data or 'userDevices' not in data['screen']:
            xbmcgui.Dialog().notification('Oneplay','Problém při přihlášení', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
        for device in data['screen']['userDevices']['devices']:
            if device['id'] != deviceId and device['name'] == addon.getSetting('deviceid'):
                post = {"payload":{"criteria":{"schema":"UserDeviceIdCriteria","id":device['id']}}}
                data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.device.remove', data = post, session = self)
        self.save_session()
        profileId = get_profile_id()
        if len(str(addon.getSetting('profile_pin'))) > 0:
            post = {"payload":{"profileId":profileId},"authorization":[{"schema":"PinRequestAuthorization","pin":str(addon.getSetting('profile_pin')),"type":"profile"}]}
        else:
            post = {"payload":{"profileId":profileId}}
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.profile.select', data = post, session = self)
        if 'err' in data or 'bearerToken' not in data:
            reset_profiles()
            profileId = get_profile_id()
            if len(str(addon.getSetting('profile_pin'))) > 0:
                post = {"payload":{"profileId":profileId},"authorization":[{"schema":"PinRequestAuthorization","pin":str(addon.getSetting('profile_pin')),"type":"profile"}]}
            else:
                post = {"payload":{"profileId":profileId}}
            data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.profile.select', data = post, session = self)            
            if 'err' in data or 'bearerToken' not in data:
                xbmcgui.Dialog().notification('Oneplay','Problém při přihlášení', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
        self.token = data['bearerToken']

    def load_session(self):
        from resources.lib.settings import Settings
        settings = Settings()
        data = settings.load_json_data({'filename' : 'session.txt', 'description' : 'session'})
        self.services = None
        if data is not None:
            data = json.loads(data)
            if 'valid_to' in data and 'token' in data:
                if int(data['valid_to']) < int(time.time()):
                    self.create_session()
                else:
                    self.token = data['token']
            else:
                self.create_session()
        else:
            self.create_session()

    def save_session(self):
        from resources.lib.settings import Settings
        settings = Settings()
        data = json.dumps({'token' : self.token, 'valid_to' : int(time.time() + 60*60*24)})        
        settings.save_json_data({'filename' : 'session.txt', 'description' : 'session'}, data)

    def remove_session(self):
        from resources.lib.settings import Settings
        settings = Settings()
        settings.reset_json_data({'filename' : 'session.txt', 'description' : 'session'})
        self.valid_to = -1
        self.create_session()
        xbmcgui.Dialog().notification('Oneplay', 'Byla vytvořená nová session', xbmcgui.NOTIFICATION_INFO, 5000)
