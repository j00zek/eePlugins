#!//usr/bin/python
# -*- coding: utf-8 -*-
#
########## plugin by mbebe licensed under GNU GENERAL PUBLIC LICENSE. Version 2, June 1991 ##########
# changes for emukodi j00zek in a nutshell stop using routing module

from resources.lib.sweettv import * #SweetTV
from emukodi import xbmc
from emukodi import xbmcaddon
from urllib.parse import parse_qsl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon('plugin.video.sweettvpl')

if __name__ == '__main__':
    #SweetTV()
    exlink = params.get('url')
    mode = params.get('mode')
    name = 'plugin.video.sweettvpl'
    xbmc.log('sweettvpl ENTER: mode=%r, name=%r, exlink=%r' % (mode, name, exlink), xbmc.LOGWARNING)
    CreateDatas()
    if mode == 'loginTV':
        loginTV()
    elif mode == 'logout':
        logout()
    elif mode == 'listM3U':
        listM3U()
    elif mode == 'refreshToken':
        refreshToken()
    elif mode == 'playtvs':
        playvid(exlink + '|null')
