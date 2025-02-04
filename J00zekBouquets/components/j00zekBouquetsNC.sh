#!/bin/sh
# 2019 @j00zek
#
#################### STALE ####################
if [ ! -e /usr/bin/pgrep ]; then
        opkg install procps 1>/dev/null 2>&1
        if [ ! -e /usr/bin/pgrep ]; then
                echo "Brakuje komponentu systemowego pgrep !!!"
                exit 0
        fi
fi
if [ ! -e /usr/bin/dvbsnoop ]; then
        opkg install dvbsnoop 1>/dev/null 2>&1
        if [ ! -e /usr/bin/dvbsnoop ]; then
                echo "Brakuje komponentu systemowego dvbsnoop !!!"
                exit 0
        fi
fi
if [ "`pgrep j00zekBouquets|grep -c 'j00zekBouquets'`" -gt 0 ];then
        echo "j00zekBouquets jest już uruchomiony !!!"
        exit 0
fi

myTITLE="--- j00zekBouquets NC v.19-01-2023 ---"

LASTSERVICE=`wget -q -O - http://127.0.0.1/web/subservices 2>/dev/null|grep 'servicereference'|sed 's/.*>\(.*\)<.*$/\1/'`
#echo $LASTSERVICE
#LAMEDBFILE=/tmp/lamedbj00zek
LAMEDBFILE=/etc/enigma2/lamedb
myPath=/tmp
rm -rf $myPath/jbtmp* >/dev/null
myPath=`mktemp -dp $myPath jbtmpXXXXXX`
#echo $myPath
#################### PODPROCEDURY ####################
#
czyszczenie() {
PLIKI='dvb.log bat.log tmp.txt nit.log sections.log services.log sdt.log batnit.log batnit.errors nctrans.log excluded.sids'
for i in $PLIKI
do
        [ -f /tmp/$i ] && rm -f /tmp/$i
        [ -f $myPath/$i ] && rm -f $myPath/$i
done
}
#
ZapToTransponder(){ #$1=dane transpondera
if [ $? -eq 0 ]; then
        if ! `echo $LASTSERVICE| grep -q ":$2:"`; then
                echo "Przełączanie..."
                wget -q  http://127.0.0.1/web/zap?sRef=$1 -O /dev/null 2>/dev/null
                [ $? -gt 0 ] && echo "Błąd przełączania kanału, sprawdź konfigurację wtyczki openwebif"
                sleep 10
        fi
fi
}
#
getNIT(){ #$1=ALLOWTRANSPONDERS
getNID_ALLOWTRANSPONDERS=$1
getNID_ALLOWTRANSPONDERS2=$2
#echo $getNID_ALLOWTRANSPONDERS
#echo $getNID_ALLOWTRANSPONDERS2
n1='^    Transport_stream_ID:'
n2='^    Original_network_ID:'
n3='^            Frequency:'
n4='^            Orbital_position:'
n5='^            Polarisation:'
n6='^            Kind:'
n7='^            Roll Off Faktor:'
n8='^            Modulation_type:'
n9='^            Symbol_rate:'
n10='^            FEC_inner:'
{ sleep 5; [ ! -s $myPath/nit.log ] && killall -9 dvbsnoop 1>/dev/null 2>&1; } &
dvbsnoop -n 12 -nph 0x10 |\
sed -n '/\('"$n1\|$n2\|$n3\|$n4\|$n5\|$n6\|$n7\|$n8\|$n9\|$n10"'\)/p'|\
sed 's/Transport_stream_ID:.*(0x\(....\)).*/TID:\1;/'|\
sed 's/Original_network_ID:.*(0x\(....\)).*/NID:\1;/'|\
sed 's/Frequency:.*(=[ ]*\(..\).\(.*\) GHz).*/FRQ:\1\20;/'|\
sed 's/Orbital_position:.*(=[ ]*\([0-9]*\)\.\([0-9]*\)).*/SAT:\1\2;/'|\
sed 's/\(SAT:192;\)/\1NAM:00c00000;/'|\
sed 's/\(SAT:130;\)/\1NAM:00820000;/'|\
sed 's/Polarisation:[ ]*\(.\).*/POL:\1;/'|\
sed 's/Kind:[ ]*\(.\).*/DS2:\1;/'|\
sed 's/Roll Off Faktor:[ ]*\(.\).*/ROL:\1;/'|\
sed 's/Modulation_type:[ ]*\(.\).*/MOD:\1;/'|\
sed 's/Symbol_rate:.*(=[ ]*\([0-9]*\)\.\([0-9]*\)).*/SRA:\1\200;/'|\
sed 's/FEC_inner:[ ]*\(.\).*/FEC:\1;/'|\
sed 's/^[ \t]*//' >$myPath/tmp.txt
cat $myPath/tmp.txt | tr -d '\n'|sed 's/TID:/\nTID:/g'|\
        sort -u >$myPath/nit.log
sed -i '/^$/d' $myPath/nit.log
sed -i 's/\(^.*;\)ROL:\(.\);\(.*\)/\1\3ROL:\2/' $myPath/nit.log
#wywalamy zbedne transpondery
if [ $getNID_ALLOWTRANSPONDERS != 'ALL' ];then
        cat $myPath/nit.log|egrep "$getNID_ALLOWTRANSPONDERS" >$myPath/tmp.txt
        mv -f $myPath/tmp.txt $myPath/nit.log
fi
if [ $getNID_ALLOWTRANSPONDERS2 != 'ALL' ];then
        while read TID; do
                sed -n "/$TID/p" <$myPath/nit.log >>$myPath/tmp.txt
        done <$getNID_ALLOWTRANSPONDERS2
        mv -f $myPath/tmp.txt $myPath/nit.log
fi
#mv -f $myPath/nit.log $myPath/nit.org
cat $myPath/nit.log | sed 's/^TID:\(....\).*$/\1/'>$myPath/tids.log
if [ ! -s $myPath/tids.log ];then 
        echo "Błąd pobierania danych o transponderach!!!"
        exit 0
fi
}
#
DumpStream(){
{ sleep 5; [ ! -s $myPath/dvb.log ] && killall -9 dvbsnoop 1>/dev/null 2>$1; } &
dvbsnoop -nph -n 500 -timeout 4000 0x11>$myPath/dvb.log
if [ ! -s $myPath/dvb.log ] || ! grep -q 'Original_network_ID: 318 ' $myPath/dvb.log >/dev/null 2>&1; then
        echo "No data available!!!!"
        echo "Please zap to any channel on correct transponder!!!"
        rm -f $myPath/dvb.log
        exit 0
fi
}
#################### Configuring system... ####################
StartTime=`date +%s`
czyszczenie
#echo
echo "$myTITLE"
echo
echo "Przełączanie na kanał nadający info o numeracji..."
sleep 10
LASTSERVICE=`wget -q -O - http://127.0.0.1/web/subservices 2>/dev/null|grep 'servicereference'|sed 's/.*>\(.*\)<.*$/\1/'`
##### init parameters $1 = bouquetID to scan, $2 =CLEARLAMEDB
if [ ! "$1" = "" ]; then
        DATA="$1"
