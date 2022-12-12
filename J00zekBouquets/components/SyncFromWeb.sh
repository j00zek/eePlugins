#!/bin/sh
# 2019 @j00zek
# Script creates list of transponders being in use by PL providers
# j00zeBouquets will filter data based on it
#
ping -c 1 www.lyngsat.com >/dev/null
if [ $? -gt 0 ]; then
	echo "Błąd - Brak połączenia internetowego."
	exit 0
fi
myPath=`dirname $0`

getTransponders(){
    echo "Pobieram listę transponderów NC z lyngsat..."
    wget -q http://www.lyngsat.com/packages/NC-.html -O - |egrep ' [HV]<'|sed 's/^.*<b>\([0-9]*\) [HV].*/\1/' >/tmp/PLtrans.tmp
    [ $? -gt 0 ] && exit 0
    echo "Pobieram listę transponderów NC z kingofsat..."
    wget -q http://pl.kingofsat.net/pack-ncplus.php -O -|grep -e 'class="bld">1[0-9]*'|sed 's/^.*bld">\(1[0-9]*\).*/\1/' >>/tmp/PLtrans.tmp
    [ $? -gt 0 ] && exit 0
    echo "Pobieram listę transponderów CP z lyngsat..."
    wget -q http://www.lyngsat.com/packages/Cyfrowy-Polsat.html -O - |egrep ' [HV]<'|sed 's/^.*<b>\([0-9]*\) [HV].*/\1/' >>/tmp/PLtrans.tmp
    [ $? -gt 0 ] && exit 0
    echo "Pobieram listę transponderów CP z kingofsat..."
    wget -q http://pl.kingofsat.net/pack-polsat.php -O -|grep -e 'class="bld">1[0-9]*'|sed 's/^.*bld">\(1[0-9]*\).*/\1/' >>/tmp/PLtrans.tmp
    [ $? -gt 0 ] && exit 0
    grep '^.....$' < /tmp/PLtrans.tmp > /tmp/PLtrans.temp
    [ $? -gt 0 ] && exit 0
    [ -f /tmp/PLtrans.tmp ] && rm -f /tmp/PLtrans.tmp 2>/dev/null
	cfgFile="/usr/lib/enigma2/python/Plugins/Extensions/J00zekBouquets/components/PLtransponders.cfg"
	[ -e  $cfgFile ] && cat $cfgFile >> /tmp/PLtrans.temp
    [ -f /tmp/PLtrans.temp ] && sort </tmp/PLtrans.temp|uniq >$myPath/PLtransponders.cfg
    #rm -f /tmp/PLtrans.temp 2>/dev/null
    #echo "_(List of transponders being in use by PL providers has been updated. Found `grep -c '^'<$myPath/transponders.PL`)"
}

getSids(){
    echo "Pobieram listę sid NC z lyngsat..."
    wget -q http://www.lyngsat.com/packages/NC-_sid.html -O -|grep '<td.*size=2><b>'|egrep -v 'href=|http'|grep -o '<b>.*'|grep -o '[0-9]*'|uniq >/tmp/PLsids.tmp
    [ $? -gt 0 ] && exit 0
    echo "Pobieram listę sid NC z kingofsat..."
    wget -q http://pl.kingofsat.net/pack-ncplus.php -O -|grep '<[tT][dD] .*class="s"'|grep -o '>[0-9]*<'|grep -o '[0-9]*'|uniq >>/tmp/PLsids.tmp
    [ $? -gt 0 ] && exit 0
    echo "Pobieram listę sid CP z lyngsat..."
    wget -q http://www.lyngsat.com/packages/Cyfrowy-Polsat_sid.html -O -|grep '<td.*size=2><b>'|egrep -v 'href=|http'|grep -o '<b>.*'|grep -o '[0-9]*'|uniq >>/tmp/PLsids.tmp
    [ $? -gt 0 ] && exit 0
    echo "Pobieram listę sid CP z kingofsat..."
    wget -q http://pl.kingofsat.net/pack-polsat.php -O -|grep '<[tT][dD] .*class="s"'|grep -o '>[0-9]*<'|grep -o '[0-9]*'|uniq >>/tmp/PLsids.tmp
    [ $? -gt 0 ] && exit 0
    #analyzing
    [ -f /tmp/PLsids ] && rm -f /tmp/PLsids 2>/dev/null
    while read -r SID
    do
      printf '%04x\n' $SID>>/tmp/PLsids
    done </tmp/PLsids.tmp
	cfgFile="/usr/lib/enigma2/python/Plugins/Extensions/J00zekBouquets/components/PLsids.cfg"
	[ -e  $cfgFile ] && cat $cfgFile >> /tmp/PLsids
    [ -f /tmp/PLsids ] && sort </tmp/PLsids|uniq >$myPath/PLsids.cfg
    rm -f /tmp/PLsids.tmp 2>/dev/null
    rm -f /tmp/PLsids 2>/dev/null
}
case $1 in
  "transponders") getTransponders;;
  "sids") getSids;;
   *) getTransponders;getSids;;
esac
exit 0
