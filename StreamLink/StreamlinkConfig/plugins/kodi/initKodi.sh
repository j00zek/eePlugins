#!/bin/sh
declare -a StringArray=("__init__" "e2utils" "jUtils" "plugin" "server")

declare -a KodiArray=("userdata/advancedsettings.xml" "userdata/keymaps/keymap.xml" "addons/script.j00zek.E2helper/")

KodiMainPAh=''

if [ `grep -c 'config.plugins.streamlinkSRV.support4kodi=True' < /etc/enigma2/settings` -eq 1 ];then
        if [ `opkg list-installed|grep -c 'enigma2-plugin-extensions-kodi'` -eq 1 ];then
                echo "Modyfikuję KODI Launcher"
                for f in "${StringArray[@]}"
                do
                        if [ -e /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc.org ];then 
                                : #echo "$f.pyc ma już kopię"
                        elif [ $f == 'jUtils' ];then
                                :
                        elif [ -e /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc ];then
                                echo "Tworzę kopię pliku $f.pyc"
                                cp -f /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc.org
                        fi
                        echo "Kopiuję nowy skrypt $f.py"
                        cp -f /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/kodi/launcher/$f.py /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.py
                done
                echo "Modyfikuję ustawienia KODI"
                for f in "${KodiArray[@]}"
                do
                  rm -rf /hdd/.kodi/$f 2>/dev/null
                                  cp -fr /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/kodi/$f /hdd/.kodi/$f
                done
                                #dodatki dla python 3.12
                                if [ -e /usr/lib/python3.12/ ];then
                                        if [ ! -e /usr/lib/python3.12/site-packages/setuptools ];then
                                                echo "Instaluje niezbedne pakiety do python-a 3.12"
                                                opkg update
                                                opkg install python3-setuptools python3-setuptools
                                        fi
                                fi
                                
        else
                echo 'Najpierw musisz mieć zainstalowaną wtyczkę enigma2-plugin-extensions-kodi!!!'
        fi
elif [ -e /usr/lib/enigma2/python/Plugins/Extensions/Kodi ]; then
        for f in "${StringArray[@]}"
        do
                if [ -e /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc.org ];then
                  mv -f /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc.org /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc
                  echo "Oryginalna wersja skryptu $f.pyc przywrócona"
                fi
                [ -e /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.py ] && rm -f /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.py
        done
        for f in "${KodiArray[@]}"
        do
         rm -rf /hdd/.kodi/$f
        done
fi
