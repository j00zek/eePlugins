# -*- coding: utf-8 -*-
import os

name2nameDict = {'telewizjawphd': 'wp',
                'tvp3białystok'             : 'tvp3warszawa',
                'tvp3bydgoszcz'             : 'tvp3warszawa',
                'tvp3gdańsk'                : 'tvp3warszawa',
                'tvp3gorzówwielkopolski'    : 'tvp3warszawa',
                'tvp3katowice'              : 'tvp3warszawa',
                'tvp3kielce'                : 'tvp3warszawa',
                'tvp3kraków'                : 'tvp3warszawa',
                'tvp3lublin'                : 'tvp3warszawa',
                'tvp3Łódź'                  : 'tvp3warszawa',
                'tvp3olsztyn'               : 'tvp3warszawa',
                'tvp3opole'                 : 'tvp3warszawa',
                'tvp3poznań'                : 'tvp3warszawa',
                'tvp3rzeszów'               : 'tvp3warszawa',
                'tvp3szczecin'              : 'tvp3warszawa',
                'tvp3wrocław'               : 'tvp3warszawa',
                }

name2service4wpDict = {
                        '4FUN.TV':                      '1:0:1:428D:2BC0:13E:820000:0:0:0',
                        '4FUN DANCE':                   '1:0:1:428F:2BC0:13E:820000:0:0:0',
                        '4FUN KIDS':                    '1:0:1:428E:2BC0:13E:820000:0:0:0',
                        'Adventure TV HD':              '1:0:19:10E9:3E8:13E:820000:0:0:0',
                        'Antena HD':                    '1:0:1:12C5:2E7C:13E:820000:0:0:0',
                        'AXN HD':                       '1:0:1:C25:1E78:71:820000:0:0:0',
                        'BBC Brit HD':                  '1:0:1:7D6:22C4:13E:820000:0:0:0',
                        'BBC Earth HD':                 '1:0:1:E08:2D50:13E:820000:0:0:0',
                        'Cartoon Network HD':           '1:0:1:2906:1EDC:71:820000:0:0:0',
                        'CNN':                          '1:0:1:329:3BC4:13E:820000:0:0:0',
                        'Comedy Central HD':            '1:0:1:C:1964:13E:820000:0:0:0',
                        'Crime+Investigation':          '1:0:1:C30:1E78:71:820000:0:0:0',
                        'Da Vinci HD':                  '1:0:1:4280:2BC0:13E:820000:0:0:0',
                        'Disney Channel':               '1:0:1:1CB6:1CE8:71:820000:0:0:0',
                        'Disney Junior':                '1:0:1:2938:1EDC:71:820000:0:0:0',
                        'Disney XD':                    '1:0:1:1CB5:1CE8:71:820000:0:0:0',
                        'DocuBox HD':                   '1:0:1:1B4:A:2:1330A8:0:0:0',
                        'Duck TV':                      '1:0:1:7985:ABC6:EC:0:0:0:0',
                        'English Club HD':              '1:0:1:7985:ABCC:EC:0:0:0:0',
                        'EzoTV':                        '1:0:1:80:1:48:0:0:0:0',
                        'Fashion TV HD':                '1:0:1:132C:33F4:13E:820000:0:0:0',
                        'Fightklub HD':                 '1:0:1:3E24:2EE0:13E:820000:0:0:0',
                        'Filmbox Arthouse HD':          '1:0:1:428A:2BC0:13E:820000:0:0:0',
                        'Filmax':                       '1:0:1:5B80:3C08:EC:0:0:0:0',
                        'FILMAX':                       '1:0:1:5B80:3C08:EC:0:0:0:0',
                        'Fox HD':                       '1:0:1:C27:1E78:71:820000:0:0:0',
                        'France 24 HD':                 '1:0:1:327:3BC4:13E:820000:0:0:0',
                        'France 24 English HD':         '1:0:1:328:3BC4:13E:820000:0:0:0',
                        'Gametoon HD':                  '1:0:1:38:16:A4A:0:0:0:0',
                        'GOLD TV':                      '1:0:16:10E8:3E8:13E:820000:0:0:0',
                        'Hip-Hop PL':                   '1:0:1:15:0:0:0:0:0:0',
                        'History':                      '1:0:1:C2F:1E78:71:820000:0:0:0',
                        'Home TV':                      '1:0:1:12C4:2E7C:13E:820000:0:0:0',
                        'Jazz HD':                      '1:0:1:540B:DD1E:EC:0:0:0:0',
                        'Kino TV HD':                   '1:0:1:3D61:2C88:13E:820000:0:0:0',
                        'Love TV HD':                   '1:0:1:36:F8:63B2:0:0:0:0',
                        'Motowizja HD':                 '1:0:19:3780:44C:13E:820000:0:0:0',
                        'MTV 00s':                      '1:0:1:8:1964:13E:820000:0:0:0',
                        'MTV 80s':                      '1:0:1:6FF1:436:1:C00000:0:0:0',
                        'MTV Live HD':                  '1:0:1:1:1964:13E:820000:0:0:0',
                        'MTV Polska HD':                '1:0:1:F:1964:13E:820000:0:0:0',
                        'Music Box Polska':             '1:0:1:152:1:48:0:0:0:0',
                        'National Geographic HD':       '1:0:1:32DF:190:13E:820000:0:0:0',
                        'Nick Jr.':                     '1:0:1:3:1964:13E:820000:0:0:0',
                        'Nick Music':                   '1:0:1:2:1964:13E:820000:0:0:0',
                        'Nickelodeon':                  '1:0:1:9:1964:13E:820000:0:0:0',
                        'NickToons HD':                 '1:0:1:E:1964:13E:820000:0:0:0',
                        'Nuta TV HD':                   '1:0:1:10DD:3E8:13E:820000:0:0:0',
                        'Paramount Channel HD':         '1:0:1:D:1964:13E:820000:0:0:0',
                        'Polonia 1':                    '1:0:1:423C:3DB8:13E:820000:0:0:0',
                        'Polsat':                       '1:0:16:3:2:2268:EEEE0000:0:0:0',
                        'Polsat HD':                    '1:0:16:3:2:2268:EEEE0000:0:0:0',
                        'Polsat Comedy Central Extra':  '1:0:1:10:1964:13E:820000:0:0:0',
                        'Polsat Viasat History HD':     '1:0:1:C20:1E78:71:820000:0:0:0',
                        'Polsat Viasat Explore HD':     '1:0:1:1CCA:1CE8:71:820000:0:0:0',
                        'Polsat Viasat Nature HD':      '1:0:1:2908:1EDC:71:820000:0:0:0',
                        'Power TV HD':                  '1:0:16:10E7:3E8:13E:820000:0:0:0',
                        'Radio 357':                    '1:0:1:3C02:3AF2:EC:0:0:0:0',
                        'Radio Nowy Świat':             '1:0:1:513D:DFC5:EC:0:0:0:0',
                        'Red Carpet TV HD':             '1:0:1:DB5:2D50:13E:820000:0:0:0',
                        'Sportklub HD':                 '1:0:1:DAF:2D50:13E:820000:0:0:0',
                        'Stars.TV HD':                  '1:0:1:427F:2BC0:13E:820000:0:0:0',
                        'Stopklatka HD':                '1:0:1:427B:2BC0:13E:820000:0:0:0',
                        'Sundance Channel HD':          '1:0:1:3E1D:2EE0:13E:820000:0:0:0',
                        'TBN Polska HD':                '1:0:1:327:1F40:13E:820000:0:0:0',
                        'Tele 5 HD':                    '1:0:1:423B:3DB8:13E:820000:0:0:0',
                        'Telewizja WP HD':              '1:0:1:3D5A:2C88:13E:820000:0:0:0',
                        'Top Kids HD':                  '1:0:16:10E5:3E8:13E:820000:0:0:0',
                        'Top Kids Jr':                  '1:0:16:10E5:3E8:13E:820000:0:0:0',
                        'Travelxp HD':                  '1:0:1:11FB:2B5C:13E:820000:0:0:0',
                        'TV 4':                         '1:0:1:3393:3390:71:820000:0:0:0',
                        'TV 4 HD':                      '1:0:1:3393:3390:71:820000:0:0:0',
                        'TV Puls':                      '1:0:1:3D66:2C88:13E:820000:0:0:0',
                        'TV Puls HD':                   '1:0:1:3D66:2C88:13E:820000:0:0:0',
                        'TV Republika HD':              '1:0:1:4289:2BC0:71:820000:0:0:0',
                        'TV Trwam':                     '1:0:1:10D6:418:1:C00000:0:0:0',
                        'TVC':                          '1:0:16:10E4:3E8:13E:820000:0:0:0',
                        'TVP Gdańsk':                   '1:0:1:9:0:48:0:0:0:0',
                        'TVP Warszawa':                 '1:0:1:113B:2AF8:13E:820000:0:0:0',
                        'TVN':                          '1:0:1:3DCD:640:13E:820000:0:0:0',
                        'TVP 1 HD':                     '1:0:1:3ABD:514:13E:820000:0:0:0',
                        'TVP 2 HD':                     '1:0:1:C22:1E78:71:820000:0:0:0',
                        'TVS':                          '1:0:1:3D58:2C88:13E:820000:0:0:0',
                        'Twoja.TV HD':                  '1:0:1:5:1:48:0:0:0:0',
                        'Ukraina 24':                   '1:0:19:4C4:5E:55:820000:0:0:0',
                        'ULTRA TV':                     '1:0:1:7389:DE37:EC:0:0:0:0',
                        'Ultra TV 4K':                  '1:0:1:7389:DE37:EC:0:0:0:0',
                        'wPolsce.pl HD':                '1:0:1:4279:2BC0:13E:820000:0:0:0',
                        'Zoom TV HD':                   '1:0:1:4291:2BC0:13E:820000:0:0:0',
                      }


