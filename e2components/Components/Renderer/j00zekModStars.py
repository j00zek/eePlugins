#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng
# v1 07.2020, 11.2021
# recode from lululla 2022
# for channellist
# <widget source="ServiceEvent" render="j00zekModStars" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# or
# <widget source="ServiceEvent" render="j00zekModStars" pixmap="BlackHarmony/icons/starsbar_empty.png" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# edit lululla 05-2022
# <ePixmap pixmap="BlackHarmony/icons/starsbar_empty.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Now" render="j00zekModStars" pixmap="BlackHarmony/icons/starsbar_filled.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="BlackHarmony/icons/stargrey.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Next" render="j00zekModStars" pixmap="BlackHarmony/icons/starsbar_filled.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different package)

from __future__ import absolute_import
from Components.config import config
from Components.Renderer.Renderer import Renderer
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent
from Components.VariableValue import VariableValue
from Components.j00zekComponents import ensure_str, clearCache
from enigma import eSlider
from enigma import eTimer

from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import re
import json
import os
import socket

#omdb_api = "cb1d9f55"
#thetvdbkey = 'D19315B88B2DE21F'
#thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"

def isMountedInRW(path):
    testfile = path + '/tmp-rw-test'
    os.system('touch ' + testfile)
    if os.path.exists(testfile):
        os.system('rm -f ' + testfile)
        return True
    return False


path_folder = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if isMountedInRW("/media/hdd"):
        path_folder = "/media/hdd/poster"
if os.path.exists("/media/usb"):
    if isMountedInRW("/media/usb"):
        path_folder = "/media/usb/poster"
if os.path.exists("/media/mmc"):
    if isMountedInRW("/media/mmc"):
        path_folder = "/media/mmc/poster"
if not os.path.exists(path_folder):
    os.makedirs(path_folder)


REGEX = re.compile(
        r'([\(\[]).*?([\)\]])|'
        r'(: odc.\d+)|'
        r'(\d+: odc.\d+)|'
        r'(\d+ odc.\d+)|(:)|'
        r'( -(.*?).*)|(,)|'
        r'!|'
        r'/.*|'
        r'\|\s[0-9]+\+|'
        r'[0-9]+\+|'
        r'\s\*\d{4}\Z|'
        r'([\(\[\|].*?[\)\]\|])|'
        r'(\"|\"\.|\"\,|\.)\s.+|'
        r'\"|:|'
        r'Премьера\.\s|'
        r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
        r'(х|Х|м|М|т|Т|д|Д)/с\s|'
        r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
        r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
        r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)

