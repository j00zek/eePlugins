# -*- coding: utf-8 -*-
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
try:
    from xbmcvfs import translatePath
except ImportError:
    from xbmc import translatePath

import codecs
import json

from resources.lib.api import API
from resources.lib.utils import get_url

_url = sys.argv[0]

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def list_profiles(label):
    xbmcplugin.setPluginCategory(_handle, label)
    profiles = get_profiles()
    for profile in profiles:
        if profile['active'] == True:
            list_item = xbmcgui.ListItem(label = '[B]' + profile['name'] + '[/B]')
        else:
            list_item = xbmcgui.ListItem(label = profile['name'])
        list_item.setArt({'thumb' : profile['image'], 'icon' : profile['image']})
        url = get_url(action='set_active_profile', id = profile['id'])  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    list_item = xbmcgui.ListItem(label = 'Načtení profilů')
    url = get_url(action='reset_profiles')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle)        

def set_active_profile(id):
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'profiles.txt')
    profiles = get_profiles()
    for profile in profiles:
        if profile['id'] ==  id:
            profile['active'] = True
        else:
            profile['active'] = False
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % json.dumps(profiles))        
    except IOError as error:
        xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení profilů', xbmcgui.NOTIFICATION_ERROR, 5000)            
    xbmc.executebuiltin('Container.Refresh')

def get_profiles(active = False):
    from resources.lib.session import Session
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'profiles.txt')
    profiles = []
    data = None
    try:
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            for row in file:
                data = row[:-1]
    except IOError as error:
        if error.errno != 2:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při načtení profilů', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
    if data is not None:
        profiles = json.loads(data)
    else:
        api = API()
        session = Session()
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.profiles.display', data = None, session = session)
        if 'err' in data or 'availableProfiles' not in data or 'profiles' not in data['availableProfiles']:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při načtení profilů', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
        is_active = True
        for profile in data['availableProfiles']['profiles']:
            profiles.append({'id' : profile['profile']['id'], 'name' : profile['profile']['name'], 'image' : profile['profile']['avatarUrl'], 'active' : is_active})
            is_active = False
        try:
            with codecs.open(filename, 'w', encoding='utf-8') as file:
                file.write('%s\n' % json.dumps(profiles))        
        except IOError as error:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení profilů', xbmcgui.NOTIFICATION_ERROR, 5000)        
            sys.exit()
    if active == True:
        for profile in profiles:
            if profile['active'] == True:
                return profile
        return None
    else:
        return profiles

def get_profile_id():
    profile = get_profiles(active = True)
    return profile['id']

def reset_profiles(load_profiles = True):
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'profiles.txt')
    if os.path.exists(filename):
        try:
            os.remove(filename) 
        except IOError:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při znovunačtení profilů', xbmcgui.NOTIFICATION_ERROR, 5000)
    if load_profiles == True:
        get_profiles()
        xbmcgui.Dialog().notification('Oneplay', 'Profily byly znovu načtené', xbmcgui.NOTIFICATION_INFO, 5000)    
        xbmc.executebuiltin('Container.Refresh')

def list_accounts(label):
    xbmcplugin.setPluginCategory(_handle, label)
    accounts = get_accounts()
    for account in accounts:
        if account['active'] == True:
            list_item = xbmcgui.ListItem(label = '[B]' + account['name'] + '[/B]')
        else:
            list_item = xbmcgui.ListItem(label = account['name'])
        url = get_url(action='set_active_account', name = account['name'])  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    list_item = xbmcgui.ListItem(label = 'Načtení účtů')
    url = get_url(action='reset_accounts')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle)  

def set_active_account(name):
    from resources.lib.session import Session
    from resources.lib.channels import Channels
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'accounts.txt')
    accounts = get_accounts()
    for account in accounts:
        if account['name'] ==  name:
            account['active'] = True
        else:
            account['active'] = False
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % json.dumps(accounts))        
    except IOError as error:
        xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení účtů', xbmcgui.NOTIFICATION_ERROR, 5000)   
    reset_profiles(load_profiles = False)
    session = Session()
    session.remove_session()
    channels = Channels()
    channels.reset_channels_full()
    xbmc.executebuiltin('Container.Refresh')

def get_accounts(active = False, accounts_data = None):
    addon = xbmcaddon.Addon()    
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'accounts.txt')
    accounts = []
    data = None
    try:
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            for row in file:
                data = row[:-1]
    except IOError as error:
        if error.errno != 2:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při načtení účtů', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
    if data is not None:
        accounts = json.loads(data)
    elif accounts_data is not None:
        is_active = True
        for account in accounts_data:
            accounts.append({'name' : account, 'active' : is_active})
            is_active = False
        try:
            with codecs.open(filename, 'w', encoding='utf-8') as file:
                file.write('%s\n' % json.dumps(accounts))        
        except IOError as error:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení účtů', xbmcgui.NOTIFICATION_ERROR, 5000)        
            sys.exit()
    if active == True:
        for account in accounts:
            if account['active'] == True:
                return account
        return None
    else:
        return accounts

def get_account_id(accounts_data = None):
    account = get_accounts(active = True, accounts_data = accounts_data)
    return account['name']

def reset_accounts():
    from resources.lib.session import Session
    from resources.lib.channels import Channels
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'accounts.txt')
    if os.path.exists(filename):
        try:
            os.remove(filename) 
        except IOError:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při znovunačtení účtů', xbmcgui.NOTIFICATION_ERROR, 5000)
    reset_profiles(load_profiles = False)
    session = Session()
    session.remove_session()
    channels = Channels()
    channels.reset_channels_full()
    xbmcgui.Dialog().notification('Oneplay', 'Účty byly znovu načtené', xbmcgui.NOTIFICATION_INFO, 5000)    
  
