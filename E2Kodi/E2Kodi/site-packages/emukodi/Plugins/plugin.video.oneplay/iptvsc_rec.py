# -*- coding: utf-8 -*-

import xbmc
from resources.lib.utils import plugin_id, parsedatetime

path = xbmc.getInfoLabel('ListItem.FileNameAndPath')
channel = xbmc.getInfoLabel('ListItem.ChannelName')
startdatetime = parsedatetime(xbmc.getInfoLabel('ListItem.Date'), xbmc.getInfoLabel('ListItem.StartDate'))
xbmc.executebuiltin('RunPlugin("plugin://' + plugin_id +'?action=iptv_sc_rec&channel=' + str(channel) + '&startdatetime=' + startdatetime + '")')
