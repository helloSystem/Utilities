#!/bin/sh

# Exit on errors
set -e

if ! [ $(id -u) = 0 ]; then
   echo "I am not root!"
   exit 1
fi

if [ -z "$1" ] ; then
  echo "USAGE: ${0} username password"
  exit 1
fi

username="$1"
password="$2"

echo "${username}:::::::::${password}" | adduser -f -
pw usermod "${username}" -s /usr/local/bin/zsh
pw groupmod wheel -m "${username}"
pw groupmod video -m "${username}"
pw groupmod webcamd -m "${username}"
pw groupmod cups -m "${username}"
