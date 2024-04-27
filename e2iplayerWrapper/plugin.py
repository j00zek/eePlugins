#
# e2iplayerWrapper do uruchamiania materialow dostepnych w e2iplayerze z listy kanalow
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
MyHelper = None

def e2iBatchCMD(batchCMD = ''):
    if batchCMD == '':
        if os.path.exists('/tmp/e2i_batch_cmd'):
            os.remove('/tmp/e2i_batch_cmd')
    else:
        print('MYe2iPlayer, batchCMD:',batchCMD)
        with open('/tmp/e2i_batch_cmd', 'w') as f:
            f.write(batchCMD)
            f.close()

    def END_e2iplayer(answer=None, lastPosition=None, clipLength=None, *args, **kwargs):
        e2iBatchCMD()

def zap(session, service, **kwargs):
    errormsg = None
    if service:
        try:
            serviceString = service.toString()
            url = serviceString.split(":")[10]
            if url != '' and url.startswith("http%3a//e2iplayer/"):
                print("j00zek:[ChannelSelection] zap > e2iplayer >>>")
                global MYe2iPlayer, MyHelper
                batchCMD = url[len('http%3a//e2iplayer/'):]
                batchCMD = batchCMD.replace('%3a', ':')
                e2iBatchCMD(batchCMD)
                if MYe2iPlayer is None:
                    try:
                        from Components.PluginComponent import pluginComponent
                        pluginList = pluginComponent.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
                    except Exception:
                        from Components.PluginComponent import plugins
                        pluginList = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
                    for weight, plugin in enumerate(pluginList, start=1):
                        if plugin.name == 'E2iPlayer':
                            MYe2iPlayer = plugin
                            break
                if MyHelper is None:
                    try:
                        from Plugins.Extensions.e2iplayerWrapper.helperNP import Helper
                        MyHelper = Helper()
                    except Exception as e:
                        MyHelper = False
                        print("j00zek:[ChannelSelection] zap > exception loading Helper:", str(e))
                if MYe2iPlayer:
                    if MyHelper != False:
                        MyHelper.init(batchCMD)
                    print("j00zek:[ChannelSelection] zap > jumping to MYe2iPlayer")
                    MYe2iPlayer(session)
                    print("j00zek:[ChannelSelection] zap > return from MYe2iPlayer")
        except Exception as e:
            print("j00zek:[ChannelSelection] zap > MYe2iPlayer failed %s" % str(e))
    return (None, errormsg)
