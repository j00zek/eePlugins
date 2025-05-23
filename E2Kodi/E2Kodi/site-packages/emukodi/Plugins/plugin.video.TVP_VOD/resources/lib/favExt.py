import os
import sys

from emukodi import xbmc
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmcvfs
import json
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
from .base import b

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
base=b(base_url,addon_handle)

addon = base.addon
PATH_profile=base.PATH_profile

#FAV ext

class favExt:  

    def favExtList(self):
        fURL=PATH_profile+'ulubione_ext.json'
        js=base.openJSON(fURL)
        for j in js:
            URL=j[0]
            if 'play' in URL:
                isPlayable='true'
                isFolder=False
            else:
                isPlayable='false'
                isFolder=True
            
            cmItems=[('[B]Usuń z ulubionych[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=favExtDel&url='+quote(j[0])+')')]
            iL=eval(j[2])
            setArt={'thumb': j[3], 'poster': j[3], 'banner': j[3], 'icon': j[3], 'fanart':''}
            base.addItemList(URL, j[1], setArt, 'video', iL, isFolder, isPlayable, True, cmItems)
        
        xbmcplugin.setContent(addon_handle, 'videos')     
        xbmcplugin.endOfDirectory(addon_handle)

    def favExtDel(self,c):
        fURL=PATH_profile+'ulubione_ext.json'
        js=base.openJSON(fURL)
        for i,j in enumerate(js):
            if  j[0]==c:
                del js[i]
        base.saveJSON(fURL,js)
        xbmc.executebuiltin('Container.Refresh()')

    def favExtAdd(self,u,t,l,i):
        fURL=PATH_profile+'ulubione_ext.json'
        js=base.openJSON(fURL)
        duplTest=False
        for j in js:
            if j[0]==u:
                duplTest=True
        if not duplTest:
            js.append([u,t,l,i])
            xbmcgui.Dialog().notification('TVP VOD', 'Dodano do ulubionych', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('TVP VOD', 'Materiał jest już w ulubionych', xbmcgui.NOTIFICATION_INFO)
        base.saveJSON(fURL,js)
    