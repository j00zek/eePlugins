from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.SystemPlugins.e2componentsInitiator.version import Version

Info='@j00zek %s' % Version

########################### Tlumaczenia ###########################################
from Components.j00zekModHex2strColor import Hex2strColor as h2c, clr
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
from os import environ

PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/e2componentsInitiator/locale')
    
def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain("e2cInitiator", PluginLanguagePath)

def mygettext(txt):
    t = gettext.dgettext("e2cInitiator", txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)
_ = mygettext

########################### KONFIGURACJA ###########################################
from Components.config import config, ConfigSubsection, ConfigDirectory, ConfigSelection, ConfigYesNo, NoSave

MinFontChoices = [("0,67", _("Defined in skin")), ("1", _("same as max font")),
                  ("0.75", _("75%% of defined font")), ("0,67", _("67%% of defined font")),
                  ("0,5", _("50%% of defined font")) ]
#############################################################################################

config.plugins.j00zekCC = ConfigSubsection()

config.plugins.j00zekCC.PiconsMainRootPath = ConfigDirectory(default = '/usr/share/enigma2')  

config.plugins.j00zekCC.PiconsStyle = ConfigSelection(default = "Transparent%201/8bit/220x132", choices = [
                                                                                ("Blue%201/8bit/220x132", "Blue 1"),
                                                                                ("Blue%202/8bit/220x132", "Blue 2"),
                                                                                ("Green/8bit/220x132", "Green"),
                                                                                ("NoName%201/8bit/220x132", "NoName 1"),
                                                                                ("NoName%202/8bit/220x132", "NoName 2"),
                                                                                ("NoName%203/8bit/220x132", "NoName 3"),
                                                                                ("NoName%204/8bit/220x132", "NoName 4"),
                                                                                ("NoName%205/8bit/220x132", "NoName 5"),
                                                                                ("SiennaRoot%201/8bit/220x132", "SiennaRoot 1"),
                                                                                ("SiennaRoot%202/8bit/220x132", "SiennaRoot 2"),
                                                                                #("Silver-Black%201/8bit/100x60", "Silver-Black 1"),
                                                                                ("Silver-Black%202/8bit/220x132", "Silver-Black 2"),
                                                                                #("Star/8bit/100x60", "Star"),
                                                                                ("Transparent%201/8bit/220x132", "Transparent 1"),
                                                                                ("Transparent%202/8bit/220x132", "Transparent 2"),
                                                                                #("White%201/8bit/100x60", "White 1"),
                                                                                ("White%202/8bit/220x132", "White 2"),
                                                                              ])
config.plugins.j00zekCC.zzPiconsStyle = ConfigSelection(default = "Transparent%201/8bit/400x170", choices = [
                                                                                ("Green/8bit/400x170", "Green"),
                                                                                ("NoName%201/8bit/400x170", "NoName 1"),
                                                                                ("NoName%202/8bit/400x170", "NoName 2"),
                                                                                ("NoName%203/8bit/400x170", "NoName 3"),
                                                                                ("NoName%205/8bit/400x170", "NoName 5"),
                                                                                ("SiennaRoot%201/8bit/400x170", "SiennaRoot 1"),
                                                                                ("SiennaRoot%202/8bit/400x170", "SiennaRoot 2"),
                                                                                ("Transparent%201/8bit/400x170", "Transparent 1"),
                                                                                ("Transparent%202/8bit/400x170", "Transparent 2"),
                                                                                ("White%202/8bit/400x170", "White 2"),
                                                                              ])
config.plugins.j00zekCC.NoPiconsOnHDD = ConfigYesNo(default = True)
config.plugins.j00zekCC.PiconsMissingDownload = ConfigYesNo(default = False)
config.plugins.j00zekCC.DeleteDownloaded = NoSave(ConfigYesNo(default = False))

config.plugins.j00zekCC.PiconAnimation_UserPath = ConfigDirectory(default = _('not set'))  
config.plugins.j00zekCC.AlternateUserIconsPath = ConfigDirectory(default = _('not set'))

config.plugins.j00zekCC.adsRootPath = ConfigDirectory(default = config.plugins.j00zekCC.PiconsMainRootPath.value)  
config.plugins.j00zekCC.adsPiconStyle = ConfigSelection(default="off", choices = [("off", _("don't mask")),
                                                                                    ("adssign", _("ads sign")),
                                                                                    ("adspicon", _("ads sign on top of picon"))
                                                                                   ])

