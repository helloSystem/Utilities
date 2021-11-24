#!/bin/sh

if ! [ $(id -u) = 0 ]; then
   echo "Please run as root"
   exit 1
fi

if [ -z "$1" ] ; then
  echo "Usage: $0 <minutes>"
  exit 1
fi


MINUTES="$1"

# https://wiki.archlinux.org/index.php/Display_Power_Management_Signaling#Setting_up_DPMS_in_X

cat > /usr/local/etc/X11/xorg.conf.d/10-monitor.conf <<EOF
Section "ServerFlags"
    Option "StandbyTime" "${MINUTES}"
    Option "SuspendTime" "${MINUTES}"
    Option "OffTime" "${MINUTES}"
    Option "BlankTime" "${MINUTES}"
EndSection

Section "ServerLayout"
    Identifier "ServerLayout0"
EndSection
EOF