else
        echo "Opcje: BouquetID [[CLEARLAMEDB|DONTCLEAR] [all|CustomLCN|1st|DEBUG]]"
        echo "Przyklad: j00zekBouquets 49188 CLEARLAMEDB DEBUG"
        DATA="49188PL" #NC+ only Polish transponders
fi
if [ "$2" = "DEBUG" ]; then
        DEBUG=1
        doABM=1
        doPROVIDER=1
        doOWN=1
elif [ "$2" = "CustomLCN" ]; then
        DEBUG=0
        doABM=1
        doPROVIDER=0
        doOWN=0
elif [ "$2" = "1st" ]; then
        DEBUG=0
        doABM=0
        doPROVIDER=0
        doOWN=1
elif [ "$2" = "prov" ]; then
        DEBUG=0
        doABM=0
        doPROVIDER=1
        doOWN=0
else
        DEBUG=0
        doABM=1
        doPROVIDER=1
        doOWN=1
fi
if [ -z "$3" ]; then
        SELECTEDSERVICE="1:0:1:1163:2AF8:13E:820000:0:0:0:"
else
        SELECTEDSERVICE=$3
fi
if [ -z "$4" ]; then
        ExcludeSIDs=0
else
        ExcludeSIDs=1
fi
if [ -z "$5" ]; then
        ZnacznikPustych="#SERVICE 1:832:D:0:0:0:0:0:0:0:: "
