# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from datetime import date, datetime, timedelta
import time
import json

from resources.lib.session import Session
from resources.lib.channels import Channels
from resources.lib.categories import page_category_display
from resources.lib.epg import epg_listitem, get_channel_epg
from resources.lib.api import API
from resources.lib.utils import get_url, plugin_id, day_translation, day_translation_short

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def list_recordings(label):
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'tvshows')
    list_item = xbmcgui.ListItem(label='Plánování nahrávek')
    url = get_url(action='list_planning_recordings', label = label + ' / ' + 'Plánování')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    page_category_display(label = 'Nahrávky', params = json.dumps({'schema' : 'PageCategoryDisplayApiAction', 'payload' : {'categoryId' : '8'}}), id = None, show_filter = False)

def delete_recording(id):
    session = Session()
    api = API()
    post = {"payload":{"contentId":id}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.mylist.remove', data = post, session = session) 
    if 'err' in data:
        xbmcgui.Dialog().notification('Oneplay', 'Problém se smazáním nahrávky', xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        xbmcgui.Dialog().notification('Oneplay', 'Nahrávka smazána', xbmcgui.NOTIFICATION_INFO, 5000)
    xbmc.executebuiltin('Container.Refresh')

def list_planning_recordings(label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')
    cnt = 0
    for number in sorted(channels_list.keys()):  
        cnt += 1
        if addon.getSetting('channel_numbers') == 'číslo kanálu':
            channel_number = str(number) + '. '
        elif addon.getSetting('channel_numbers') == 'pořadové číslo':
            channel_number = str(cnt) + '. '
        else:
            channel_number = ''
        list_item = xbmcgui.ListItem(label = channel_number + channels_list[number]['name'])
        list_item.setArt({'thumb': channels_list[number]['logo'], 'icon': channels_list[number]['logo']})
        url = get_url(action='list_rec_days', id = channels_list[number]['id'], label = label + ' / ' + channels_list[number]['name'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)
    
def list_rec_days(id, label):
    xbmcplugin.setPluginCategory(_handle, label)
    for i in range (8):
        day = date.today() + timedelta(days = i)
        if i == 0:
            den_label = 'Dnes'
            den = 'Dnes'
        elif i == 1:
            den_label = 'Zítra'
            den = 'Zítra'
        else:
            den_label = day_translation_short[day.strftime('%w')] + ' ' + day.strftime('%d.%m.')
            den = day_translation[day.strftime('%w')] + ' ' + day.strftime('%d.%m.%Y')
        list_item = xbmcgui.ListItem(label=den)
        url = get_url(action='future_program', id = id, day = i, label = label + ' / ' + den_label)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def future_program(id, day, label):
    addon = xbmcaddon.Addon()
    icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')
    label = label.replace('Nahrávky / Plánování /', '')
    xbmcplugin.setPluginCategory(_handle, label)
    today_date = datetime.today() 
    today_start_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day).timetuple()))
    today_end_ts = today_start_ts + 60*60*24 -1
    if int(day) == 0:
        from_ts = int(time.mktime(datetime.now().timetuple()))
        to_ts = today_end_ts
    else:
        from_ts = today_start_ts + int(day)*60*60*24
        to_ts = today_end_ts + int(day)*60*60*24 
    epg = get_channel_epg(id, from_ts, to_ts)
    if int(day) >  0:
        list_item = xbmcgui.ListItem(label='Předchozí den')
        day_dt = date.today() + timedelta(days = int(day) - 1)
        den_label = day_translation_short[day_dt.strftime('%w')] + ' ' + day_dt.strftime('%d.%m.')
        url = get_url(action='future_program', id = id, day = int(day) - 1, label = label.rsplit(' / ')[0] + ' / ' + den_label)  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'previous_arrow.png'), 'icon' : os.path.join(icons_dir , 'previous_arrow.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    for key in sorted(epg.keys()):
        start = epg[key]['startts']
        end = epg[key]['endts']
        list_item = xbmcgui.ListItem(label = day_translation_short[datetime.fromtimestamp(start).strftime('%w')] + ' ' + datetime.fromtimestamp(start).strftime('%d.%m. %H:%M') + ' - ' + datetime.fromtimestamp(end).strftime('%H:%M') + ' | ' + epg[key]['title'])
        list_item = epg_listitem(list_item, epg[key], '')
        list_item.setProperty('IsPlayable', 'false')
        list_item.addContextMenuItems([])     
        menus = [('Přidat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=add_recording&id=' + str(epg[key]['id']) + ')')]
        list_item.addContextMenuItems(menus)         
        url = get_url(action='add_recording', id = epg[key]['id'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    if int(day) <  7:
        list_item = xbmcgui.ListItem(label='Následující den')
        day_dt = date.today() + timedelta(days = int(day) + 1)
        den_label = day_translation_short[day_dt.strftime('%w')] + ' ' + day_dt.strftime('%d.%m.')
        url = get_url(action='future_program', id = id, day = int(day) + 1, label = label.rsplit(' / ')[0] + ' / ' + den_label)  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'next_arrow.png'), 'icon' : os.path.join(icons_dir , 'next_arrow.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, updateListing = True)

def add_recording(id):
    session = Session()
    api = API()
    post = {"payload":{"contentId":id}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/user.mylist.add', data = post, session = session) 
    if 'err' in data:
        xbmcgui.Dialog().notification('Oneplay', 'Problém s přidáním nahrávky', xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        xbmcgui.Dialog().notification('Oneplay', 'Nahrávka přidána', xbmcgui.NOTIFICATION_INFO, 5000)
    