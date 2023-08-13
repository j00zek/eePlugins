# -*- coding: utf-8 -*-
import json, os, requests, sys, re
from urllib.parse import quote as urllib_quote, unquote as urllib_unquote
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import base64

def ensure_str(string2decode):
    if isinstance(string2decode, bytes):
        return string2decode.decode('utf-8', 'ignore')
    return string2decode

def downloadWebPage(webURL, newHEADERS = None):
        def decodeHTML(text):
            text = text.replace('&#243;', 'ó')
            text = text.replace('&#176;', '°').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
            text = text.replace('&#228;', 'ä').replace('&#196;', 'Ă').replace('&#246;', 'ö').replace('&#214;', 'Ö').replace('&#252;', 'ü').replace('&#220;', 'Ü').replace('&#223;', 'ß')
            return text
        
        webContent = ''
        try:
            if newHEADERS is None:
                HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                        'Accept-Charset': 'utf-8', 
                        'Content-Type': 'text/html; charset=utf-8'
                      }
            else:
                HEADERS = newHEADERS
            resp = requests.get(webURL, headers=HEADERS, timeout=7)
            webContent = ensure_str(resp.content)
            webHeader = resp.headers
            webContent = urllib_unquote(webContent)
            webContent = decodeHTML(webContent)
            #print("webHeader: %s" % resp.headers )
        except Exception as e:
            print("EXCEPTION '%s' in downloadWebPage() for %s" % (str(e), webURL) )
            webContent = 'EXCEPTION'
        return ensure_str(webContent)

def findInContent(ContentString, reFindString, reS = True):
    retTxt = ''
    if reS: FC = re.findall(reFindString, ContentString, re.S)
    else:   FC = re.findall(reFindString, ContentString)
    if FC:
        for i in FC:
            retTxt += i

    return retTxt

def getList(retList, ContentString, reFindString, reS = True):
    if reS: FC = re.findall(reFindString, ContentString, re.S)
    else:   FC = re.findall(reFindString, ContentString)
    if FC:
        for i in FC:
            retList.append(i)
    return retList

azmanIPTVsettings = None

def get_azmanIPTVsettings():
    global azmanIPTVsettings
    if azmanIPTVsettings is None:
        azmanIPTVsettings = {}
        azmanIPTVsettings['userbouquets'] = []
        try:
            mainURL = 'https://github.com/azman26/azmanIPTVsettings'
            webContent = downloadWebPage(mainURL)
            #open("/tmp/azmanIPTVsettings.txt", "w").write(webContent)
            title = findInContent(webContent, '<title>([^<]*)')
            webContent = downloadWebPage(mainURL + '/file-list/main')
            if webContent == 'EXCEPTION':
                return {'userbouquets': [], 'title':'EXCEPTION downloading list from github'}
            #open("/tmp/azmanIPTVsettings.txt", "w").write(webContent)
            webContent = findInContent(webContent, '<div class="js-details-container.*')
            webContent = re.sub(r"[\n\t\r]", "", webContent)
            webContent = webContent.replace('<div role="row"','\n<div role="row"') #mamy kazdy rekord w jednej linii
            #open("/tmp/azmanIPTVsettings.txt", "w").write(webContent)
            tmpList = getList([], webContent, 'href="([^"]*blob[^"]*\.tv)">([^<]*).*datetime="([0-9\-]+).([0-9:]+)', False)
            tmpList = getList(tmpList, webContent, 'href="([^"]*blob[^"]*\.radio)">([^<]*).*datetime="([0-9\-]+).([0-9:]+)', False)
            wbList = []
            for listItem in tmpList:
                wbList.append(('https://raw.githubusercontent.com' + listItem[0].replace('blob/',''), listItem[1],listItem[2],listItem[3]))
            #print(len(wbList))
            if len(wbList) > 0:
                azmanIPTVsettings['title'] = title
                azmanIPTVsettings['userbouquets'] = wbList
            else:
                azmanIPTVsettings['title'] = 'No azmanIPTVsettings found :('
        except Exception as e:
            azmanIPTVsettings['title'] = str(e)
    return azmanIPTVsettings
    
if __name__ == '__main__':
    print(get_azmanIPTVsettings())