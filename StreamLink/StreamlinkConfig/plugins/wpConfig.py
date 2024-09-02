import os

try:
    from streamlink.e2config import getE2config
except Exception:
    os.system('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/re-initiate.sh') #nie powinno być potrzebne, ale...
    from streamlink.e2config import getE2config
  

params = { 'login_url'        : 'https://pilot.wp.pl/api/v1/user_auth/login?device_type=android_tv',
           'main_url'         : 'https://pilot.wp.pl/api/v1/channels/list?device_type=android_tv',
           'video_url'        : 'https://pilot.wp.pl/api/v1/channel/',
           'close_stream_url' : 'https://pilot.wp.pl/api/v1/channels/close?device_type=android_tv',
          }

headers = { 'User-Agent':   'ExoMedia 4.3.0 (43000) / Android 8.0.0 / foster_e',
            'Accept':       'application/json',
            'x-version':    'pl.videostar|3.53.0-gms|Android|26|foster_e',
            'content-type': 'application/json; charset=UTF-8',
            'Referer':      'https://pilot.wp.pl/login'
          }

data = {'device': 'android_tv', 
        'login' : getE2config('WPusername'), 
        'password': getE2config('WPpassword')
      }

PreferDash = getE2config('WPpreferDASH', False)
videoDelay = getE2config('WPvideoDelay', 0)

def saveCookie(cookie):
    open("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/pilotwppl.cookie", "w").write('%s' % cookie)
  
def getCookie():
    if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/pilotwppl.cookie"):
        return open("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/pilotwppl.cookie", "r").read().strip()
    else:
        return None
