#!/bin/sh

bukiety=`cat /etc/enigma2/bouquets.tv|grep '#SERVICE'|cut -d '"' -f2`

for plik in $bukiety
do
  if [ -e /etc/enigma2/$plik ]; then
    if [ `cat /etc/enigma2/$plik| grep -E ':streamlink|:YT-DL'|grep -Ec '#SERVICE :|#SERVICE 5001:|#SERVICE 5002:'` -gt 0 ];then
      sed -i 's/#SERVICE \(1\|5001\|5002\)\(.*:streamlink.*\|.*:YT-DL.*\)/#SERVICE 4097\2/g' /etc/enigma2/$plik
    fi
  fi
done
exit 0