else
        ZnacznikPustych="$5"
fi

SELECTEDNID=`echo $SELECTEDSERVICE|cut -d':' -f5`
ZapToTransponder $SELECTEDSERVICE $SELECTEDNID
##### configure script for bouquetID update
PROVIDER='Unknown'
ALLOWTRANSPONDERS='ALL'
ALLOWTRANSPONDERS2='ALL'
BOUQUETFILE="userbouquet.ncplus.j00zekAutobouquet"
FILE="hd_sat_130_nc_plus_CustomLCN.xml"
if [ $DATA == "49186" ]; then
        WAITMESSAGE="Synchronizacja serwisów w lamedb, czas do 8 minut..."
        PROVIDER='NC+ HotBird & Astra'
elif [ $DATA == "49187" ]; then
        WAITMESSAGE="Synchronizacja serwisów w lamedb, czas do 8 minut..."
        PROVIDER='NC+ HotBird & Astra chyba'
elif [ $DATA == "49188" ]; then
        WAITMESSAGE="Synchronizacja serwisów w lamedb, czas do 5 minut..."
        PROVIDER='NC+ HotBird'
        ALLOWTRANSPONDERS='SAT:130'
elif [ $DATA == "49188PL" ]; then
        WAITMESSAGE="Synchronizacja serwisów w lamedb, czas do 3 minut..."
        DATA="49188"
        PROVIDER='NC+ Hotbird-PL'
        ALLOWTRANSPONDERS="SAT:130"
        [ -f /tmp/transponders.PL ] && ALLOWTRANSPONDERS2="/tmp/transponders.PL"
fi
if [ "$PROVIDER" = 'Unknown' ]; then
        echo "Nieznany dostawca !!!"
        exit 0
else
        echo "Wybrany dostawca: $PROVIDER"
fi
#################### NIT ####################
echo "_Zbieranie danych o transponderach..."
getNIT $ALLOWTRANSPONDERS $ALLOWTRANSPONDERS2
#################### Dumping dvb stream... ####################
echo "Pobieranie pakietów dvb z satelity..."
DumpStream
#################### SDT ####################
echo "Odczytywanie SDT..."
#trwa 6s
s1='^Transport_Stream_ID:'
s3='^    Service_id:'
s4='^            service_type:'
s5='^            service_provider_name:'
s6='^            Service_name:'
cat $myPath/dvb.log |\
        sed -n '/\('"$s1\|$s3\|$s4\|$s5\|$s6"'\)/p'|\
        sed 's/^[ ]*//'|\
        sed 's/"[ ]*--.*$/"/'|\
        sed 's/Transport_Stream_ID:.*(0x\(....\)).*/TID:\1/'|\
        sed 's/Service_id:.*(0x\(....\)).*/;SID:\1/'|\
        sed 's/service_type: \(.\).*/;TYP:\1/'|\
        sed 's/service_provider_name:[ ]*/;PRO:/'|\
        sed 's/Service_name:[ ]*/;SNA:/'>$myPath/sdttmp.txt
cat $myPath/sdttmp.txt | tr -d '\n'|sed 's/TID:/\nTTID:/g'|sed '/^$/d'|sort -u >$myPath/sdt.log
[ $DEBUG -eq 0 ] && rm -f $myPath/sdttmp.txt
#Cleaning SDT
while read -r TID
do
        sed -i "s/^T\(TID:$TID\)/\1/g" $myPath/sdt.log
