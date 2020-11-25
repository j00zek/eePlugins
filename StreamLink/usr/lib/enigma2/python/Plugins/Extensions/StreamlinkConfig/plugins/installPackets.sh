#/bin/sh
if [ "$1" == 'forceReinstall' ]; then
  reinstall=1
else
  reinstall=0
fi

if `grep -q 'osd.language=pl_PL' </etc/enigma2/settings`; then
  PL=1
else
  PL=0
fi

[ $PL -eq 1 ] && echo "Czekam na opkg..." || "Waiting for opkg..."
while [ -e /var/lib/opkg/lock ]
do
  sleep 10
done

opkg update > /dev/null
installed=`opkg list-installed|cut -d ' ' -f1`
paskagesList="ffmpeg
python-argparse 
python-core
python-pycrypto 
python-ctypes
python-iso3166 
python-iso639 
python-isodate 
python-futures
python-misc 
python-pkgutil
python-requests
python-shell
python-singledispatch 
python-pysocks
python-sqlite3
python-subprocess
python-websocket 
"

for pkg in $paskagesList;
do
  #echo "$installed"| grep -c $pkg
  if [ `echo "$installed"| grep -c $pkg` -gt 0 ];then
    if [ $reinstall -eq 0 ];then
        [ $PL -eq 1 ] && echo "$pkg jest już zainstalowany" || echo "$pkg already installed"
    else
        echo "------------------------------------------------------------"
        [ $PL -eq 1 ] && echo "$pkg jest już zainstalowany, wymuszam reinstalację" || "$pkg already installed, reinstalling it"
        echo "------------------------------------------------------------"
        opkg install --force-reinstall $pkg
                err=$?
                if [ $err -gt 0 ] && [ `ls /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/|grep -c $pkg` -eq 1 ];then
                        echo "------------------------------------------------------------"
                        [ $PL -eq 1 ] && echo "BŁĄD: brak $pkg w oficjanym repozytorium, instaluję kopię" || "ERROR: no $pkg in official repo, installing offline version"
                        echo "------------------------------------------------------------"
                        opkg install --force-reinstall /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/$pkg*.ipk
                fi
    fi
  else
    opkg install $pkg
        err=$?
        if [ $err -gt 0 ] && [ `ls /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/|grep -c $pkg` -eq 1 ];then
                echo "------------------------------------------------------------"
                [ $PL -eq 1 ] && echo "BŁĄD: brak $pkg w oficjanym repozytorium, instaluję kopię" || "ERROR: no $pkg in official repo, installing offline version"
                echo "------------------------------------------------------------"
                opkg install /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/$pkg*.ipk
        fi
  fi
done

[ -e /usr/lib/python2.7/site-packages/Crypto/Util/Padding.py ] || ln -sf /usr/lib/python2.7/site-packages/streamlink/missingScripts/Padding.py /usr/lib/python2.7/site-packages/Crypto/Util/Padding.py

sync
[ `grep -c 'config.plugins.streamlinksrv.enabled=true' < /etc/enigma2/settings` -eq 0 ] && exit 0

echo
if [ -e /var/run/streamlink.pid ];then
  [ $PL -eq 1 ] && echo "$pkg jest już zainstalowany" || echo "Restarting streamlinksrv"
  /etc/init.d/streamlinksrv restart
else
  [ $PL -eq 1 ] && echo "$pkg jest już zainstalowany" || echo "Starting streamlinksrv"
  killall streamlinksrv  > /dev/null
  /etc/init.d/streamlinksrv start
fi
if [ -e /var/run/streamlink.pid ];then
  [ $PL -eq 1 ] && echo "streamlinksrv uruchomiony poprawnie" || "streamlinksrv started properly"
else
  [ $PL -eq 1 ] && echo "Błąd uruchamiania streamlinksrv" || "Error starting streamlinksrv"
fi

echo
