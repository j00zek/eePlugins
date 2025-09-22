# -*- coding: utf-8 -*-
import sys

import xbmcgui
import xbmcaddon
import xbmcvfs

from datetime import datetime, timezone
import time

from resources.lib.channels import Channels
from resources.lib.utils import plugin_id, replace_by_html_entity
from resources.lib.epg import get_day_epg, get_channel_epg
from resources.lib.recordings import add_recording

tz_offset = int(datetime.now(timezone.utc).astimezone().utcoffset().total_seconds() / 3600)

def save_file_test():
    addon = xbmcaddon.Addon()  
    try:
        content = ''
        output_dir = addon.getSetting('output_dir')      
        test_file = output_dir + 'test.fil'
        file = xbmcvfs.File(test_file, 'w')
        file.write(bytearray(('test').encode('utf-8')))
        file.close()
        file = xbmcvfs.File(test_file, 'r')
        content = file.read()
        if len(content) > 0 and content == 'test':
            file.close()
            xbmcvfs.delete(test_file)
            return 1  
        file.close()
        xbmcvfs.delete(test_file)
        return 0
    except Exception:
        file.close()
        xbmcvfs.delete(test_file)
        return 0 

def generate_playlist(output_file = ''):
    addon = xbmcaddon.Addon()
    if addon.getSetting('output_dir') is None or len(addon.getSetting('output_dir')) == 0:
        xbmcgui.Dialog().notification('Oneplay', 'Nastav adresář pro playlist a EPG!', xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit() 
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')
    if save_file_test() == 0:
        xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení playlistu', xbmcgui.NOTIFICATION_ERROR, 5000)
        return
    output_dir = addon.getSetting('output_dir') 
    try:
        if len(output_file) > 0:
            file = xbmcvfs.File(output_file, 'w')
        else:
            if addon.getSetting('playlist_filename') == 'playlist.m3u':
                file = xbmcvfs.File(output_dir + 'playlist.m3u', 'w')
            else:
                file = xbmcvfs.File(output_dir + 'playlist.txt', 'w')
        if file == None:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení playlistu', xbmcgui.NOTIFICATION_ERROR, 5000)
        else:
            file.write(bytearray(('#EXTM3U\n').encode('utf-8')))
            for number in sorted(channels_list.keys()):  
                logo = channels_list[number]['logo']
                if logo is None:
                    logo = ''
                if channels_list[number]['liveOnly'] == True:
                    line = '#EXTINF:-1 tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']
                elif addon.getSetting('catchup_mode') == 'default':
                    line = '#EXTINF:-1 catchup="default" catchup-days="7" catchup-source="plugin://' + plugin_id + '/?action=iptsc_play_stream&id=' + str(channels_list[number]['id']) + '&catchup_start_ts={utc}&catchup_end_ts={utcend}" tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']
                else:
                    line = '#EXTINF:-1 catchup="append" catchup-days="7" catchup-source="&catchup_start_ts={utc}&catchup_end_ts={utcend}" tvg-chno="' + str(number) + '" tvg-id="' + channels_list[number]['name'] + '" tvh-epg="0" tvg-logo="' + logo + '",' + channels_list[number]['name']
                file.write(bytearray((line + '\n').encode('utf-8')))
                line = 'plugin://' + plugin_id + '/?action=iptsc_play_stream&id=' + str(channels_list[number]['id'])
                if channels_list[number]['liveOnly'] == False:
                    file.write(bytearray(('#KODIPROP:inputstream=inputstream.ffmpegdirect\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:inputstream.ffmpegdirect.stream_mode=timeshift\n').encode('utf-8')))
                    file.write(bytearray(('#KODIPROP:inputstream.ffmpegdirect.is_realtime_stream=true\n').encode('utf-8')))
                file.write(bytearray(('#KODIPROP:mimetype=video/mp2t\n').encode('utf-8')))
                file.write(bytearray((line + '\n').encode('utf-8')))
            file.close()
            xbmcgui.Dialog().notification('Oneplay', 'Playlist byl uložený', xbmcgui.NOTIFICATION_INFO, 5000)    
    except Exception:
        file.close()
        xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení playlistu', xbmcgui.NOTIFICATION_ERROR, 5000)