done <$myPath/tids.log
sed -i '/^TTID:/d' $myPath/sdt.log
#################### BAT ####################
echo "Analizowanie Bouquet Association Table..."

grep -n "Bouquet_ID: $DATA" < $myPath/dvb.log | cut -d ":" -f1 >$myPath/tmp.txt

dvb=`sed 'q' $myPath/tmp.txt`
let dvb4=dvb+4
let dvb5=dvb+5
sec_num_first=`sed -n "$dvb4{p}" $myPath/dvb.log | cut -d " " -f2`
sec_num_last=`sed -n "$dvb5{p}" $myPath/dvb.log | cut -d " " -f2`
echo "Liczba sekcji referencyjnych: $sec_num_last"

if [ $sec_num_first -eq 0 ]; then
        sec_num_cycle=$sec_num_last
else
        sec_num_cycle=$(($sec_num_first-1))
fi

rm -f $myPath/sections.log
echoTitle=1
while read ln; do
        let dvb1=ln+4
        let dvb17=dvb1-17
        sec_num=`sed -n "${dvb1}{p}" $myPath/dvb.log | cut -d " " -f2`
        sed -n "$dvb17,/^CRC/p" $myPath/dvb.log|sed 's/\[.*\][ ]*&//'>>$myPath/sections.log
        if [ $echoTitle -eq 1 ];then
                echoTitle=0
                echo -ne "Znalezione sekcje: $sec_num@$dvb1"
        else
                echo -ne ", $sec_num@$dvb1"
        fi
        [ $sec_num -eq $sec_num_cycle ] && break
done <$myPath/tmp.txt
[ $echoTitle = 0 ] && echo

sed -n "/^    Transport_stream_ID:/,/^CRC/p" $myPath/sections.log|\
        egrep "Transport_stream_ID|Original_network_ID|^[ ]*00[0-9]0:[ ]*"|\
        sed 's/^    Transport_stream_ID:.*(0x\(....\)).*/TID:\1;/'|\
        sed 's/^    Original_network_ID:.*(0x\(....\)).*/NID:\1;DATA /'|\
        sed 's/^[ ]*00[0-9]0:[ ]*//'|\
        sed 's/   .*$//'|sed 's/\(.. .. .. .. \) /\1\n/g'|\
        sed 's/^ //'|sed 's/[ ]*$/ /'>$myPath/tmp.txt
cat $myPath/tmp.txt | tr -d '\n'|\
        sed 's/TID:/\nTID:/g'|sed '/^$/d'|\
        sed 's/; NID:/;NID:/'|\
        sed 's/ \(..\) \(..\)/ \1\2/g'|\
        grep -v 'NID:02be'|\
        sort -u >$myPath/batext.log
[ $DEBUG -eq 0 ] && rm -f $myPath/sections.log
[ $DEBUG -eq 0 ] && rm -f $myPath/dvb.log
#Cleaning batext.log
while read -r TID
do
        sed -i "s/^\(TID:$TID\)/OK\1/g" $myPath/batext.log
done <$myPath/tids.log
sed -i '/^TID:/d' $myPath/batext.log
sed -i 's/^OK\(TID:\)/\1/' $myPath/batext.log
[ $DEBUG -eq 0 ] && rm -f $myPath/tids.log

cat $myPath/batext.log |sed 's/^TID.*DATA//'|\
        sed 's/\(.... ....\) /\1\n/g'|sed 's/^ //'|\
        sed 's/\(....\) \(....\)/\2;\1/'|sed '/^$/d'|sort -u >$myPath/bat.log

