# -*- coding: utf-8 -*-
import logging

from streamlink.plugin import Plugin
from streamlink.plugin.plugin import parse_url_params
from streamlink.stream import HTTPStream
from streamlink.utils import update_scheme

from streamlink.e2config import getE2config

log = logging.getLogger(__name__)

import sys
import re
import time

from xml.etree import cElementTree as ET

sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/')
#examples:
#Polsat Sport HD
#http://root:root@192.168.1.8/web/zap?sRef=1:0:1:C1D:1E78:71:820000:0:0:0/http://192.168.1.8:8001/1:0:1:C1D:1E78:71:820000:0:0:0
#TVN Turbo HD
#http://root:root@192.168.1.8/web/zap?sRef=1:0:1:3DD0:640:13E:820000:0:0:0/http://192.168.1.8:8001/1:0:1:3DD0:640:13E:820000:0:0:0

class remoteE2(Plugin):
    _url_re = re.compile(r"http://(.+)/web/zap.sRef=(.+)|.+800[12]/.+")
 
    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        if not '/web/zap' in self.url:
            log.info('URL to stream channel only, zapping not needed')
            return {"live": HTTPStream(self.session, self.url)}
        
        url, params = parse_url_params(self.url) 
        zapURL        = self.url.split('/http://')[0]
        streamURL     = 'http://' + self.url.split('/http://')[1]
        mainURL       = zapURL.split('/web/zap')[0]
        #https://dream.reichholf.net/wiki/Enigma2:WebInterface
        
        log.debug("URL={0}; params={1}", url, params) 
        log.debug("zapURL: %s" % zapURL)
        log.debug("streamURL: %s" % streamURL)
        #sprawdzenie stanu tunera
        response = self.session.http.get(mainURL + '/web/powerstate')
        log.debug(response.text)
        if response.status_code != 200:
            return
        root = ET.fromstring(response.text)
        #budzenie tunera
        if root.tag == 'e2powerstate' and root[0].tag == 'e2instandby' and root[0].text.strip() == 'true':
            log.info('Tuner is sleeping, waking it up')
            response = self.session.http.get(mainURL + '/web/powerstate?newstate=4')
            log.info(response.text)
            if response.status_code != 200:
                log.info("ERROR waking up tuner")
                return
        #zap na kanal
        currChannel = 'unknown'
        response = self.session.http.get(mainURL + '/web/subservices')
        log.info(response.text)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            for child in root[0]:
                if child.tag == 'e2servicereference':
                    currChannel = child.text.strip()
                    if currChannel[-1:] == ':':
                        currChannel = currChannel[:-1]
                    break
        else:
            return
        if currChannel in zapURL and currChannel != 'unknown':
            log.info('Tuner already on correct channel (%s), zapping not needed' % currChannel)
        else:
            log.info('Zapping from %s to %s' % (currChannel,zapURL.split('Ref=')[1]))
            response = self.session.http.get(zapURL)
            if response.status_code == 200:
                log.debug("Successful ZAP to '%s'" % zapURL)
            else:
                log.info("ERROR ZAPPING to '%s'\n\t Response: %s" % (zapURL,response.status_code))
                return
        #wylaczenie tunera?
        #strumieniowanie
        time.sleep(1)
        return {"live": HTTPStream(self.session, streamURL, **params)} 

__plugin__ = remoteE2