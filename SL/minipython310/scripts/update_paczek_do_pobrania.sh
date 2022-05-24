#/bin/bash
#http://images.mynonpublic.com/openatv/7.1/index.php?open=zgemmah9twin

dirPath=`dirname "$0"`

mkdir -p /tmp/AQQ
rm -rf /tmp/AQQ/*
cd /tmp/AQQ

rm -f ./paczki_do_pobrania.txt

echo tworzenie/aktualizacja list paczek
curl  http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/Packages.gz -o ./Packages.gz
echo rozpakowanie
gunzip -f ./Packages.gz

for paczka in `cat $dirPath/paczki_do_pobrania`
do
    sed -n "/Package: $paczka/,/^MD5Sum:/p" < ./Packages > ./$paczka.info
    echo $paczka >> ./paczki_do_pobrania.txt
    grep 'Depends: ' < ./$paczka.info|sed 's/Depends: //'|sed 's/[(][>]*=[^)]*[)]//g'|sed 's/[ ]*, /\n/g' >> ./paczki_do_pobrania.txt
done
cat ./paczki_do_pobrania.txt|sort | uniq > ./paczki_do_pobrania.sorted; rm -f ./paczki_do_pobrania.txt

echo pobieranie paczek
for paczka in `grep python < ./paczki_do_pobrania.sorted`
do
    sed -n "/Package: $paczka/,/^MD5Sum:/p" < ./Packages > ./$paczka.info
    echo $paczka >> ./paczki_do_pobrania.txt
    grep 'Depends: ' < ./$paczka.info|sed 's/Depends: //'|sed 's/[(][>]*=[^)]*[)]//g'|sed 's/[ ]*, /\n/g' >> ./paczki_do_pobrania.txt
done
cat ./paczki_do_pobrania.txt|sort | uniq > ./paczki_do_pobrania.sorted

exit 0

myPKG=`grep 'Filename:.*streamlink_' < ./Packages|grep -o 'streamlink_[^ ]*.ipk'`
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
#http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/streamlink_3.2.0-git4100+3762fe8_0.0-git10+6168dfc-r0_cortexa15hf-neon-vfpv4.ipk