#################### TRANSPONDERS in LAMEDB ####################
echo "Synchronizowanie transponderów w lamedb..."
#NAMESPACE:TID:NID
#00820000:1b58:013e
#       s FREQ:SRATE:POLARISATION:FEC:SATELLITE:INVERSION:FLAGS:DVBS2:MODULATION:ROLLOFF:PILOT
#       s 12111000:27500000:1    :3  :130      :2        :0     
#/ 
INVERSION=2 #Inversion_Unknown
FLAGS=0
PILOT=2 #Pilot_Unknown
echoHEADER=1
while IFS=';' read -r TID NID FREQ SATELLITE NAMESPACE POLARISATION DVBS2 MODULATION SRATE FEC ROLLOFF
do
        NAMESPACE=${NAMESPACE:4}
        TID=${TID:4}
        NID=${NID:4}
        if ! `grep -q "$NAMESPACE:$TID:$NID" $LAMEDBFILE`; then
                #echo "TID:$TID;NID:$NID"
                if `grep -q "TID:$TID;NID:$NID" $myPath/batext.log`; then
                        FREQ=${FREQ:4}
                        SRATE=${SRATE:4}
                        POLARISATION=${POLARISATION:4}
                        FEC=${FEC:4}
                        SATELLITE=${SATELLITE:4}
                        MODULATION=${MODULATION:4}
                        DVBS2=${DVBS2:4}
                        ROLLOFF=${ROLLOFF:4}
                        LINE1="$NAMESPACE:$TID:$NID"
                        if [ "$DVBS2" == "0" ]; then
                                LINE2="s $FREQ:$SRATE:$POLARISATION:$FEC:$SATELLITE:$INVERSION:$FLAGS"
                        else
                                LINE2="s $FREQ:$SRATE:$POLARISATION:$FEC:$SATELLITE:$INVERSION:$FLAGS:$DVBS2:$MODULATION:$ROLLOFF:$PILOT"
                        fi
                        sed -i "s/\(transponders\)/\1\n$LINE1\n\t$LINE2\n\//" $LAMEDBFILE
                        if [ $DEBUG -eq 1 ];then
                                if [ $echoHEADER -eq 1 ]; then
                                        echo -ne "Dodano do lamedb:"
                                        echoHEADER=0
                                fi
                                echo -ne " $TID,"
                        fi
                fi
        fi
done <$myPath/nit.log
[ $echoHEADER -eq 0 ] && echo
#################### SERVICES in LAMEDB ####################
echo "$WAITMESSAGE"
if [ ! -f $LAMEDBFILE ]; then
        echo "BŁĄD!!!:"
