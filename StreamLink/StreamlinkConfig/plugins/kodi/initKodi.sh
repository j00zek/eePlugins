#!/bin/sh
declare -a StringArray=("__init__" "e2utils" "jUtils" "plugin" "server")
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
        else
                echo 'Najpierw musisz mieć zainstalowaną wtyczkę nigma2-plugin-extensions-kodi!!!'
        fi
else
        for f in "${StringArray[@]}"
        do
                [ -e /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc.org ] && mv -f /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc.org /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.pyc
                [ -e /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.py ] && rm -f /usr/lib/enigma2/python/Plugins/Extensions/Kodi/$f.py
                echo "Oryginalna wersja skryptu $f.pyc przywrócona"
        done
fi