#j00zekLabel
config.plugins.j00zekCC.j00zekLabelSN = ConfigSelection(default = "0", choices = MinFontChoices )
config.plugins.j00zekCC.j00zekLabelEN = ConfigSelection(default = "0", choices = MinFontChoices )
#runningText
config.plugins.j00zekCC.rtType = ConfigSelection(default = "0", choices = [("0", _("Defined in skin")), ("1", _("don't move")), ("2", _("RUNNING")), ("3", _("SWIMMING"))])
config.plugins.j00zekCC.rtFontSize = ConfigSelection(default = "0", choices = [("0", _("if defined in skin")), ("0.1", _("+/- 10%%")), ("0.2", "+/- 20%%")])
config.plugins.j00zekCC.rtStartDelay = ConfigSelection(default = "0", choices =   [ ("0", _("Defined in skin")), ("1000", _("1s")), ("2000", _("2s")),
                                                                                   ("4000", _("4s")), ("6000", _("6s")), ("8000", _("8s")) ])
config.plugins.j00zekCC.rtStepTimeout = ConfigSelection(default = "0", choices = [ ("0", _("Defined in skin")), ("25", _("40 px/s")),
                                                                             ("50", _("20 px/s")), ("100", _("10 px/s")) ])
config.plugins.j00zekCC.rtRepeat = ConfigSelection(default = "0", choices = [ ("0", _("Defined in skin")), ("1", _("one time")),
                                                                             ("5", _("5 times")), ("100", _("never stop")) ])
#EventName
config.plugins.j00zekCC.enDescrType = ConfigSelection(default = "0", choices = [("0", _("Defined in skin")), ("1", _("Short")),
                                                                                ("2", _("Extended or Short")), ("3", _("Short and Extended")),
                                                                                ("4", _("Extended and short (if different)")) ])
config.plugins.j00zekCC.enTMDBratingFirst = ConfigYesNo(default = False)
config.plugins.j00zekCC.enADSfirst = ConfigYesNo(default=False)

#j00zekModServiceName2
config.plugins.j00zekCC.snVFDtype = ConfigSelection(default = "\x25N", choices = [("\x25N", _("Chanel name")), ("\x25n - \x25N", _("Channel number - Channel name")),
                                                                                  ("\x25N - \x25S", _("Chanel name - Sat name")), ("\x25E", _("Event name")),
                                                                                  ("\x25N - \x25E", _("CHname - EVname")), ("\x25n - \x25N - \x25E", _("CHnumber - CHname - EVname")),
                                                                                  ("\x25N - \x25E (\x25e)", _("CHname - EVname (progress \x25)")),
                                                                                  ("\x25n - \x25N - \x25E (\x25e)", _("CHnumber -CHname - EVname (progress \x25)")),
                                                                                  ("\x25D", _("HH:MM E.g. 07:23")), ("\x25d", _("HH:MM E.g. 7:23"))
                                                                                 ])
config.plugins.j00zekCC.snINFOtype = ConfigSelection(default = "\x25S", choices = [("\x25S", _('Sat name')), ("\x25T", _('Transponder info')),
                                                                                   ("\x25cB \x25s \x25cY \x25T", '%s %s %s %s' %( clr['B'], _('Signal type'), clr['Y'], _('Transponder info'))),
                                                                                   ("\x25cB \x25s \x25cY \x25S \x25cG \x25P", '%s %s %s %s %s %s' %( clr['B'], _('Signal type'), clr['Y'], _('Sat name'), clr['G'], _('Provider'))),
                                                                                   ("\x25cB \x25s \x25cY \x25S \x25cG \x25T", '%s %s %s %s %s %s' %( clr['B'], _('Signal type'), clr['Y'], _('Sat name'), clr['G'], _('Transponder info'))),
                                                                                   ("\x25cB \x25s \x25cY \x25T \x25cG \x25B", '%s %s %s %s %s %s' %( clr['B'], _('Signal type'), clr['Y'], _('Transponder info'), clr['G'], _('Bouquet name'))),
                                                                                   ("\x25cB \x25s \x25cY \x25T \x25cG \x25P", '%s %s %s %s %s %s' %( clr['B'], _('Signal type'), clr['Y'], _('Transponder info'), clr['G'], _('Provider')))
                                                                                 ])
#rollerCharLCD
config.plugins.j00zekCC.scroll_speed = ConfigSelection(default = "300", choices = [("500", _("slow")), ("300", _("normal")), ("100", _("fast"))])
config.plugins.j00zekCC.scroll_delay = ConfigSelection(default = "10000", choices = [("10000", "10 " + _("seconds")), ("20000", "20 " + _("seconds")),
                                                                                     ("30000", "30 " + _("seconds")), ("60000", "1 " + _("minute")),
                                                                                     ("300000", "5 " + _("minutes")), ("noscrolling", _("off"))
                                                                                    ])
