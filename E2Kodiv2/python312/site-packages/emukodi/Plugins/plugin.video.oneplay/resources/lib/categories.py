# -*- coding: utf-8 -*-
import sys
import os
import xbmcplugin
import xbmcgui
import xbmcaddon

import json 
import time
from datetime import datetime

from resources.lib.session import Session
from resources.lib.api import API
from resources.lib.epg import get_item_detail, epg_listitem
from resources.lib.utils import get_url, plugin_id, get_color, get_label_color
from resources.lib.stream import play_stream


if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def item_data(item):
    color = get_color()
    title = item['title']
    if 'tracking' in item and 'type' in item['tracking']:
        type = item['tracking']['type']
    else:
        type = 'item'
    subtitle = ''
    if 'subTitle' in item:
        subtitle = item['subTitle']
    if 'additionalFragments' in item and len(item['additionalFragments']) > 0 and 'labels' in item['additionalFragments'][0]:
        for label in item['labels']:
            if 'Vyprší' not in label['name'] and 'Můj seznam' not in label['name']:
                if len(subtitle) > 0:
                    subtitle += ' | ' + label['name']
                else:
                    subtitle = label['name']
        has_date = False
        for label in item['additionalFragments'][0]['labels']:
            if label['name'].count('.') == 2:
                has_date = True
                if len(subtitle) > 0:
                    subtitle += ' | ' + label['name']
                else:
                    subtitle = label['name']
            elif ':' in label['name']:
                if len(subtitle) > 0:
                    if has_date == True:
                        subtitle += ' ' + label['name']
                    else:
                        subtitle += ' | ' + label['name']
                else:
                    subtitle = label['name']
            elif 'Díl' in label['name']:
                if len(subtitle) > 0:
                    subtitle += ' | ' + label['name']
                else:
                    subtitle = label['name']
    if len(subtitle) > 1:
        title = item['title'] + '\n' + get_label_color(subtitle, color)
    image = item['image'].replace('{WIDTH}', '320').replace('{HEIGHT}', '480')
    if 'description' in item:
        description = item['description']
    else:
        description = ''
    item_data = {'title' : title, 'type' : type, 'cover' : image, 'poster' : image, 'description' : description}
    if 'tracking' in item and 'show' in item['tracking']:
        item_data['showtitle'] = item['tracking']['show']['title'] + ' / ' + item['tracking']['season']
    return item_data

def get_episodes(carouselId, id, season_title, limit = 1000):
    session = Session()
    api = API()
    get_page = True
    page = 1
    cnt = 0
    episodes = {}
    filterCriterias = id
    while get_page == True:
        post = {"payload":{"carouselId":carouselId,"paging":{"count":12,"position":12*(page-1)+1},"criteria":{"filterCriterias":filterCriterias,"sortOption":"DESC"}}}
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/carousel.display', data = post, session = session)
        if not 'err' in data and 'carousel' in data:
            for item in data['carousel']['tiles']:
                if 'params' in item['action'] and ('contentId' in item['action']['params']['payload'] or 'contentId' in item['action']['params']['payload']['criteria']):
                    cnt += 1
                    contentId = get_contentId(item['action']['params'])
                    episodeId = int(contentId.split('.')[1])
                    if id not in episodes:
                        item = item_data(item)
                        episodes.update({episodeId : {'id' : contentId, 'type' : item['type'], 'showtitle' : season_title, 'title' : item['title'], 'cover' : item['cover'], 'poster' : item['cover'], 'description' : item['description']}})
                    if cnt >= limit:
                        get_page = False
                        break
            if data['carousel']['paging']['next'] == True:
                page = page + 1
            else:
                get_page = False
        else:
            get_page = False
    return episodes

def get_seasons(id):
    session = Session()
    api = API()
    post = {'payload' : {'contentId' : id}}
    seasons = []
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/page.content.display', data = post, session = session)
    for block in data['layout']['blocks']:
        if block['schema'] == 'TabBlock' and block['template'] == 'tabs':
            for tab in block['tabs']:
                if tab['label']['name'] == 'Celé díly':
                    if tab['isActive'] == True:
                        data = block
                    else:
                        post = {"payload":{"tabId":tab['id']}}
                        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/tab.display', data = post, session = session)
    for block in data['layout']['blocks']:
        if block['schema'] == 'CarouselBlock' and block['template'] in ['list','grid']:
            for carousel in block['carousels']:
                if 'criteria' in carousel:
                    for criteria in carousel['criteria']:
                        if criteria['schema'] == 'CarouselGenericFilter' and criteria['template'] == 'showSeason':
                            first = True
                            season_item = None
                            for season in criteria['items']:   
                                season_item = {'title' : season['label'], 'id' : season['criteria'], 'carouselId' : carousel['id']}
                                if first == True and '.' in season['label'] and season['label'].split('.')[0] != '1':
                                    break
                                first = False
                            seasons.append(season_item)
    return seasons

