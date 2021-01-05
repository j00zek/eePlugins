#!/usr/bin/python
# -*- coding: utf-8 -*- 
#######################################################################
#
#    download and analyzes wather data from MSN
#    Coded by j00zek (c)2018
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem skryptu
#    Please respect my work and don't delete/change name of the script author
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#     
#######################################################################

iconsMap={
    'lekkideszczzesniegiem' :   '6.png',
    "slabeopadydeszczu"     :   '9.png',
    'opadydeszczu'          :   '11.png',
    'deszcz'                :   '11.png',
    "niewielkieopadysniegu" :   '13.png', 
    'snieg'                 :   '16.png',
    "zachmurzeniecalkowite" :   '26.png',
    'zachmurzenieduze'      :   '28.png',
    'zachmurzeniemale'      :   '29.png',
    'czesciowoslonecznie'   :   '30.png',
    'bezchmurnie'           :   '31.png',
    'slonecznie'            :   '32.png',
    'przewaznieslonecznie'  :   '34.png',
    'burze'                 :   '35.png',
    'silneburze'            :   '37.png',
    #EN
    "rainshowers"           :   '9.png',
    'lightrain'             :   '11.png',
    'rain'                  :   '11.png',
    'cloudy'                :   '26.png',
    'sunny'                 :   '32.png',
    'mostlysunny'           :   '34.png',
    #DE
    'leichterregenundschnee':   '6.png',
    'leichterregen'         :   '9.png',
    'regenschauer'          :   '11.png',
    'regen'                 :   '11.png',
    'schnee'                :   '16.png',
    "bewoelkt"              :   '26.png',
    "meistbewoelkt"         :   '28.png',
    "teilweisebewoelkt"     :   '29.png',
    'teilweisesonnig'       :   '30.png',
    'sonnig'                :   '32.png',
    'ueberwiegendsonnig'    :   '34.png',
    'gewitter'              :   '35.png',
    }

def utfTOansi(text):
    text = text.replace(" ","").replace("Ś","s").replace("ś","s").replace("ł","l").strip()
    text = text.replace("ę","e").replace("ć","c").replace("ó","o").strip().replace("ż","z").strip()
    text = text.replace("ö","oe").replace("Ü","Ue")
    return text.lower()
  
def decodeHTML(text):
    text = text.replace('&#176;','°').replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace('&#228;','ä').replace('&#196;','Ä').replace('&#246;','ö').replace('&#214;','Ö').replace('&#252;','ü').replace('&#220;','Ü').replace('&#223;','ß')
    return text

import re, os
# instantiate the parser and fed it some HTML
def getWeather(webContent, DBGnow = False, DBGhourly = False, DBGdaily = False, reportMissingIcons = True):
    webContent = decodeHTML(webContent)
    def findInContent( WC, reFindString ):
        retTxt = ''
        FC = re.findall(reFindString, WC, re.S)
        if FC:
            for i in FC:
                retTxt += i
        return retTxt
    def getList( retList, WC, reFindString ):
        FC = re.findall(reFindString, WC, re.S)
        if FC:
            for i in FC:
                retList.append(i)
        return retList
    #report missing icons
    reportMissingIcons = True
    missingIcons = ''
    if reportMissingIcons and os.path.exists("/tmp/MSNWeatherMissingMappings.log"):
        missingIcons = open("/tmp/MSNWeatherMissingMappings.log", "r").read()
        #open("/tmp/MSNWeatherMissingMappings.log", "w").write('')
    #now
    nowContent = findInContent(webContent, '<div class="weather-info">(.*?)</div>')
    nowDict = {}
    nowDict['title'] = getList([], nowContent, '<span>(.*?)</span>.*<ul>')
    nowDict['nowData']  = getList([], nowContent, '<li><span>(.*?)</span>(.*?)</li>')
    if DBGnow:
        print '---------------------------------- nowContent ----------------------\n'
        print nowContent
        print '---------------------------------- nowDict ----------------------\n'
        print nowDict
        print nowDict['title'][0]
    # >>>>> hourly <<<<<
    hourlyContent = findInContent(webContent, '<div class="dailydetails" >(.*?)</ul>')
    hourlyDict = {}
    hourlyDict['title'] = getList([], hourlyContent, '<h2 id="hourlymsg">[\n ]*(.*?)[\n ]*<span>(.*?)</span>[\n ]*<span>(.*?)</span>')
    id = 0
    Lines = getList([], hourlyContent, '<li>(.*?)</li>')
    for Line in Lines:
        #print Line
        hourlyDict['Record=%s' % id] = getList([], Line, 'class="time">(.*?)<.*alt="(.*?)".*src="(.*?)".*class="temp">(.*?)<.*class="precipicn"><span>(.*?)<')
        id += 1
    # >>>>> daily <<<<<
    dailyContent = findInContent(webContent, '<div class="dailymsg"(.*?)</ul>')
    dailyDict = {}
    dailyDict['title'] = 'Daily'
    id = 0
    Lines = getList([], dailyContent, '<li(.*?)</li>')
    for Line in Lines:
        if DBGdaily: print '---------------------------------- Line ----------------------\n' , Line
        dailyDict['Record=%s' % id] = getList([], Line, 'role="button" href="\?(.*?)".*<span>(.*?)<.*<span>(.*?)<.*src="(.*?)".*alt="(.*?)" .*data-icon="(.*?)".*daytemphigh">(.*?)<.*<p>(.*?)</p>.*<span>(.*?)<')
        try:
            weatherIconName = utfTOansi(dailyDict['Record=%s' % id][0][4])
            dailyDict['WeatherIcon4Record=%s' % id] = iconsMap.get(weatherIconName, '')
            if reportMissingIcons and dailyDict['WeatherIcon4Record=%s' % id] == '' and weatherIconName not in missingIcons:
                open("/tmp/MSNWeatherMissingMappings.log", "a").write('Missing iconsMap(%s)\n' % weatherIconName)
                missingIcons += weatherIconName + '\n'
        except Exception:
            dailyDict['WeatherIcon4Record=%s' % id] = ''
        if DBGdaily:
            print "---------------------------------- dailyDict['Record=%s'] ----------------------\n"  % id, dailyDict['Record=%s' % id]
            print '!!! >>> WeatherIcon4Record%s="%s" > "%s"' % (id, weatherIconName, dailyDict['WeatherIcon4Record=%s' % id])
        id += 1
    
    return nowDict, hourlyDict, dailyDict
            
#for tests outside e2
if __name__ == '__main__':
    import os
    import urllib2
    #webContent = urllib2.urlopen('http://www.msn.com/weather/we-city?culture=pl-PL&form=PRWLAS&q=Warszawa%2C%20Polska').read()
    webContent = urllib2.urlopen('https://www.msn.com/pl-PL/weather?culture=pl-PL&form=PRWLAS&q=Warszawa%2C%20Polska').read()
    nowDict, hourlyDict, dailyDict = getWeather(webContent, False, False, True)
    #print '---------------------------------- webContent ----------------------'
    #print webContent
    #print '---------------------------------- nowDict -------------------------'
    #print nowDict
    #print '---------------------------------- hourlyDict ----------------------'
    #print hourlyDict
    #print '---------------------------------- dailyDict -----------------------'
    #print dailyDict