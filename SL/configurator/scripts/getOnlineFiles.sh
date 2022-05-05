#/bin/bash
myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
#echo $myAbsPath

rm -rf ~/streamlink-master* 2 >/dev/null

wget -q https://github.com/streamlink/streamlink/archive/refs/heads/master.zip -O ~/streamlink-master.zip
[ $? -gt 0 ] && exit 0
unzip -q ~/streamlink-master.zip
cp -rf ~/streamlink-master/src/streamlink/* $myAbsPath/../../streamlink/
cp -rf ~/streamlink-master/src/streamlink_cli/* $myAbsPath/../../streamlink_cli/
cp -rf ~/streamlink-master/src/streamlink_cli/* $myAbsPath/../plugins/streamlink_cli/

rm -rf ~/streamlink-master*
