#playermb params:
#       [1 '?mode=logout' 'resume:false' 'YESNO=YES']
#       [1, '?mode=login', 'resume:false']

import os, sys

def doLog(tekst, mode = 'a'): open("/tmp/emukodi.log", mode).write('%s\n' % tekst)

def runCMD(mainScript, mainScriptArgsList):
    if os.path.exists('/tmp/emukodi.plugindata'):
        os.remove('/tmp/emukodi.plugindata')
    for testDir in ['/j00zek/pywidevinecdm', '0:/usr/lib/python%s.%s/site-packages/pywidevinecdm' % (sys.version_info.major,sys.version_info.minor)]:
        activeDir = os.path.join(testDir, mainScript)
        if os.path.exists(activeDir):
            doLog('/usr/bin/python %s %s' % (activeDir, ' '.join(mainScriptArgsList)), 'w')
            os.system('/usr/bin/python %s %s' % (activeDir, ' '.join(mainScriptArgsList)))
            if os.path.exists('/tmp/emukodi.plugindata'):
                return(open('/tmp/emukodi.plugindata', 'r').read())

if __name__ == '__main__':
    # /usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/drmBouquet.py /etc/enigma2/userbouquet.cda.tv cda 8088 0 y 
    if sys.argv[1] == 'LOGIN':
        if 'player' in sys.argv[2].lower():
            mainScript = 'playerMain.py'
            print('Logowanie do serwisu player.pl.\n\nMBędziesz mieć maksimum 340 sekund na wykonanie polecenia w przeglądarce!!!')
            ret = runCMD(mainScript, [1, '?mode=login', 'resume:false']) #set logged flag
            ret = runCMD(mainScript, '1', '', 'resume:false') #initiate login process

    else:
        print(sys.argv)
        file_name = sys.argv[1]
        providerName = sys.argv[2]
        streamlinkURL = 'http%%3a//127.0.0.1%%3a%s/' % sys.argv[3]
        frameWork = str(sys.argv[4])
        if frameWork == "0":
            frameWork = "4097"
