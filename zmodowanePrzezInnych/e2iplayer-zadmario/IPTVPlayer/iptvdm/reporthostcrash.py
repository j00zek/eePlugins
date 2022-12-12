# -*- coding: utf-8 -*-

from Plugins.Extensions.IPTVPlayer.p2p3.UrlLib import urllib2_Request, urllib_urlencode, urllib2_urlopen
import sys


def ReportCrash(url, except_msg):
    request = urllib2_Request(url, data=urllib_urlencode({'except': except_msg}))
    data = urllib2_urlopen(request).read()
    print(data)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    ReportCrash(sys.argv[1], sys.argv[2])
    sys.exit(0)
