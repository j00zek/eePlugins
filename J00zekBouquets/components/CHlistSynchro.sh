#!/bin/sh
#
# skrypt synchronizujacy liste kanalow pomiedzy tunerami
# @j00zek
# wersja 2017-04-14
myPath=`dirname $0`

wget=''

if [ -f /usr/bin/fullwget ]; then
	wget=/usr/bin/fullwget
elif `/usr/bin/wget -help 2>&1|grep -q 'GNU Wget'`;then
	wget=/usr/bin/wget
elif `opkg list|grep -q wget`;then
	opkg install wget
	if `/usr/bin/wget -help 2>&1|grep -q 'GNU Wget'`;then
		wget=/usr/bin/wget
	fi
fi
if [ $wget == '' ];then
	echo "_(Install full version of wget first!)"
	exit 0
fi

##### FUNKCJE #####
getCONFIG(){
value=`grep "config.plugins.$1=" /etc/enigma2/settings | cut -d '=' -f2` 
if [ -z $value ]; then
	case $1 in #ustawienia standardowe
		"j00zek.chlistServerHidden") value='192.168.1.5';;
		"j00zek.chlistServerLogin") value='root';;
		"j00zek.chlistServerPass") value='root';;
		"j00zek.chlistServerHidden") value='false';;
	esac
fi
echo "$value"
}

##### INICJALIZACJA #####
ChannelsListPath='/tmp/myCHlist'
[ -z $1 ] && IPaddr=$( getCONFIG "j00zek.chlistServerHidden" ) || IPaddr=$1
[ -z $2 ] && login=$( getCONFIG "j00zek.chlistServerLogin" )   || login=$2
[ -z $3 ] && password=$( getCONFIG "j00zek.chlistServerPass" ) || password=$3

echo "_(Synchronizing from) $IPaddr login:$login password:$password"

[ -e $ChannelsListPath ] && rm -rf $ChannelsListPath/* || mkdir $ChannelsListPath # czyszczenie katalogu

##### FUNKCJE c.d. #####
getFILE(){
$wget --user=$login --password=$password -x ftp://$IPaddr/$1 -P $ChannelsListPath -q
if [ $? -eq 0 ]; then
	echo "$1 _(downloaded)"
else
	echo "_(ERROR downloading) $1, end!!!"
	exit 0
fi
}

getDIR(){
$wget --user=$login --password=$password -r ftp://$IPaddr/$1 -P $ChannelsListPath -q
if [ $? -eq 0 ]; then
	echo "DIR $1 downloaded"
else
	echo "ERROR downloading $1 DIR, end!!!"
	exit 0
fi
}
##### POBIERANIE KATALOGOW i PODSTAWOWE PORZADKI #####
getDIR /etc/enigma2
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/playlist 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/profile 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/blacklist 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/whitelist 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/settings 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/timers.xml 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.cache 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.pem 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.conf 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.e2pls 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/emc*.cfg 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/epg.dat 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/resumepoints.pkl 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/skin*.xml 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/resumepoints.pkl 2>/dev/null

getDIR /etc/tuxbox
rm -rf $ChannelsListPath/$IPaddr/etc/tuxbox/scart.conf 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/tuxbox/timezone.xml 2>/dev/null
##### PRZYGOTOWANIE LISTY #####
echo "_(Preparing channels list)..."
mkdir -p $ChannelsListPath/etc/tuxbox
mv -f $ChannelsListPath/$IPaddr/etc/tuxbox/*.xml $ChannelsListPath/etc/tuxbox/
mkdir -p $ChannelsListPath/etc/enigma2
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/lamedb $ChannelsListPath/etc/enigma2/ 2>/dev/null
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/satellites.xml $ChannelsListPath/etc/enigma2/ 2>/dev/null
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/bouquets.radio $ChannelsListPath/etc/enigma2/ 2>/dev/null
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/bouquets.tv $ChannelsListPath/etc/enigma2/
##### KOPIOWANIE TYLKO TEGO CO POTRZEBNE #####
echo "_(Analyzing radio bouquets)"
while read bukiet; do
	myFile=`echo $bukiet | grep "^#SERVICE[:]*"|sed 's/^#.*0:0:0:0://; s/^.*FROM BOUQUET "\(.*\)".*/\1/'`
	#echo "$bukiet filename: '$myFile'"
	if [ -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile ]; then
		mv -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile $ChannelsListPath/etc/enigma2/
	fi
done <$ChannelsListPath/etc/enigma2/bouquets.radio
echo "_(Analyzing TV bouquets)"
while read bukiet; do
	myFile=`echo $bukiet | grep "^#SERVICE[:]*"|sed 's/^#.*0:0:0:0://; s/^.*FROM BOUQUET "\(.*\)".*/\1/'`
	#echo "$bukiet filename: '$myFile'"
	if [ -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile ]; then
		mv -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile $ChannelsListPath/etc/enigma2/
	fi
done <$ChannelsListPath/etc/enigma2/bouquets.tv
##### OSTATECZNA SYNCHRONIZACJA #####
echo "_(Syncing channels list)..."
rm -rf /etc/enigma2/userbouquet*

cp -f $ChannelsListPath/etc/tuxbox/* /etc/tuxbox/
cp -f $ChannelsListPath/etc/enigma2/* /etc/enigma2/
##### Sprzatanie #####
rm -rf $ChannelsListPath

exit 0
