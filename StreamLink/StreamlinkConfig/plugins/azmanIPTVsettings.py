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
            webContent = findInContent(webContent, 'docsUrl.*<script type="application\/json" data-target="react-partial.embeddedData">([^<]*)<\/script>')
            #open("/tmp/azmanIPTVsettings_webContent.txt", "w").write(webContent)
            tmpList = json.loads(webContent)["props"]["initialPayload"]["tree"]["items"]
            wbList = []
            for listItem in tmpList:
                if listItem["name"].endswith('.tv'):
                    wbList.append(('https://raw.githubusercontent.com/azman26/azmanIPTVsettings/main/' + listItem["path"], listItem["name"]))
            #print(len(wbList))
            if len(wbList) > 0:
                azmanIPTVsettings['title'] = title
                azmanIPTVsettings['userbouquets'] = wbList
            else:
                azmanIPTVsettings['title'] = 'BŁĄD analizy danych list kolegi azman pobranych z github'
        except Exception as e:
            azmanIPTVsettings['title'] = str(e)
            print(e)
    return azmanIPTVsettings
    
if __name__ == '__main__':
    print(get_azmanIPTVsettings())