fi
#SID :NAMESPACE:TID :NID :TYP:0
#02e0:00820000 :1b58:013e:2  :0
#<nazwa programu>
#RDS
#p:PROVIDER,C:0000
#p:nc+,C:0000 
[ -f $myPath/batnit.log ] && rm -f $myPath/batnit.log
[ -f $myPath/batnit2.log ] && rm -f $myPath/batnit2.log
[ -f $myPath/batnit.errors ] && rm -f $myPath/batnit.errors
echoHEADER=1
while IFS=";" read -r ID SID 
do
        TID=`grep " $SID $ID" $myPath/batext.log|sed 's/^.*TID://'|cut -d ";" -f1`
        if [ "$TID" == "" ];then
                echo "$ID:$SID">>$myPath/batnit.errors
        else
                grep "TID:$TID" $myPath/sdt.log|grep ";SID:$SID"|sed "s/SID:/\nSID:/g"|grep "SID:$SID" |\
                sed 's/[,]*SID://;s/TYP://;s/PRO://;s/SNA:"//;s/"\;$//;s/"$//;s/\;$//'>$myPath/sdt.current
                #struktura sdt.current:SID;TYPE;SAT;ServiceNAME;
                IFS=";" read -r SDTSID TYP SATPROVIDER NAZWA <$myPath/sdt.current
                if [ $TYP -eq 1 ];then #tylko TV
                        grep "TID:$TID" $myPath/nit.log|\
                        sed 's/TID://;s/NID://;s/FRQ://;s/SAT://;s/NAM://;s/POL://;s/DS2://;s/MOD://;s/SRA://;s/FEC://;s/ROL://'>$myPath/nit.current
                        #struktura nit.current:TID;NID;FRQ;SAT;NAMESPACE;POL;DVBS2;MOD;SRA;FEC;ROL 
                        IFS=";" read -r TIDNIT NID FRQ SAT NAMESPACE POL DVBS2 MOD SRA FEC ROL<$myPath/nit.current
                        if ! `grep -q "$SID:$NAMESPACE:$TID:$NID" $LAMEDBFILE`; then
                                LINIA1="$SID:$NAMESPACE:$TID:$NID:$TYP:0"
                                LINIA2="$NAZWA"
                                LINIA3="p:$SATPROVIDER,C:0000"
                                sed -i "s/\(^services\)/\1\n$LINIA1\n$LINIA2\n$LINIA3/" $LAMEDBFILE
                                if [ $DEBUG -eq 1 ];then
                                        if [ $echoHEADER -eq 1 ]; then
                                                echo -ne "Dodano do lamedb:"
                                                echoHEADER=0
                                        fi
                                        echo -ne " $NAZWA,"
                                fi
                        fi
                        echo "$ID:$SID:$NAMESPACE:$NID:$TIDNIT;$TYP;$DVBS2;$SATPROVIDER;$NAZWA"|sed 's/:[0]*/;/g'|sed 's/&/\\&/'>>$myPath/batnit.log
                elif [ $TYP -eq 2 ]; then #dla radia
                        grep "TID:$TID" $myPath/nit.log|\
                        sed 's/TID://;s/NID://;s/FRQ://;s/SAT://;s/NAM://;s/POL://;s/DS2://;s/MOD://;s/SRA://;s/FEC://;s/ROL://'>$myPath/nit.current
                        #struktura nit.current:TID;NID;FRQ;SAT;NAMESPACE;POL;DVBS2;MOD;SRA;FEC;ROL 
                        IFS=";" read -r TIDNIT NID FRQ SAT NAMESPACE POL DVBS2 MOD SRA FEC ROL<$myPath/nit.current
                        if ! `grep -q "$SID:$NAMESPACE:$TID:$NID" $LAMEDBFILE`; then
                                LINIA1="$SID:$NAMESPACE:$TID:$NID:$TYP:0"
                                LINIA2="$NAZWA"
                                LINIA3="p:$SATPROVIDER,C:0000"
                                sed -i "s/\(^services\)/\1\n$LINIA1\n$LINIA2\n$LINIA3/" $LAMEDBFILE
                                if [ $DEBUG -eq 1 ];then
                                        if [ $echoHEADER -eq 1 ]; then
                                                echo -ne "Dodano do lamedb:"
                                                echoHEADER=0
                                        fi
                                        echo -ne " $NAZWA,"
                                fi
                        fi
                        echo "$ID:$SID:$NAMESPACE:$NID:$TIDNIT;$TYP;$DVBS2;$SATPROVIDER;$NAZWA"|sed 's/:[0]*/;/g'|sed 's/&/\\&/'>>$myPath/batnit2.log
                fi
        fi
done <$myPath/bat.log

[ $echoHEADER -eq 0 ] && echo
[ $DEBUG -eq 0 ] && rm -f $myPath/sdt.current
[ $DEBUG -eq 0 ] && rm -f $myPath/nit.current
[ $DEBUG -eq 0 ] && rm -f $myPath/bat.log
[ $DEBUG -eq 0 ] && rm -f $myPath/batext.log

if [ $ExcludeSIDs -eq 1 ];then
        echo "Pomijanie niechcianych kanałów..."
        cat /etc/enigma2/userbouquet.excludedSIDs.j00zekAutobouquet.tv|cut -d ':' -f4-5|sort -u >$myPath/excluded.sids
        while IFS=":" read SID TID; do
                #sed -i "s/^.*;$SID;.*;$TID;.*$//" $myPath/batnit.log
                sed -i "/;$SID;.*;$TID;/d" $myPath/batnit.log
        done <$myPath/excluded.sids
        [ $DEBUG -eq 0 ] && rm -f $myPath/excluded.sids