class j00zekModStars(VariableValue, Renderer):
    def __init__(self):
        if not self.intCheck():
            return
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.__start = 0
        self.__end = 100
        self.text = ''
        self.timer30 = eTimer()
        self.tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
        self.formatImg = 'w185'
        try:
            self.lng = str(config.osd.language.value[:-3])
        except:
            self.lng = 'en'
        print('[j00zekModStars] self.lng =', self.lng)


    GUI_WIDGET = eSlider

    def intCheck(self):
        try:
            socket.setdefaulttimeout(0.5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except:
            return False

    def checkRedirect(self, url):
        # print("*** check redirect ***")
        import requests
        from requests.adapters import HTTPAdapter, Retry
        hdr = {"User-Agent": "Enigma2 - Enigma2 Plugin"}
        content = None
        retries = Retry(total=1, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retries)
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        try:
            r = http.get(url, headers=hdr, timeout=(10, 30), verify=False)
            r.raise_for_status()
            if r.status_code == requests.codes.ok:
                try:
                    content = r.json()
                except Exception as e:
                    print('[j00zekModStars] checkRedirect error:', e)
            # return content
        except Exception as e:
            print('[j00zekModStars] next ret: ', e)
        return content

    def convtext(self, text=''):
        def remove_accents(string):
            string = re.sub(u"[àáâãäå]", 'a', string)
            string = re.sub(u"[èéêë]", 'e', string)
            string = re.sub(u"[ìíîï]", 'i', string)
            string = re.sub(u"[òóôõö]", 'o', string)
            string = re.sub(u"[ùúûü]", 'u', string)
            string = re.sub(u"[ýÿ]", 'y', string)
            return string

        try:
            if text != '' or text is not None or text != 'None':
                print('[j00zekModStars] original text: ', text)
                text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')
                text = text.lower()
                text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('primatv', '').replace('1^tv', '')
                text = text.replace('prima visione', '').replace('1^ tv', '').replace('((', '(').replace('))', ')')
                if 'studio aperto' in text:
                    text = 'studio aperto'
                if 'josephine ange gardien' in text:
                    text = 'josephine ange gardien'
                if 'elementary' in text:
                    text = 'elementary'
                if 'squadra speciale cobra 11' in text:
                    text = 'squadra speciale cobra 11'
                if 'criminal minds' in text:
                    text = 'criminal minds'
                if 'i delitti del barlume' in text:
                    text = 'i delitti del barlume'
                if 'senza traccia' in text:
                    text = 'senza traccia'
                if 'hudson e rex' in text:
                    text = 'hudson e rex'
                if 'ben-hur' in text:
                    text = 'ben-hur'
                if text.endswith("the"):
                    text.rsplit(" ", 1)[0]
                    text = text.rsplit(" ", 1)[0]
                    text = "the " + str(text)
                text = text + 'FIN'
                if re.search(r'[Ss][0-9][Ee][0-9]+.*?FIN', text):
                    text = re.sub(r'[Ss][0-9][Ee][0-9]+.*?FIN', '', text)
                if re.search(r'[Ss][0-9] [Ee][0-9]+.*?FIN', text):
                    text = re.sub(r'[Ss][0-9] [Ee][0-9]+.*?FIN', '', text)
                text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
                text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
                text = re.sub(r'(\d+)+.*?FIN', '', text)
                text = text.partition("(")[0] + 'FIN'  # .strip()
                # text = re.sub("\s\d+", "", text)
                text = text.partition("(")[0]  # .strip()
                text = text.partition(":")[0]  # .strip()
                text = text.partition(" -")[0]  # .strip()
                text = re.sub(' - +.+?FIN', '', text)  # all episodes and series ????
                text = re.sub('FIN', '', text)
                text = re.sub(r'^\|[\w\-\|]*\|', '', text)
                text = re.sub(r"[-,?!/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
                text = ensure_str(text)
                text = remove_accents(text)
                text = text.strip()
                text = text.capitalize()
                print('[j00zekModStars] Final text: ', text)
            else:
                text = text
            return text
        except Exception as e:
            print('[j00zekModStars] convtext error: ', e)

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            # print('[j00zekModStars] event A what[0] == self.CHANGED_CLEAR')
            (self.range, self.value) = ((0, 1), 0)
            return
        if what[0] != self.CHANGED_CLEAR:
            print('[j00zekModStars] event B what[0] != self.CHANGED_CLEAR')
            if self.instance:
                self.instance.hide()
            # try:
                # self.timer30.callback.append(self.infos)
            # except:
                # self.timer30_conn = self.timer30.timeout.connect(self.infos)
            # self.timer30.start(50, True)
            self.infos()

    def fromAzmanEPG(self):
        #>>>utilize azman scores. ;)
        self.extDescr = str(self.event.getExtendedDescription()).strip()
        print('[j00zekModStars] self.extDescr:', self.extDescr)
        rtng = 0
        try:
            if 'FilmWeb:' in self.extDescr:
                rtng = self.extDescr.split('FilmWeb:')[1].split('/')[0].strip()
                rtng = int(10 * (float(rtng)))
            elif 'IMDB:' in self.extDescr:
                rtng = self.extDescr.split('IMDB:')[1].split('/')[0].strip()
                rtng = int(10 * (float(rtng)))
        except Exception as e:
            print('[j00zekModStars] Exception in fromAzmanEPG', e)
        if rtng > 0:
            print('[j00zekModStars] fromAzmanEPG, rtng=', rtng)
            (self.range, self.value) = ((0, 100), rtng)
            self.instance.show()
            return True
        print('[j00zekModStars] fromAzmanEPG, no rating found :(')
        return False

    def infos(self):
        try:
            rtng = 0
            range = 0
            value = 0
            ImdbRating = "0"
            ids = None
            data = ''
            self.event = self.source.event
            if self.event and self.event != 'None' or self.event is not None:  # and self.instance:
                self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                self.evntNm = self.convtext(self.evnt)
                if self.fromAzmanEPG():
                    return
                dwn_infos = "{}/{}".format(path_folder, self.evntNm)
                if not os.path.exists(dwn_infos):
                    clearCache()
                    '''
                    try:
                        url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(self.tmdb_api, self.evntNm)
                        url = url.encode()
                        url = self.checkRedirect(url)
                        print('[j00zekModStars] url1:', url)
                        ids = url['results'][0]['id']
                        print('[j00zekModStars] url1 ids:', ids)
                    except:
                    '''
                    try:
                        url = 'http://api.themoviedb.org/3/search/multi?api_key={}&query={}'.format(self.tmdb_api, self.evntNm)
                        url = url.encode()
                        url = self.checkRedirect(url)
                        print('[j00zekModStars] url2:', url)
                        if url is not None:
                            ids = url['results'][0]['id']
                            print('[j00zekModStars] url2 ids:', ids)
                    # except Exception as e:
                        # print('[j00zekModStars] Exception no ids in zstar ', e)
                            if ids and ids is not None or ids != '':
                                try:
                                    data = 'https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), self.tmdb_api, self.lng)  # &language=" + str(language)
                                    data = ensure_str(data)
                                    print('[j00zekModStars] pass ids Else: ')
                                    if data:
                                        data = json.load(urlopen(data))
                                        open(dwn_infos, "w").write(json.dumps(data))
                                    else:
                                        data = 'https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=credits&language={}'.format(str(ids), self.tmdb_api, self.lng)  # &language=" + str(language)
                                        data = ensure_str(data)
                                        print('[j00zekModStars] pass ids Else: ')
                                        if data:
                                            data = json.load(urlopen(data))
                                            open(dwn_infos, "w").write(json.dumps(data))

                                except Exception as e:
                                    print('[j00zekModStars] pass Exception:', e)
                    except Exception as e:
                        print('[j00zekModStars] Exception no ids ', e)
                if os.path.exists(dwn_infos):
                    try:
                        with open(dwn_infos) as f:
                            data = json.load(f)
                        ImdbRating = ''
                        if "vote_average" in data:
                            ImdbRating = data['vote_average']
                        elif "imdbRating" in data:
                            ImdbRating = data['imdbRating']
                        else:
                            ImdbRating = '0'
                        print('[j00zekModStars] ImdbRating: ', ImdbRating)
                        if ImdbRating and ImdbRating != '0':
                            rtng = int(10 * (float(ImdbRating)))
                        else:
                            rtng = 0
                        range = 100
                        value = rtng
                        (self.range, self.value) = ((0, range), value)
                        self.instance.show()
                    except Exception as e:
                        print('[j00zekModStars] ImdbRating Exception: ', e)
        except Exception as e:
            print('[j00zekModStars] passImdbRating: ', e)

    def postWidgetCreate(self, instance):
        instance.setRange(self.__start, self.__end)

    def setRange(self, range):
        (self.__start, self.__end) = range
        if self.instance is not None:
            self.instance.setRange(self.__start, self.__end)

    def getRange(self):
        return self.__start, self.__end

    range = property(getRange, setRange)
