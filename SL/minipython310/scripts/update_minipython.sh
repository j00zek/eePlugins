#/bin/bash
#http://images.mynonpublic.com/openatv/7.1/index.php?open=zgemmah9twin

dirPath=`dirname "$0"`

mkdir -p /tmp/AQQ
rm -rf /tmp/AQQ/*
cd /tmp/AQQ

rm -f ../Packages*

curl -s http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/Packages.gz -o ../Packages.gz
gunzip -f ../Packages.gz

echo pobieranie paczek
for paczka in `cat $dirPath/paczki_do_pobrania|grep -v '^#'`
do
    #echo $paczka
    info=`sed -n "/^Package: $paczka\$/,/^MD5Sum:/p" < ../Packages`
    myPKG=`echo $info|grep "Filename: "|grep -o "[^ ]*.ipk"|grep -o "[^ ]*.ipk"`
    if [ -z $myPKG ];then
      echo brak danych dla $paczka
      exit 1
    fi
    echo Pobieram $myPKG
    curl -s http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/$myPKG -o ./myPKG.ipk
    ar -x ./myPKG.ipk;
    tar -xf ./data.tar.xz
    rm -f ./* 2>/dev/null
done
rm -fr $dirPath/../usr
cp -fr ./* $dirPath/../
mv -f $dirPath/../usr/bin/chardetect $dirPath/../usr/bin/chardetect3 #konflikt z py2.7
rm -f $dirPath/../etc/ld.so.conf
