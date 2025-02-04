#/usr/bin/bash
echo "############################################" >> /tmp/enigma2_cleanUp.log
echo "reportGS.sh initiated" >> /tmp/enigma2_cleanUp.log
echo "############################################" >> /tmp/enigma2_cleanUp.log
timePeriodOnSeconds=60
DeleteLogAfterSeconds=259200

currSkin=`cat /etc/enigma2/settings|grep 'config.skin.primary_skin='|cut -d '=' -f2|cut -d '/' -f1`
SkinModsPath="/usr/share/enigma2/$currSkin/mySkin"

currEPOC=`date +%s` #returns EPOC in seconds
echo curr EPOC=$currEPOC
lastGScount=0
GScont=0
for filename in `ls /hdd/dvbapp2_crash*.log 2>/dev/null`
do
    fileEPOC=`date -r $filename +%s`
    diffEPOC=$((currEPOC - fileEPOC))
    GScont=$((GScont+1))
    if [ $diffEPOC -lt $timePeriodOnSeconds ];then
        lastGScount=$((lastGScount+1))
    fi
    if [ $diffEPOC -lt $DeleteLogAfterSeconds ];then
        cat $filename|sed -n '/^Traceback/,/^[\*]*KERNEL LOG/p' > $filename.Traceback
    fi
    rm -f $filename
done

if [ $lastGScount -gt 1 ];then
    echo "Analyzed $GScont GS logs." >> /tmp/enigma2_cleanUp.log
    echo "Multiple GS's ($lastGScount) in short time detected !!!"
    echo "removing skin parts configuration"
    [ -e $SkinModsPath ] && rm -f $SkinModsPath/*.xml
    [ -e /etc/enigma2/skin_user_BlackHarmony.xml ] && rm -f /etc/enigma2/skin_user_BlackHarmony.xml
    [ -e /usr/share/enigma2/BlackHarmony/mySkin/skin_user_BlackHarmony.xml ] && rm -f /usr/share/enigma2/BlackHarmony/mySkin/skin_user_BlackHarmony.xml
    echo "Multiple GS's in short time detected, skin parts configuration has been deleted!!!" >> /tmp/enigma2_cleanUp.log
else
    echo "Analyzed $GScont GS logs. No issues found. :)"
    echo "Analyzed $GScont GS logs. No issues found. :)" >> /tmp/enigma2_cleanUp.log
fi
