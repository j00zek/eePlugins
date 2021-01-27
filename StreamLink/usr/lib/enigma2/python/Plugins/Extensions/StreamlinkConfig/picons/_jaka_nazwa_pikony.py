# -*- coding: utf-8 -*-
import sys, re, unicodedata 

gname = 'TV JAS£O'

gname = gname.lower()
gname = gname.replace(' fhd', ' hd').replace(' uhd', ' hd') #iptv streams names correction
gname = unicodedata.normalize('NFKD', unicode(gname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
gname = re.sub('[^a-z0-9]', '', gname.replace('&', 'and').replace('+', 'plus').replace('*', 'star'))
print gname