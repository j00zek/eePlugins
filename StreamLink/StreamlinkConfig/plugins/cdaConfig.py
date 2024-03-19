import os
import requests

def saveSetting(settingName, settingValue):
    settingName = "/etc/streamlink/cda/%s" % settingValue
    open(settingName, "w").write('%s' % cookie)
  
def getSetting(settingName):
    settingName = "/etc/streamlink/cda/%s" % settingName
    if os.path.exists(settingName):
        return open(settingName, "r").read().strip()
    else:
        return None

sess = requests.Session()
def build_url(query):
    return base_url + '?' + urlencode(query)

def getJson(url,post=None, params=None, auth=None, data=None):
    acc_token = getSetting('acc_token')
    headers = {
    #'User-Agent': 'pl.cda 1.2 (version 1.2.115 build 16083; Android 9; Samsung SM-J330F)',
    'User-Agent':'pl.cda.tv 1.0 (version 1.2.20 build 10619; Android 8.0.0; Unknown sdk_google_atv_x86)',
    'Accept': 'application/vnd.cda.public+json',
    'Host': 'api.cda.pl',}

    if not auth:
        headers.update({'Authorization': 'Basic YzU3YzBlZDUtYTIzOC00MWQwLWI2NjQtNmZmMWMxY2Y2YzVlOklBTm95QlhRRVR6U09MV1hnV3MwMW0xT2VyNWJNZzV4clRNTXhpNGZJUGVGZ0lWUlo5UGVYTDhtUGZaR1U1U3Q'})
    else:
        headers.update({'Authorization': 'Bearer '+acc_token})
    if not post:
        jsdata = sess.get(url, headers=headers, params=params, verify=False).json()
    else:

        jsdata = sess.post(url, headers=headers, params=params, data=data,verify=False).json()
    return jsdata
