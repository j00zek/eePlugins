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

from resources.lib.epg import epg_listitem
from resources.lib.categories import Item, get_seasons, get_episodes
from resources.lib.utils import get_url, plugin_id, get_color, get_label_color

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def add_favourite(type, id, image, title):  
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'favourites.txt')
    favourites = get_favourites()
    if type not in favourites or id not in favourites[type]:
        if type not in favourites:
            favourites.update({ type : {id : {'image' : image, 'title' : title}}})
        else:
            favourites[type].update({id : {'image' : image, 'title' : title}})
        try:
            with codecs.open(filename, 'w', encoding='utf-8') as file:
                file.write('%s\n' % json.dumps(favourites))        
        except IOError as error:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení oblíbených pořadů', xbmcgui.NOTIFICATION_ERROR, 5000)            
        xbmcgui.Dialog().notification('Oneplay', 'Pořad byl přidaný do oblíbených', xbmcgui.NOTIFICATION_INFO, 5000)
    else:
        xbmcgui.Dialog().notification('Oneplay', 'Pořad je již v oblíbených', xbmcgui.NOTIFICATION_ERROR, 5000)

def remove_favourite(type, id):
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'favourites.txt')
    favourites = get_favourites()
    del favourites[type][id]
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % json.dumps(favourites))        
    except IOError:
        xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení oblíbených pořadů', xbmcgui.NOTIFICATION_ERROR, 5000)            
    xbmc.executebuiltin('Container.Refresh')

def get_favourites():
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'favourites.txt')
    data = None
    try:
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            for row in file:
                data = row[:-1]
    except IOError as error:
        if error.errno != 2:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při načtení oblíbených pořadů', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
    if data is not None:
        favourites = json.loads(data)
    else:
        favourites = {}
    return favourites

def list_favourites(label):
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'movies')
    types = ['category', 'show', 'season', 'item']
    favourites = get_favourites()
    for type in types:
            if type in favourites.keys():
                for id in favourites[type]:
                    item = favourites[type][id]
                    if type == 'show':
                        Item(label = item['title'], title = item['title'], type = type, schema = 'ApiAppAction', call = 'page_content_display', params = {'schema': 'PageContentDisplayApiAction', 'payload': {'contentId': id}, 'contentType': 'show'}, tracking = None, data = {'title' : item['title'], 'cover' : item['image'], 'favourite_type' : type, 'favourite_id' : id})
                    elif type == 'item':
                        Item(label = item['title'], title = item['title'], type = type, schema = 'ApiAppAction', call = 'page_content_display', params = {'schema': 'PageContentDisplayApiAction', 'payload': {'contentId': id}, 'contentType': id.split('.')[0]}, tracking = None, data = {'title' : item['title'], 'cover' : item['image'], 'favourite_type' : type, 'favourite_id' : id})
                    elif type == 'season':
                        split_id = id.split('~')
                        item_id = split_id[0]
                        caruselId = split_id[1]
                        Item(label = item['title'], title = item['title'], type = type, schema = 'CarouselGenericFilter', call = 'carousel_display', params = {'payload': {'carouselId': caruselId, 'criteria': {'filterCriterias': item_id, 'sortOption': 'DESC'}}}, tracking = None, data = {'favourite_type' : type, 'favourite_id' : id})
                    elif type == 'category':
                        split_id = id.split('~')
                        item_id = split_id[0]
                        caruselId = split_id[1]
                        criteria = split_id[2]
                        if criteria == 'None':
                            Item(label = item['title'], title = item['title'], type = 'category_item', schema = 'CarouselBlock', call = 'page_category_display', params = {'schema': 'PageCategoryDisplayApiAction', 'payload': {'categoryId': item_id}}, tracking = {'id': caruselId, 'title': item['title'], 'recommended': False, 'recoGroupId': ''}, data = {'favourite_type' : type, 'favourite_id' : id})                            
                        else:
                            Item(label = item['title'], title = item['title'], type = 'category_item', schema = 'ApiAppAction', call = 'page_category_display', params = {'schema': 'PageCategoryDisplayApiAction', 'payload': {'categoryId': item_id, 'criteria': {'filterCriterias': criteria}}}, tracking = {'id': caruselId, 'title': item['title'], 'recommended': False, 'recoGroupId': ''}, data = {'favourite_type' : type, 'favourite_id' : id})
    xbmcplugin.endOfDirectory(_handle)        

def list_favourites_new(label):
    addon = xbmcaddon.Addon()
    color = get_color()
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'movies')
    limit = int(addon.getSetting('favourites_new_count'))
    types = ['show', 'season']
    seasons = []
    favourites = get_favourites()
    blacklist = get_favourites_episodes_bl()
    for type in types:
            if type in favourites.keys():
                for id in favourites[type]:
                    item = favourites[type][id]
                    if type == 'show':
                        seasons_items = get_seasons(id)
                        for season in seasons_items:
                            seasons.append({'title' : item['title'] + ' / ' + season['title'], 'id': season['id'], 'carouselId': season['carouselId']})
                    if type == 'season':
                        split_id = id.split('~')
                        id = split_id[0]
                        caruselId = split_id[1]
                        season_item = {'title' : item['title'], 'id' : id, 'carouselId' : caruselId}
                        if season_item not in seasons:
                            seasons.append(season_item)
    episodes = {}
    if addon.getSetting('episodes_order') == 'sestupně':
        reverse = True
    else:
        reverse = False
    for season in seasons:
        episodes.update(get_episodes(season['carouselId'], season['id'], season['title'], limit))

    for episodeId in sorted(episodes.keys(), reverse = reverse):
        item = episodes[episodeId]
        if item['id'] not in blacklist:
            if '\n' not in item['title']:
                item['title'] = item['title'] + '\n' + get_label_color(item['showtitle'], color)
            list_item = xbmcgui.ListItem(label = item['title'])            
            list_item = epg_listitem(list_item, item, None)
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')
            menus = [('Skrýt epizodu', 'RunPlugin(plugin://' + plugin_id + '?action=add_favourites_episodes_bl&id=' + item['id'] + ')')]
            list_item.addContextMenuItems(menus)       
            url = get_url(action = 'play_archive', id = item['id'])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)  

def add_favourites_episodes_bl(id):  
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'favourites_episodes_bl.txt')
    blacklist = get_favourites_episodes_bl()
    blacklist.append(id)
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % json.dumps(blacklist))        
    except IOError as error:
        xbmcgui.Dialog().notification('Oneplay', 'Chyba při uložení skrytých epizod oblíbených pořadů', xbmcgui.NOTIFICATION_ERROR, 5000)            
    xbmc.executebuiltin('Container.Refresh')
    
def get_favourites_episodes_bl():
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'favourites_episodes_bl.txt')
    data = None
    try:
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            for row in file:
                data = row[:-1]
    except IOError as error:
        if error.errno != 2:
            xbmcgui.Dialog().notification('Oneplay', 'Chyba při čtení skrytých epizod oblíbených pořadů', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()
    if data is not None:
        blacklist = json.loads(data)
    else:
        blacklist = []
    return blacklist