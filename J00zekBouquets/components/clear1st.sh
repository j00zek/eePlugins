#!/bin/sh
#
# @2016 by j00zek
#
myFile="/tmp/.ChannelsNotUpdated"
[ -f $myFile ] || exit 0
bouquetFile=`head -n 1 $myFile`
[ -f $bouquetFile ] || exit 0
toDelete=`grep '#SERVICE 1:0' <$myFile`
[ -z "$toDelete" ] && exit 0

while read line           
do           
	if `echo $line|grep -q '#SERVICE 1:0'`;then
		sed -i "/$line/d" $bouquetFile 2>/dev/null
    fi
done <$myFile
rm -f $myFile 2>/dev/null