def get_contentId(params):
    if 'contentId' in params['payload']:
        return params['payload']['contentId']
    else:
        return params['payload']['criteria']['contentId']

def remote_favourite_menu(data):
     return ('Odebrat z oblíbených Oneplay', 'RunPlugin(plugin://' + plugin_id + '?action=remove_favourite&type=' + data['favourite_type'] + '&id=' + data['favourite_id'] + ')')

def add_favourite_menu(type, id, image, title):
     return ('Přidat do oblíbených Oneplay', 'RunPlugin(plugin://' + plugin_id + '?action=add_favourite&type=' + type + '&id=' + id + '&image=' + image + '&title=' + title + ')')

class Item:
    def __init__(self, label, title, type, schema, call, params, tracking, data):
        self.label = label
        self.title = title
        self.type = type
        self.schema = schema
        self.call = call
        self.params = params
        self.tracking = tracking
        self.data = data
        func = getattr(self, self.schema)
        func()

    def ApiAppAction(self):
        self.call = self.call.replace('.', '_')
        if 'payload' in self.params and self.params and 'contentId' in self.params['payload']:
            item = get_item_detail(self.params['payload']['contentId'], True, self.data)
        elif self.data is not None:
            item = self.data
        else:
            item = {}
        list_item = xbmcgui.ListItem(label = self.title)
        if 'schema' in self.params and (self.params['schema'] == 'ContentPlayApiAction' or (self.params['schema'] == 'PageContentDisplayApiAction' and self.params['contentType'] in ['movie', 'epgitem'])):
            list_item = epg_listitem(list_item, item, None)
            url = get_url(action = self.call, params = json.dumps(self.params), label = self.title)
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')
            menus = []
            if self.data is not None and 'recording' in self.data and self.data['recording'] == True:
                menus.append(('Smazat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=delete_recording&id=' + get_contentId(self.params) + ')'))
            elif self.params is not None and 'payload' in self.params:
                if 'contentType' in self.params and self.params['contentType'] == 'epgitem':
                    menus.append(('Přidat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=add_recording&id=' + self.params['payload']['contentId'] + ')'))
                elif 'deeplink' in self.params['payload'] and 'epgItem' in self.params['payload']['deeplink']:
                    menus.append(('Přidat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=add_recording&id=' + self.params['payload']['deeplink']['epgItem'] + ')'))
            if self.type in ['movie','epgitem','match','highlight']:
                if self.data is not None and 'favourite_id' in self.data:
                    menus.append(remote_favourite_menu(self.data))
                else:
                    contentId = get_contentId(self.params)
                    menus.append(add_favourite_menu('item', contentId, self.data['cover'], self.title))
            if len(menus) > 0:
                list_item.addContextMenuItems(menus)       
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        else:
            if self.params['schema'] == 'PageContentDisplayApiAction' and self.params['contentType'] not in ['competition']:
                list_item = epg_listitem(list_item, item, None)
            url = get_url(action = self.call, params = json.dumps(self.params), label = self.label)
            if self.type in ['show', 'category_item', 'criteria_item']:
                menus = []
                if self.data is not None and 'recording' in self.data and self.data['recording'] == True:
                    menus.append(('Smazat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=delete_recording&id=' + get_contentId(self.params) + ')'))
                elif self.type in ['show'] and 'deeplink' in self.params['payload'] and 'epgItem' in self.params['payload']['deeplink']:
                        menus.append(('Přidat nahrávku', 'RunPlugin(plugin://' + plugin_id + '?action=add_recording&id=' + self.params['payload']['deeplink']['epgItem'] + ')'))
                if self.data is not None and 'favourite_id' in self.data:
                    menus.append(remote_favourite_menu(self.data))
                else:
                    if self.type == 'show':
                        menus.append(add_favourite_menu('show', self.params['payload']['contentId'], self.data['cover'], self.title))
                    elif self.type == 'category_item' and 'payload' in self.params:
                        if 'criteria' in self.params['payload']:
                            criteria = self.params['payload']['criteria']['filterCriterias']
                        else:
                            criteria = None
                        menus.append(add_favourite_menu('category', self.params['payload']['categoryId'] + '~' + self.tracking['id'] + '~' + str(criteria), 'None', self.label.replace('Kategorie / ','')))
                if len(menus) > 0:
                    list_item.addContextMenuItems(menus)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    def CarouselBlock(self):
        list_item = xbmcgui.ListItem(label = self.title)
        url = get_url(action = 'page_category_display', params = json.dumps(self.params), id = self.tracking['id'], show_filter = False, label = self.label)
        if self.type in ['category_item']:
            menus = []
            if self.data is not None and 'favourite_id' in self.data:
                menus.append(remote_favourite_menu(self.data))
            else:
                if 'criteria' in self.params['payload']:
                    criteria = self.params['payload']['criteria']['filterCriterias']
                else:
                    criteria = None
                menus.append(add_favourite_menu('category', self.params['payload']['categoryId'] + '~' + self.tracking['id'] + '~' + str(criteria), 'None', self.label.replace('Kategorie / ','')))
            if len(menus) > 0:
                list_item.addContextMenuItems(menus)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    def CarouselGenericFilter(self):
        list_item = xbmcgui.ListItem(label = self.title)
        url = get_url(action = self.call, params = json.dumps(self.params), label = self.label)
        if self.data is not None and 'image' in self.data:
            list_item.setArt({ 'thumb' : self.data['image'], 'icon' : self.data['image'] })
        if self.type == 'season':
            menus = []
            if self.data is not None and 'favourite_id' in self.data:
                menus.append(remote_favourite_menu(self.data))
            else:
                menus.append(add_favourite_menu('season', self.params['payload']['criteria']['filterCriterias'] + '~' + self.params['payload']['carouselId'], 'None', self.label))
            if len(menus) > 0:
                list_item.addContextMenuItems(menus)       
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    def SubMenu(self):
        list_item = xbmcgui.ListItem(label = self.title)
        url = get_url(action = self.call, params = json.dumps(self.params), id = self.data['id'], show_filter = True, label = self.label)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