name2serviceDict = {'tvp3warszawa':     '1:0:1:113B:2AF8:13E:820000:0:0:0',
                    'radionowyswiat':   '1:0:1:513D:DFC5:EC:0:0:0:0',
                    'tvpgdansk':        '1:0:1:9:0:48:0:0:0:0',
                    }

def updateDict():
    global name2serviceDict
    with open('/etc/enigma2/bouquets.tv','r') as btv:
        for bf2 in btv:
            if bf2.startswith('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET'):
                bf2 = bf2.split('"')[1]
                if os.path.exists('/etc/enigma2/' + bf2):
                    with open('/etc/enigma2/' + bf2,'r') as bf3:
                        try:
                            for line in bf3:
                                if line.startswith('#SERVICE ') and '::' in line: #this excludes every url links
                                    mdata = line.strip().replace('#SERVICE ','').split('::')
                                    if len(mdata[1]) > 3 and not name2serviceDict.get(mdata[1], False):
                                        name = mdata[1].lower().replace(' ','')
                                        name2serviceDict[name] = mdata[0]
                                        if name.endswith('hd'):
                                            name2serviceDict[name[:-2]] = mdata[0]
                        except Exception:
                            pass
    name2serviceDict['updatedDict'] = True


if name2serviceDict.get('updatedDict', False) == False:
    updateDict()

if __name__ == '__main__':
    for item in name2serviceDict:
        print("Key: '{}' , Referencja: '{}'".format(item,name2serviceDict[item]))