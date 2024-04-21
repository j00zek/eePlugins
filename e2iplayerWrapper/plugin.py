#
# e2iplayerWrapper do uruchamiania materialow dostpenych w e2iplayerze z listy kanalow
# dziala tylko na softach majacych zaimplementowana funkcje wrappera. Testowane na OpenATV 7.X
# skladnia na liscie kanalow: <referencja>:http%3a//e2iplayer/<nazwa hosta>%3a<sciezka w hoscie>:nazwa kanalu na liscie
# Przyklad:
#  #SERVICE 1:0:1:0:0:0:0:0:0:0:http%3a//e2iplayer/canalplus%3aTelewizja na żywo -> Wszystkie kanały -> CANAL+ DOMO HD:CANAL+ DOMO HD
#
# uwaga czas przelaczenie to okolo 3-4 sekundy na tunerach arm
#

from Plugins.Plugin import PluginDescriptor
import os

def Plugins(**kwargs):
    e2iBatchCMD()
    return [PluginDescriptor(name="StreamlinkExtWrapper", description="StreamlinkExtWrapper", where=PluginDescriptor.WHERE_CHANNEL_ZAP, needsRestart = False, fnc=zap)]

MYe2iPlayer = None

def e2iBatchCMD(batchCMD = ''):
    if batchCMD == '':
        if os.path.exists('/tmp/e2i_batch_cmd'):
            os.remove('/tmp/e2i_batch_cmd')
    else:
        print('MYe2iPlayer, batchCMD:',batchCMD)
        with open('/tmp/e2i_batch_cmd', 'w') as f:
            f.write(batchCMD)
            f.close()

def zap(session, service, **kwargs):
    def END_e2iplayer(answer=None, lastPosition=None, clipLength=None, *args, **kwargs):
        e2iBatchCMD()
    
    errormsg = None
    if service:
        try:
            serviceString = service.toString()
            url = serviceString.split(":")[10]
            if url != '' and url.startswith("http%3a//e2iplayer/"):
                global MYe2iPlayer
                batchCMD = url[len('http%3a//e2iplayer/'):] # expected result: "canalplus%3aTelewizja na żywo/Wszystkie kanały/CANAL+ DOMO HD"
                batchCMD = batchCMD.replace('%3a', ':')
                e2iBatchCMD(batchCMD)
                if MYe2iPlayer is None:
                    try:
                        from Components.PluginComponent import pluginComponent
                        pluginList = pluginComponent.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
                        for weight, plugin in enumerate(pluginList, start=1):
                            if plugin.name == 'E2iPlayer':
                                MYe2iPlayer = plugin
                                break
                    except ImportError as e:
                        print("[ChannelSelection] zap > MYe2iPlayer importing IPTVPlayer component error '%s'" % str(e))
                if MYe2iPlayer:
                    MYe2iPlayer(session)
        except Exception as e:
            print("[ChannelSelection] zap > MYe2iPlayer failed %s" % str(e))
    return (None, errormsg)