def CarouselBlock(label, block, params, id):
    addon = xbmcaddon.Addon()
    color = get_color()
    for carousel in block['carousels']:
        if 'paging' in carousel and 'next' in carousel['paging'] and carousel['paging']['next'] == True:
            paging = True
        else:
            paging = False
        if params['schema'] == 'PageCategoryDisplayApiAction' and id is None and block['template'] != 'contentFilter' and 'myList' not in block['template'] and 'search' not in block['template']:
            title = carousel['tracking']['title']
            if 'showMore' in carousel:
                item = carousel['showMore']
                Item(label = label + ' / ' + title , title = title, type = 'category_item', schema = item['action']['schema'], call = item['action']['call'], params = item['action']['params'], tracking = carousel['tracking'], data = None)
            else:
                Item(label = label + ' / ' + title, title = title, type = 'category_item', schema = block['schema'], call = None, params = params, tracking = carousel['tracking'], data = None)
        else:
            if params['schema'] == 'PageContentDisplayApiAction' and 'criteria' in carousel and carousel['criteria'][0]['schema'] == 'CarouselGenericFilter':
                carouselId = carousel['id']
                for item in carousel['criteria'][0]['items']:
                    if 'additionalText' in item:
                        title = item['label'] + ' (' + item['additionalText'] + ')'
                    else:
                        title = item['label']
                    if addon.getSetting('episodes_order') == 'sestupně':
                        order = 'DESC'
                    else:
                        order = 'ASC'
                    Item(label = label + ' / ' + item['label'], title = title, type = 'season', schema = carousel['criteria'][0]['schema'], call = 'carousel_display', params = {'payload' : {'carouselId' : carouselId, 'criteria' : {'filterCriterias' : item['criteria'], 'sortOption' : order}}}, tracking = None, data = None)
            elif 'tiles' in carousel:
                if id is None or id == carousel['tracking']['id'] or id == block['id']:
                    if paging == True and 'pageCount' not in carousel['paging']:
                        carousel_display(label, json.dumps({'payload' : {'carouselId' : carousel['id']}}))
                    else:
                        for item in carousel['tiles']:
                            if item['action']['schema'] != 'NoAppAction':
                                exp_info = ''
                                if params['schema'] == 'PageCategoryDisplayApiAction' and 'payload' in params and 'categoryId' in params['payload'] and params['payload']['categoryId'] == '8' and 'additionalFragments' in item:
                                    year = datetime.now().year
                                    expiration = int(time.mktime(time.strptime(item['additionalFragments'][0]['labels'][0]['name'] + str(year) + ' ' + item['additionalFragments'][0]['labels'][1]['name'], '%d.%m.%Y %H:%M'))) + 30*24*60*60
                                    exp_info = get_label_color(' (do ' + datetime.fromtimestamp(expiration).strftime('%d.%m').lstrip("0").replace(" 0", " ") + ')', color)
                                if 'params' in item['action'] and 'contentType' in item['action']['params']:
                                    item_type = item['action']['params']['contentType']
                                else:
                                    item_type = 'other'
                                itemdata = item_data(item)
                                if 'payload' in params and 'categoryId' in params['payload'] and params['payload']['categoryId'] == '8':
                                    itemdata['recording'] = True
                                Item(label = item['title'], title = item_data(item)['title'] + exp_info, type = item_type, schema = item['action']['schema'], call = item['action']['call'], params = item['action']['params'], tracking = None, data = itemdata)
                        if paging == True:
                            addon = xbmcaddon.Addon()
                            icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')
                            pageCount = carousel['paging']['pageCount']
                            count = len(carousel['tiles'])
                            page = 2
                            carouselId = carousel['id']
                            image = os.path.join(icons_dir , 'next_arrow.png')
                            Item(label = label, title = 'Následující strana (' + str(page) + '/' + str(pageCount) + ')', type = 'arrow', schema = carousel['criteria'][0]['schema'], call = 'carousel_display', params = {'payload' : {'carouselId' : carouselId, 'criteria' : block['carousels'][0]['paging']['criteria'], 'paging' : {'count' : count, 'position' : count * (page - 1) + 1}}}, tracking = None, data = {'image' : image})

