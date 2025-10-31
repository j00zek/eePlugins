# -*- coding: utf-8 -*-
import os
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon

from datetime import date, datetime, timedelta
import time

from resources.lib.utils import get_url, day_translation, day_translation_short, plugin_id
from resources.lib.channels import Channels 
from resources.lib.epg import get_channel_epg, epg_listitem

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def list_archive(label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')
    cnt = 0
    for number in sorted(channels_list.keys()):  
        if channels_list[number]['liveOnly'] == False:
            cnt += 1
            if addon.getSetting('channel_numbers') == 'číslo kanálu':
                channel_number = str(number) + '. '
            elif addon.getSetting('channel_numbers') == 'pořadové číslo':
                channel_number = str(cnt) + '. '
            else:
                channel_number = ''
            list_item = xbmcgui.ListItem(label = channel_number + channels_list[number]['name'])
            list_item.setArt({'thumb': channels_list[number]['logo'], 'icon': channels_list[number]['logo']})
            url = get_url(action='list_archive_days', id = channels_list[number]['id'], label = label + ' / ' + channels_list[number]['name'])  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_archive_days(id, label):
    xbmcplugin.setPluginCategory(_handle, label)
    for i in range (8):
        day = date.today() - timedelta(days = i)
        if i == 0:
            den_label = 'Dnes'
            den = 'Dnes'
        elif i == 1:
            den_label = 'Včera'
            den = 'Včera'
        else:
            den_label = day_translation_short[day.strftime('%w')] + ' ' + day.strftime('%d.%m.')
            den = day_translation[day.strftime('%w')] + ' ' + day.strftime('%d.%m.%Y')
        list_item = xbmcgui.ListItem(label = den)
        url = get_url(action='list_program', id = id, day_min = i, label = label + ' / ' + den_label)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_program(id, day_min, label):
    addon = xbmcaddon.Addon()
    icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')
    label = label.replace('Archiv /','')
    xbmcplugin.setPluginCategory(_handle, label)
    if addon.getSetting('default_tv_view') == 'false':
        xbmcplugin.setContent(_handle, 'tvshows')
    today_date = datetime.today() 
    today_start_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day) .timetuple()))
    today_end_ts = today_start_ts + 60*60*24 -1
    if int(day_min) == 0:
        from_ts = today_start_ts - int(day_min)*60*60*24
        to_ts = int(time.mktime(datetime.now().timetuple()))
    else:
        from_ts = today_start_ts - int(day_min)*60*60*24
        to_ts = today_end_ts - int(day_min)*60*60*24
    epg = get_channel_epg(id, from_ts, to_ts)

    if int(day_min) < 7:
        list_item = xbmcgui.ListItem(label='Předchozí den')
        day = date.today() - timedelta(days = int(day_min) + 1)
        den_label = day_translation_short[day.strftime('%w')] + ' ' + day.strftime('%d.%m.')
        url = get_url(action='list_program', id = id, day_min = int(day_min) + 1, label = label.rsplit(' / ')[0] + ' / ' + den_label)
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'previous_arrow.png'), 'icon' : os.path.join(icons_dir , 'previous_arrow.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    for key in sorted(epg.keys(), reverse = False):
        if int(epg[key]['endts']) > int(time.mktime(datetime.now().timetuple()))-60*60*24*7:
            list_item = xbmcgui.ListItem(label = day_translation_short[datetime.fromtimestamp(epg[key]['startts']).strftime('%w')] + ' ' + datetime.fromtimestamp(epg[key]['startts']).strftime('%d.%m. %H:%M') + ' - ' + datetime.fromtimestamp(epg[key]['endts']).strftime('%H:%M') + ' | ' + epg[key]['title'])
            list_item = epg_listitem(list_item = list_item, epg = epg[key], icon = None)
            menus = []
            menus.append(('Přidat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=add_recording&id=' + str(epg[key]['id']) + ')'))
            if epg[key]['type'] == 'tvshow':
                menus.append(('Zobrazit epizody', 'Container.Update(plugin://' + plugin_id + '?action=list_tv_episodes&id=' + str(epg[key]['referenceid']) + '&label=' + epg[key]['title'] + ')'))
            list_item.addContextMenuItems(menus)       
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')
            if epg[key]['endts'] > int(time.mktime(datetime.now().timetuple()))-10:
                 url = get_url(action = 'play_live', id = id, mode = 'start')
            else:
                url = get_url(action='play_archive', id = epg[key]['id'])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

    if int(day_min) > 0:
        list_item = xbmcgui.ListItem(label='Následující den')
        day = date.today() - timedelta(days = int(day_min) - 1)
        den_label = day_translation_short[day.strftime('%w')] + ' ' + day.strftime('%d.%m.')
        url = get_url(action='list_program', id = id, day_min = int(day_min) - 1, label = label.rsplit(' / ')[0] + ' / ' + den_label)  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'next_arrow.png'), 'icon' : os.path.join(icons_dir , 'next_arrow.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle, updateListing = True, cacheToDisc = False)