fi
#################### MANUAL BOUQUET CREATION ####################
#struktura batnit.log:ID;SID=3dcd;NAM=0640;NID;NID=013e;FRQ;TID=0640;TYP=1;DS2=TID;PRO="nc+";SNA="TVN HD"; 
if [ $doPROVIDER -eq 1 ];then
        echo "Tworzenie pliku $BOUQUETFILE.tv"
        if [ "$ZnacznikPustych" == "sortuj" ]; then
                echo "#NAME $PROVIDER od A do Z">$myPath/$BOUQUETFILE.tv
        else
                echo "#NAME $PROVIDER">$myPath/$BOUQUETFILE.tv
        fi
        ExpectedNumber=0
        loopsDone=0
        rm -f $myPath/numbers
        while IFS=";" read -r ID SID NAMESPACE NID TID TYP DVBS2 SATPROVIDER NAZWA; do
                CurrNumber=$(( 0x$ID ))
                [ $ExpectedNumber -eq 0 ] && ExpectedNumber=$CurrNumber
                if [ "$ZnacznikPustych" != "skasuj" ] && [ "$ZnacznikPustych" != "sortuj" ]; then
                        if [ $CurrNumber -gt $ExpectedNumber ];then
                                until [ $ExpectedNumber -eq $CurrNumber ]; do
                                        echo "#SERVICE 1:832:D:0:0:0:0:0:0:0:: ">>$myPath/$BOUQUETFILE.tv
                                        #echo "#DESCRIPTION ">>$myPath/$BOUQUETFILE.tv
                                        let ExpectedNumber=ExpectedNumber+1
                                        let loopsDone=loopsDone+1
                                        if [ $loopsDone -gt 1100 ]; then
                                                break
                                        fi
                                done
                        fi
                fi
                if [ "$TYP" == '1' ] ; then
                        echo "#SERVICE 1:0:1:$SID:$TID:$NID:$NAMESPACE:0:0:0::$NAZWA">>$myPath/$BOUQUETFILE.tv
                fi
                let ExpectedNumber=CurrNumber+1
                let loopsDone=loopsDone+1
                if [ $loopsDone -gt 1200 ]; then
                        echo "Przerywam po 1200 rekordach, reszta to śmiecie"
                        break
                fi
        done <$myPath/batnit.log
        if [ "$ZnacznikPustych" == "sortuj" ]; then
        echo "Sortowanie kanałów"
                sort -t ':' -k12 < $myPath/$BOUQUETFILE.tv > /etc/enigma2/$BOUQUETFILE.tv
        else
                cp -f $myPath/$BOUQUETFILE.tv /etc/enigma2/
        fi
        [ $DEBUG -eq 0 ] && rm -f $myPath/$BOUQUETFILE.tv
        #RADIO
        echo "Tworzenie pliku $BOUQUETFILE.radio"
        echo "#NAME $PROVIDER">$myPath/$BOUQUETFILE.radio
        ExpectedNumber=0
        rm -f $myPath/numbers
        while IFS=";" read -r ID SID NAMESPACE NID TID TYP DVBS2 SATPROVIDER NAZWA; do
                CurrNumber=$(( 0x$ID ))
                [ $ExpectedNumber -eq 0 ] && ExpectedNumber=$CurrNumber
                if [ $CurrNumber -gt $ExpectedNumber ];then
                        until [ $ExpectedNumber -eq $CurrNumber ]; do
                                echo "#SERVICE 1:832:D:0:0:0:0:0:0:0:: ">>$myPath/$BOUQUETFILE.tv
                                let ExpectedNumber=ExpectedNumber+1
                        done
                fi
                if [ "$TYP" == '2' ] ; then
                        echo "#SERVICE 1:0:1:$SID:$TID:$NID:$NAMESPACE:0:0:0::$NAZWA">>$myPath/$BOUQUETFILE.radio
                fi
                let ExpectedNumber=CurrNumber+1
        done <$myPath/batnit2.log
        [ $DEBUG -eq 0 ] && mv -f $myPath/$BOUQUETFILE.radio /etc/enigma2/ || cp -f $myPath/$BOUQUETFILE.radio /etc/enigma2/