def TabBlock(label, block, params):
    for block in block['layout']['blocks']:
        CarouselBlock(label, block, params, None)

def BreadcrumbBlock(label, block, params, id, show_filter):
    for item in block['menu']['groups'][0]['items']:
        if item['schema'] == 'SubMenu':
            if show_filter == False or show_filter == 'False':
                Item(label = label, title = item['title'], type = 'criteria', schema = item['schema'], call = 'page_category_display', params = params, tracking = None, data = {'id' : id})
            else:
                for filter in item['groups'][0]['items']:
                    Item(label = label + ' / ' + filter['title'], title = filter['title'], type = 'criteria_item', schema = filter['action']['schema'], call = filter['action']['call'], params = filter['action']['params'], tracking = None, data = None)
        
def page_category_display(label, params, id, show_filter):
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'movies')
    params = json.loads(params)
    session = Session()
    api = API()
    post = {'payload' : params['payload']}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/page.category.display', data = post, session = session) 
    if 'err' not in data:
        for block in data['layout']['blocks']:
            if block['schema'] == 'BreadcrumbBlock':
                BreadcrumbBlock(label, block, params, id, show_filter)
            if block['schema'] == 'TabBlock':                
                TabBlock(label, block, params)
            if block['schema'] == 'CarouselBlock' and (show_filter == False or show_filter == 'False'):
                CarouselBlock(label, block, params, id)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)    

def page_content_display(label, params):
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'movies')
    params = json.loads(params)
    session = Session()
    api = API()
    post = {'payload' : params['payload']}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/page.content.display', data = post, session = session)
    if 'err' not in data:
        if data['tracking']['type'] in ['movie', 'epgitem']:
            params = None
            for block in data['layout']['blocks']:
                if block['schema'] == 'ContentHeaderBlock':
                    params = block['mainAction']['action']['params']
            if params is None:
                params = {'payload' : {'criteria' : {'schema' : 'ContentCriteria', 'contentId' : data['tracking']['id']}}}
            content_play(json.dumps(params))
        else:
            list = True
            switch_tab = False
            for block in data['layout']['blocks']:
                if block['schema'] == 'TabBlock':
                    for tab in block['tabs']:
                        if tab['label']['name'] == 'Celé díly':
                            if tab['isActive'] == False:
                                post = {"payload":{"tabId":tab['id']}}
                                data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/tab.display', data = post, session = session)
                                for block in data['layout']['blocks']:
                                    CarouselBlock(label, block, params, None)
                                switch_tab = True
            if switch_tab == False:
                for block in data['layout']['blocks']:
                    if block['schema'] == 'CarouselBlock':
                        if block['header']['title'] == 'Celé díly':
                            list = False
                            CarouselBlock(label, block, params, None)
                        elif block['header']['title'] == 'Vysílané v TV':
                            list = False
                            CarouselBlock(label, block, params, None)
                        if list == True:                
                            CarouselBlock(label, block, params, None)
                    if block['schema'] == 'TabBlock':
                        list = False
                        TabBlock(label, block, params)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)    