def generate_epg(output_file = '', show_progress = True):
    addon = xbmcaddon.Addon()
    channels = Channels()
    channels_list = channels.get_channels_list('channel_number')
    channels_list_by_id = channels.get_channels_list('id')
    if len(channels_list) > 0:
        if save_file_test() == 0:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení EPG', xbmcgui.NOTIFICATION_ERROR, 5000)
            return
        output_dir = addon.getSetting('output_dir') 
        try:
            if len(output_file) > 0:
                file = xbmcvfs.File(output_file, 'w')
            else:
                file = xbmcvfs.File(output_dir + 'oneplay_epg.xml', 'w')
            if file == None:
                xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení EPG', xbmcgui.NOTIFICATION_ERROR, 5000)
            else:
                file.write(bytearray(('<?xml version="1.0" encoding="UTF-8"?>\n').encode('utf-8')))
                file.write(bytearray(('<tv generator-info-name="EPG grabber">\n').encode('utf-8')))
                content = ''
                for number in sorted(channels_list.keys()):
                    logo = channels_list[number]['logo']
                    if logo is None:
                        logo = ''
                    channel = channels_list[number]['name']
                    content = content + '    <channel id="' + replace_by_html_entity(channel) + '">\n'
                    content = content + '            <display-name lang="cs">' +  replace_by_html_entity(channel) + '</display-name>\n'
                    content = content + '            <icon src="' + logo + '" />\n'
                    content = content + '    </channel>\n'
                file.write(bytearray((content).encode('utf-8')))
                today_date = datetime.today() 
                today_start_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day) .timetuple()))
                today_end_ts = today_start_ts + 60*60*24 - 1
                if show_progress == True:
                    dialog = xbmcgui.DialogProgressBG()
                    dialog.create('Stahování EPG dat')
                i = 0
                for day in range(int(addon.getSetting('epg_from'))*-1, int(addon.getSetting('epg_to')), 1):
                    i = i + 1
                    if show_progress == True:
                        dialog.update(int(i/(int(addon.getSetting('epg_from'))+int(addon.getSetting('epg_to'))+1)*100))
                    cnt = 0
                    content = ''
                    epg = get_day_epg(today_start_ts + day*60*60*24, today_end_ts + day*60*60*24)
                    for ts in sorted(epg.keys()):
                        epg_item = epg[ts]
                        if epg_item['channel_id'] in channels_list_by_id:
                            starttime = datetime.fromtimestamp(epg_item['startts']).strftime('%Y%m%d%H%M%S')
                            endtime = datetime.fromtimestamp(epg_item['endts']).strftime('%Y%m%d%H%M%S')
                            content = content + '    <programme start="' + starttime + ' +0' + str(tz_offset) + '00" stop="' + endtime + ' +0' + str(tz_offset) + '00" channel="' +  replace_by_html_entity(channels_list_by_id[epg_item['channel_id']]['name']) + '">\n'
                            content = content + '       <title lang="cs">' +  replace_by_html_entity(epg_item['title']) + '</title>\n'
                            if epg_item['description'] != None and len(epg_item['description']) > 0:
                                content = content + '       <desc lang="cs">' +  replace_by_html_entity(epg_item['description']) + '</desc>\n'
                            content = content + '       <icon src="' + epg_item['poster'] + '"/>\n'
                            content = content + '    </programme>\n'
                            cnt = cnt + 1
                            if cnt > 20:
                                file.write(bytearray((content).encode('utf-8')))
                                content = ''
                                cnt = 0
                    file.write(bytearray((content).encode('utf-8')))                          
                file.write(bytearray(('</tv>\n').encode('utf-8')))
                file.close()
                if show_progress == True:
                    dialog.close()
                if show_progress == True or addon.getSetting('epg_info') == 'true':
                    xbmcgui.Dialog().notification('Oneplay', 'EPG bylo uložené', xbmcgui.NOTIFICATION_INFO, 5000)    
        except Exception:
            file.close()
            if show_progress == True:
                dialog.close()
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při generování EPG!', xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        xbmcgui.Dialog().notification('Oneplay', 'Nevrácena žádná data!', xbmcgui.NOTIFICATION_ERROR, 5000)

def iptv_sc_rec(channelName, startdatetime):
    channels = Channels()
    channels_list = channels.get_channels_list('name', visible_filter = False)
    from_ts = int(time.mktime(time.strptime(startdatetime, '%d.%m.%Y %H:%M')))
    epg = get_channel_epg(channel_id = channels_list[channelName]['id'], from_ts = from_ts  - 7200, to_ts = from_ts + 60*60*12)
    if len(epg) > 0 and from_ts in epg:
        add_recording(epg[from_ts]['id'])
    else:
        xbmcgui.Dialog().notification('Oneplay', 'Pořad v Oneplay nenalezen! Používáte EPG z doplňku Oneplay?', xbmcgui.NOTIFICATION_ERROR, 10000)