fi
#################### UPDATING 1ST bouquet ####################
#struktura batnit.log:ID;SID=3dcd;NAM=0640;NID;NID=013e;FRQ;TID=0640;TYP=1;DS2=TID;PRO="nc+";SNA="TVN HD"; 
if [ $doOWN -eq 1 ];then
        FirstBouquet=`grep -v 'userbouquet.excludedSIDs.j00zekAutobouquet.tv' /etc/enigma2/bouquets.tv |grep -m 1 "^#SERVICE[:]*"|sed 's/^#.*:0:0:0://; s/^.*FROM BOUQUET "\(.*\)".*/\1/'`
        if [ -z "$FirstBouquet" ];then
                echo "Błąd przypisania nazwy pierwszego bukietu"
        elif [ ! -f /etc/enigma2/$FirstBouquet ];then
                echo "/etc/enigma2/$FirstBouquet nie istnieje !!!"
        elif [ "$FirstBouquet" != "$BOUQUETFILE.tv" ];then
                        BouquetName=`cat /etc/enigma2/$FirstBouquet|grep '#NAME'|tr -d '\r'|sed 's/:[1234567890-]*$//'|sed 's/, aktualizacja.*$//'`
                        UpdateDate=`date +%d-%m-%Y`
                        cat /etc/enigma2/$FirstBouquet|grep -v '#DESCRIPTION'|tr -d '\r'|tr -d '\n'|sed 's/\(#SERVICE\)/\n\1/g'|\
                        awk -F '::' '{ print tolower($1)"::"$2 }'|\
                        sed 's/#service/#SERVICE/'|sed 's/#name/#NAME/'|sed 's/:[:]*$/:/' >$myPath/$FirstBouquet
                        x=$(tail -c 1 $myPath/$FirstBouquet)
                        [ "$x" != "" ] && echo >>$myPath/$FirstBouquet # na wypadek, jak plik nie konczy sie znakiem nowej linii
                        [ -f /tmp/.ChannelsNotUpdated ] || (cp -f $myPath/$FirstBouquet /tmp/.ChannelsNotUpdated;sed -i "1s;^;/etc/enigma2/$FirstBouquet\n;" /tmp/.ChannelsNotUpdated)
                echo "Aktualizowanie bukietu $FirstBouquet"
                while IFS=";" read -r ID SID NAMESPACE NID TID TYP DVBS2 SATPROVIDER NAZWA; do
                        ServiceLine="1:0:1:$SID:$TID:$NID:$NAMESPACE:0:0:0::" #drugi dwukropek zeby wykluczyc iptv z podmiany
                        FullServiceLine="1:0:1:$SID:$TID:$NID:$NAMESPACE:0:0:0::$NAZWA"
                        sed -i "s/^\(#SERVICE \)$ServiceLine.*/\1$FullServiceLine/" $myPath/$FirstBouquet 2>/dev/null #updating record
                        sed -i "/^#SERVICE $ServiceLine/d" /tmp/.ChannelsNotUpdated 2>/dev/null #deleting updated record
                        if ! `grep -q "$FullServiceLine" $myPath/$FirstBouquet`; then
                                echo "#SERVICE $FullServiceLine" >>$myPath/$FirstBouquet
                        fi
                done <$myPath/batnit.log
                sed -i "s/\(#NAME.*\)/$BouquetName, aktualizacja $UpdateDate/" $myPath/$FirstBouquet
                [ $DEBUG -eq 0 ] && mv -f $myPath/$FirstBouquet /etc/enigma2/$FirstBouquet || cp -f $myPath/$FirstBouquet /etc/enigma2/$FirstBouquet
        fi
fi
#################### UPDATING E2 ####################
[ $DEBUG -eq 0 ] && czyszczenie
[ $DEBUG -eq 0 ] && rm -rf $myPath
EndTime=`date +%s`
let runningTime=EndTime-StartTime
echo "Zakończono w $runningTime s."
exit 0
