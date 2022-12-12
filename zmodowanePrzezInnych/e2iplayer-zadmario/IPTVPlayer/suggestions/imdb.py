# -*- coding: utf-8 -*-
#
# seems not used  to DELETE import urllib
try:
    import json
except Exception:
    import simplejson as json

from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc

from Plugins.Extensions.IPTVPlayer.p2p3.manipulateStrings import ensure_str


class SuggestionsProvider:

    def __init__(self):
        self.cm = common()

    def getName(self):
        return _("IMDb Suggestions")

    def getSuggestions(self, text, locale):
        text = text.decode('ascii', 'ignore').encode('ascii').lower()
        if len(text) > 2:
            text = text.replace(' ', '_')
            url = 'http://v2.sg.media-imdb.com/suggests/titles/%s/%s.json' % (text[0], text)
            sts, data = self.cm.getPage(url)
            if sts:
                retList = []
                data = data[data.find('(') + 1:data.rfind(')')]
                printDBG(data)
                data = json.loads(data)['d']
                for item in data:
                    retList.append(ensure_str(item['l']))
                return retList
        return None
