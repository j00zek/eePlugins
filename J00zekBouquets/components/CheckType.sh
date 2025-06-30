#!/bin/sh
#
# @j00zek, wersja 2018-01-02
#

[ -f /tmp/jB.log ] && rm -f /tmp/jB.log 2>/dev/null

rootPath=`dirname $0`
chmod 755 $rootPath/*.sh
if `grep -q 'ARMv7' </proc/cpuinfo`;then
  validSystems='ARM'
  platform="arm"
elif `grep -q 'cpu family.*sh4' </proc/cpuinfo`;then
  platform="sh4"
else
  platform="mips"
fi 
myPath=$rootPath/$platform
#echo $myPath
if [ -f $myPath/dvbsnoop ] && [ ! -e /usr/bin/dvbsnoop ] && [ ! -e /usr/sbin/dvbsnoop ];then
    aqq=`opkg install dvbsnoop1 2>&1 1>/dev/null`
    [ $? -gt 0 ] && cp -f $myPath/dvbsnoop /usr/bin/dvbsnoop 2>/dev/null
fi

if [ -f $myPath/platformtester-$platform ]; then
  chmod 755 $myPath/*
  type=`$myPath/platformtester-$platform 2>/dev/null`
  if [ -z $type ];then
    echo 'Wykryto kernel typu A'
    echo
    ln -sf $myPath/j00zekBouquetsNC-$platform.Atype $rootPath/j00zekBouquetsNC
    ln -sf $myPath/j00zekBouquetsCP-$platform.Atype $rootPath/j00zekBouquetsCP
  else
    echo 'Wykryto kernel typu B'
    ln -sf $myPath/j00zekBouquetsNC-$platform.Btype $rootPath/j00zekBouquetsNC
    ln -sf $myPath/j00zekBouquetsCP-$platform.Btype $rootPath/j00zekBouquetsCP
  fi
else
  echo '$myPath/platformtester-$platform nie istnieje!!!'
fi
