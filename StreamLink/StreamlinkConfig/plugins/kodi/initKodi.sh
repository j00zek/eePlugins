#!/bin/sh
if [ `grep -c 'config.plugins.streamlinkSRV.support4kodi=True' < /etc/enigma2/settings` -eq 1 ];then
        if [ `opkg list-installed|grep -c 'enigma2-plugin-extensions-kodi'` -eq 1 ];then 
                echo 'Znaleziono zainstalowaną standardową wtyczkę do KODI, musisz ją najpierw odinstalować komendą "opkg remove enigma2-plugin-extensions-kodi" !!!'
        elif [[ -L "/usr/lib/enigma2/python/Plugins/Extensions/Kodi" && -d "/usr/lib/enigma2/python/Plugins/Extensions/Kodi" ]]; then
                echo 'Własna wersja wtyczki obsługująca KODI jest już zainstalowana :)'
        else
                echo 'Instaluje własną wersję wtyczki obsługującej KODI'
                ln -sf /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/kodi/launcher /usr/lib/enigma2/python/Plugins/Extensions/Kodi
        fi
fi