# -*- coding: utf-8 -*-
#
from Plugins.Extensions.IPTVPlayerMario.p2p3.UrlLib import urllib_quote
try:
    import json
except Exception:
    import simplejson as json

from Plugins.Extensions.IPTVPlayerMario.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayerMario.libs.pCommon import common
from Plugins.Extensions.IPTVPlayerMario.tools.iptvtools import printDBG, printExc

from Plugins.Extensions.IPTVPlayerMario.p2p3.manipulateStrings import ensure_str


class SuggestionsProvider:

    def __init__(self):
        self.cm = common()

    def getName(self):
        return _("Filmweb Suggestions")

    def getSuggestions(self, text, locale):
        url = 'https://www.filmweb.pl/api/v1/live/search?query=' + urllib_quote(text).lower()
        sts, data = self.cm.getPage(url)
        if sts:
            retList = []
#            printDBG(data)
            data = json.loads(data)['searchHits']
            for item in data:
                if item.get('matchedName', '') == '':
                    retList.append(ensure_str(item['matchedTitle']))
                else:
                    retList.append(ensure_str(item['matchedName']))
            return retList
        return None
