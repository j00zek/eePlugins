# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon

from datetime import datetime

from resources.lib.channels import Channels 
from resources.lib.epg import get_live_epg, epg_listitem
from resources.lib.utils import get_url, get_color, get_label_color, plugin_id, get_kodi_version

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def list_live(label):
    addon = xbmcaddon.Addon()
    color = get_color()
    xbmcplugin.setPluginCategory(_handle, label)
    if addon.getSetting('default_tv_view') == 'false':
        xbmcplugin.setContent(_handle, 'tvshows')
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')
    epg, epg_next = get_live_epg()
    kodi_version = get_kodi_version()
    cnt = 0
    for num in sorted(channels_list.keys()):
        cnt += 1
        if addon.getSetting('channel_numbers') == 'číslo kanálu':
            channel_number = str(num) + '. '
        elif addon.getSetting('channel_numbers') == 'pořadové číslo':
            channel_number = str(cnt) + '. '
        else:
            channel_number = ''
        if channels_list[num]['id'] in epg:
            epg_item = epg[channels_list[num]['id']]
            list_item = xbmcgui.ListItem(label = channel_number + channels_list[num]['name'] + ' | ' + get_label_color(epg_item['title'] + ' | ' + datetime.fromtimestamp(epg_item['startts']).strftime('%H:%M') + ' - ' + datetime.fromtimestamp(epg_item['endts']).strftime('%H:%M'), color))
            list_item = epg_listitem(list_item = list_item, epg = epg_item, icon = channels_list[num]['logo'])
            if channels_list[num]['id'] in epg_next:
                epg_next_item = epg_next[channels_list[num]['id']]
                description = epg_item['description'] + '\n\n[COLOR=darkgray]Následuje:\n' + epg_next_item['title'] + ' | ' + datetime.fromtimestamp(epg_next_item['startts']).strftime('%H:%M') + ' - ' + datetime.fromtimestamp(epg_next_item['endts']).strftime('%H:%M') +  '[/COLOR]'
                if kodi_version >= 20:
                    infotag = list_item.getVideoInfoTag()
                    infotag.setPlot(description)
                else:
                    list_item.setInfo('video', {'plot': description})
            menus = []
            menus.append(('Přidat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=add_recording&id=' + str(epg_item['id']) + ')'))
            if epg_item['type'] == 'tvshow':
                menus.append(('Zobrazit epizody', 'Container.Update(plugin://' + plugin_id + '?action=list_tv_episodes&id=' + str(epg_item['referenceid']) + '&label=' + epg_item['title'] + ')'))
            list_item.addContextMenuItems(menus)       
        else:
            epg_item = {}
            list_item = xbmcgui.ListItem(label = channel_number + channels_list[num]['name'])
            list_item.setArt({'thumb': channels_list[num]['logo'], 'icon': channels_list[num]['logo']})    
            list_item.setInfo('video', {'mediatype':'movie', 'title': channels_list[num]['name']}) 
        list_item.setContentLookup(False)          
        list_item.setProperty('IsPlayable', 'true')
        url = get_url(action = 'play_live', id = channels_list[num]['id'], mode = 'start', title = channels_list[num]['name'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)


