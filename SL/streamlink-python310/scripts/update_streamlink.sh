#/bin/bash
#http://images.mynonpublic.com/openatv/7.1/index.php?open=zgemmah9twin

dirPath=`dirname "$0"`
echo $dirPath

mkdir -p /tmp/AQQ
rm -rf /tmp/AQQ/*

cd /tmp/AQQ
echo pobieranie
curl  http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/Packages.gz -o ./Packages.gz
echo rozpakowanie
gunzip -f ./Packages.gz

myPKG=`grep 'Filename:.*streamlink_' < ./Packages|grep -o 'streamlink_[^ ]*.ipk'`
echo $myPKG
curl http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/$myPKG -o ./myPKG.ipk
ar -x ./myPKG.ipk
tar -xf ./data.tar.xz
rm -rf $dirPath/../streamlink
mv -f ./usr/lib/python3.10/site-packages/streamlink $dirPath/../
tar -xf ./control.tar.gz
depends=` grep 'Depends:.*' < ./control`
echo $depends
#sed -i "s/^Depends:.*/$depends/" /DuckboxDisk/github/eePlugins/SL/streamlink310/CONTROL/control
#http://feeds2.mynonpublic.com/7.1/h9combo/cortexa15hf-neon-vfpv4/streamlink_3.2.0-git4100+3762fe8_0.0-git10+6168dfc-r0_cortexa15hf-neon-vfpv4.ipk
cd ~
rm -rf /tmp/AQQ