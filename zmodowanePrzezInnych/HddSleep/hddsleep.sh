#!/bin/sh

### BEGIN INIT INFO
# Provides:          hd-idle
# Required-Start:    $local_fs
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: start hd-idle daemon (spin down idle hard disks)
### END INIT INFO


PATH=/sbin:/bin:/usr/sbin:/usr/bin

DAEMON=/usr/bin/hd-idle
HD_IDLE_OPTS="-i 600"
START_HD_IDLE=false

[ -r /etc/enigma2/hddsleep ] && . /etc/enigma2/hddsleep

if [ "$START_HD_IDLE" != "true" -a "$1" != "stop" ] ; then
  echo "START_HD_IDLE is false"
  exit 0
fi

# See if the daemon is there
test -x $DAEMON || exit 0

case "$1" in
	start)
    echo "starting the hd-idle daemon: hd-idle"
		start-stop-daemon --start --quiet --exec $DAEMON -- $HD_IDLE_OPTS
    echo "done."
		;;

	stop)
    echo "stopping the hd-idle daemon: hd-idle"
		start-stop-daemon --stop --quiet --exec $DAEMON
		echo "done."
		;;

	restart|force-reload)
		$0 stop && sleep 2 && $0 start
		;;

	*)
		echo "Usage: ./hd-idle start/stop/restart/force-reload"
		exit 1
		;;
esac