def carousel_display(label, params):
    xbmcplugin.setPluginCategory(_handle, label)
    xbmcplugin.setContent(_handle, 'movies')
    params = json.loads(params)
    get_page = True
    page = 1
    session = Session()
    api = API()
    post = {'payload' : params['payload']}
    while get_page == True:
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/carousel.display', data = post, session = session)
        if 'err' not in data:
            if data['carousel']['paging']['next'] == True and 'pageCount' in data['carousel']['paging']:
                pageCount = data['carousel']['paging']['pageCount']
                count = len(data['carousel']['tiles'])
                if 'paging' in post['payload']:
                    position = post['payload']['paging']['position']
                    page = int((position - 1) / count + 1 - 1)
                else:
                    page = 0
                if 'criteria' in data['carousel']['paging'] and page > 0:
                    carouselId = data['carousel']['id']
                    addon = xbmcaddon.Addon()
                    icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')
                    image = os.path.join(icons_dir , 'previous_arrow.png')
                    Item(label = label, title = 'Předchozí strana (' + str(page) + '/' + str(pageCount) + ')',type = 'arrow', schema = 'CarouselGenericFilter', call = 'carousel_display', params = {'payload' : {'carouselId' : carouselId, 'criteria' : data['carousel']['paging']['criteria'], 'paging' : {'count' : count, 'position' : count * (page - 1) + 1}}}, tracking = None, data = {'image' : image})                    

            for item in data['carousel']['tiles']:
                if 'call' in item['action']:
                    itemdata = item_data(item)
                    if 'payload' in params and 'carouselId' in params['payload'] and 'page:8;' in params['payload']['carouselId']:
                        itemdata['recording'] = True
                    Item(label = item['title'], title = item_data(item)['title'], type = item['tracking']['type'], schema = item['action']['schema'], call = item['action']['call'], params = item['action']['params'], tracking = None, data = itemdata)

            if data['carousel']['paging']['next'] == True:
                if 'pageCount' in data['carousel']['paging']:
                    if 'paging' in post['payload']:
                        position = post['payload']['paging']['position']
                        page = int((position - 1) / count + 1 + 1)
                    else:
                        page = 2
                    if 'criteria' in data['carousel']['paging'] and page <= pageCount:
                        carouselId = data['carousel']['id']
                        addon = xbmcaddon.Addon()
                        icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')
                        image = os.path.join(icons_dir , 'previous_arrow.png')
                        Item(label = label, title = 'Následující strana (' + str(page) + '/' + str(pageCount) + ')', type = 'arrow', schema = 'CarouselGenericFilter', call = 'carousel_display', params = {'payload' : {'carouselId' : carouselId, 'criteria' : data['carousel']['paging']['criteria'], 'paging' : {'count' : count, 'position' : count * (page - 1) + 1}}}, tracking = None, data = {'image' : image})                    
                        get_page = False
                else:
                    count = len(data['carousel']['tiles'])
                    page = page + 1
                    post['payload']['paging'] = {'count' : count, 'position' : count * (page - 1) + 1}
            else:
                get_page = False
        else:
            get_page = False                
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)       

def content_play(params):
    params = json.loads(params)
    contentId = get_contentId(params)
    if 'channel,' in contentId:
        contentId = contentId.replace('channel.', '')
        mode = 'start'
    else:
        mode = 'archive'
    play_stream(contentId, mode)

def page_search_display(query):
    session = Session()
    api = API()    
    post = {"payload":{"query":query}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/page.search.display', data = post, session = session)  
    if 'err' not in data:
        if 'blocks' in data['layout']:
            for block in data['layout']['blocks']:
                if block['schema'] == 'CarouselBlock':
                    CarouselBlock('', block, {'schema' : 'PageCategoryDisplayApiAction'}, None)
        else:
            xbmcgui.Dialog().notification('Oneplay','Nic nenalezeno', xbmcgui.NOTIFICATION_INFO, 3000)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)              

def list_categories(label):
    xbmcplugin.setPluginCategory(_handle, label)
    session = Session()
    api = API()
    post = {"payload":{"reason":"start"}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/app.init', data = post, session = session) 
    if 'err' in data or not 'menu' in data:
        xbmcgui.Dialog().notification('Oneplay','Problém při načtení kategorií', xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        for group in data['menu']['groups']:
            if group['position'] == 'top':
                for item in group['items']:
                    if item['action']['call'] == 'page.category.display':
                        Item(label = item['title'], title = item['title'], type = 'category_menu', schema = item['action']['schema'], call = item['action']['call'], params = item['action']['params'], tracking = None, data = None)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)    
