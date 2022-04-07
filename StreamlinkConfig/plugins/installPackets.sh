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

##### sprawdzenie i ustawienie architektury procesora
if [ `grep -c ARMv7 < /proc/cpuinfo` -eq 0 ]; then
        echo "NiEWSPIERANA architektura CPU!!! Instalator NIE będzie działać. Radź sobie sam :P"
        exit 1
else
        archName='cortexa15hf-neon-vfpv4'
fi

##### sprawdzenie i ustawienie modelu tunera
tunerModel="vusolo4k" #h9combo

##### pobieranie najświeższych danych opkg
[ $PL -eq 1 ] && echo "Odświerzam opkg..." || "Updating opkg..."
while [ -e /var/lib/opkg/lock ]
do
  sleep 10
done

opkg update > /dev/null

##### sprawdzenie i ewentualne ustawienie architektury opkg
if [ `grep -c 'arch cortexa15hf-neon-vfpv4 26' < /etc/opkg/arch.conf` -gt 0 ];then
        echo "wykryto zmodyfikowaną przez wtyczkę architekturę systemu dla procesora ARMv7 :)"
elif [ `grep -c 'cortexa15hf-neon-vfpv4' < /etc/opkg/arch.conf` -gt 0 ];then
        echo "wykryto kompatybilną architekturę systemu :)"
else
        echo "wykryto niekompatybilną architekturę systemu dla procesora ARMv7, modyfikuję"
        echo 'arch cortexa15hf-neon-vfpv4 26' >> /etc/opkg/arch.conf
fi

##### finalne przygotowanie parametrów i struktury
archFeed="http://feeds2.mynonpublic.com/7.1/$tunerModel/$archName"

plugDir=/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/
tmpDir=/tmp/SLinstall
mkdir -p $tmpDir
rm -rf $tmpDir/*

cd $tmpDir

##### buduję listę wymaganych pakietów
#http://images.mynonpublic.com/openatv/7.1/index.php?open=zgemmah9twin
#http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/streamlink_3.2.0-git4100+3762fe8_0.0-git10+6168dfc-r0_cortexa15hf-neon-vfpv4.ipk
echo "Tworzenie listy wymaganych pakietów instalacyjnych"
curl http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/Packages.gz -o ./Packages.gz > /dev/null 2>&1
gunzip -f ./Packages.gz
cat $tmpDir/Packages|tr -d '\n'|sed 's/\(Package:\)/\n\1/g'|egrep -v 'locale-|-locale|perl-'|sed 's/Version:.*\(Depends:.*\)Size:.*/, \1/g'|sed 's/ ([^)]*)//g' > $tmpDir/Packages.records
echo 'streamlink' > $tmpDir/Packages.ToInstall
#grep 'Package: streamlink' < $tmpDir/Packages.records|sed 's/Package:\(.*\)Depends:\(.*\)Source:.*/\1\2/g'|sed 's/, /\n/g' > $tmpDir/Packages.ToInstall
#myPKGsArray=`grep 'Package: streamlink' < $tmpDir/Packages.records|sed 's/Package:[ ]*\(.*\)Depends:[ ]*\(.*\)Source:.*/\1\2/g'|sed 's/, /\n/g'`
#echo $myPKGsArray
while read line;do
        #echo $line
        if [ `grep "Package: $line" < $tmpDir/Packages.records|grep -c 'Depends:'` -gt 0 ];then
                grep "Package: $line" < $tmpDir/Packages.records|sed 's/.*Depends:\(.*\)Source:.*/\1\2/g'|sed 's/, /\n/g' >> $tmpDir/Packages.ToInstall
                myPKGarray=`grep "Package: $line" < $tmpDir/Packages.records|sed 's/.*Depends:[ ]*\(.*\)Source:.*/\1\2/g'|sed 's/, /\n/g'`
                for pkg in $myPKGarray;do
                        echo $pkg
                        if [ `grep -c "$pkg" < $tmpDir/Packages.ToInstall` -eq 0 ]; then
                                grep -c "$pkg" < $tmpDir/Packages.ToInstall
                                echo $pkg|xargs >> $tmpDir/Packages.ToInstall
                        fi
                done
        fi
done < $plugDir/plugins/InstallPackets.list

#####

exit 0


myPKG=`grep 'Filename:.*streamlink_' < $tmpDir/Packages.records|grep -o 'streamlink_[^ ]*.ipk'`
echo $myPKG
curl http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/$myPKG -o ./myPKG.ipk
ar -x ./myPKG.ipk
tar -xf ./data.tar.xz
rm -rf /DuckboxDisk/github/eePlugins/StreamLinkPython310/streamlink
mv -f ./usr/lib/python3.10/site-packages/streamlink /DuckboxDisk/github/eePlugins/StreamLinkPython310/
tar -xf ./control.tar.gz
depends=` grep 'Depends:.*' < ./control`
#echo $depends
sed -i "s/^Depends:.*/$depends/" /DuckboxDisk/github/eePlugins/StreamLinkPython310/CONTROL/control


exit 0
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
python-websocket-client
python-lxml
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