#j00zekModClockToText
config.plugins.j00zekCC.clockVFDstdby = ConfigSelection(default = "\x25H:\x25M", choices = [("\x25H:\x25M", _("HH:MM E.g. 07:23")),("\x25-H:\x25M", _("HH:MM E.g. 7:23")),  
                                                                                            ("\x25H:%M:\x25S", _("HH:MM:SS")),
                                                                                  ("\x25H:\x25M \x25d.\x25m.\x25Y", _("HH:MM day.month.year")),
                                                                                  ("\x25H:\x25M \x25a \x25d \x25b", _("HH:MM Weekday Day MonthName")) ])
config.plugins.j00zekCC.clockVFDpos = ConfigSelection(default = "0", choices = [("0", _("Defined in skin")), ("1", _("left")), ("2", _("center")), ("3", _("right"))])

#j00zekModFrontendInfo2
config.plugins.j00zekCC.feInfoType = ConfigSelection(default = "11", choices = [("10", _("Active & Busy & Available")), ("11", _("Active & Busy")), ("12", _("Don't show FE state"))])
config.plugins.j00zekCC.feInfoTitle = ConfigSelection(default = "", choices = [("", _("No Title")), (_("FE's in use:"), _("FE's in use:")), (_("FE's"), _("FE's"))])
#j00zekModCaidInfo2
config.plugins.j00zekCC.ciFormat = ConfigSelection(default = "", choices = [("", _("Defined in skin")), ("%SCFN %S %H %SY %PV %SP %PR %C %P %p %O %R %T", _("All info in a line")),
                                                                             ("%SCN %n %S %n %H %n %SY %n %PV %n %SP %n %PR %n %C %n %P %n %p %n %O %n %R %n %T", _("All info in a column")),
                                                                             ("%SCN", _("Running Softcam name")), (_("%SCFN"), _("Running Softcam file name")),
                                                                             (h2c(0x0000CC99) + " %SCFN ", '%s %s ' %( h2c(0x0000CC99), _('Running Softcam file name'))),
                                                                             ("%SCFN , %R", _("Running Softcam file name, READER")),
                                                                             ("%R", _("Active reader name")),
                                                                             (h2c(0x0000FF00) + " %SCFN " + h2c(0x00FFCC00) + " %R", '%s %s %s %s' %( h2c(0x0000FF00), _('Running Softcam file name'), h2c(0x00FFCC00), _('READER'))),
                                                                             (_("Coded program %SY"), _("TXT PROVIDER")),
                                                                             ("CAID: %C PROV: %p HOPS: %H TIME: %T", _("CAID, PROV, HOPS, TIME")),
                                                                             ("CAID: %C PROV: %p FROM: %S %SP HOPS: %H TIME: %T", _("CAID, PROV, FROM, HOPS, TIME")),
                                                                             ("CAID: %C PROV: %p FROM: %O HOPS: %H TIME: %T", _("CAID, PROV, SOURCE, HOPS, TIME")),
                                                                             (h2c(0x00FFCC00) + " CAID: %C PROV: %p HOPS: %H TIME: %T ", '%s %s ' %( h2c(0x00FFCC00), _('CAID, PROV, HOPS, TIME'))),
                                                                             (h2c(0x0000CC99) + " CAID: %C PROV: %p FROM: %S %SP HOPS: %H TIME: %T ", '%s %s ' %( h2c(0x0000CC99), _('CAID, PROV, FROM, HOPS, TIME'))),
                                                                             (h2c(0x0000B7EB) + " CAID: %C PROV: %p FROM: %O HOPS: %H TIME: %T ", '%s %s ' %( h2c(0x0000B7EB), _('CAID, PROV, SOURCE, HOPS, TIME'))),
                                                                             (h2c(0x0000FF00) + " CAID: %C " + h2c(0x00FFCC00) + " PROV: %p " + h2c(0x0000CC99) + " FROM: %S %SP " + h2c(0x0000FF00) + " HOPS: %H " + h2c(0x00FFCC00) + " TIME: %T", '%s %s %s %s %s %s %s %s %s %s' %( h2c(0x0000FF00), _('CAID:'), h2c(0x00FFCC00), _('PROV:'), h2c(0x0000CC99), _('FROM:'), h2c(0x0000FF00), _('HOPS:'), h2c(0x00FFCC00), _('TIME:')))
                                                                            ])

config.plugins.j00zekCC.iconsANDanims = ConfigYesNo(default = False)
#ConfigText(default = _("none")) #("", _(""))
config.plugins.j00zekCC.PiPbackground = ConfigSelection(default = "b", choices = [("n", _("no background")), ("b", _("Bing"))])
