#!/bin/sh

if [ $(id -u) -ne 0 ]
  then echo Please run this script as root or using sudo!
  exit
fi

rm -rf /usr/bin/ytmusic-playlist-downloader
rm -rf /usr/share/applications/ytmusic-playlist-downloader.desktop
rm -rf /usr/share/icons/hicolor/128x128/apps/ytmusic-playlist-downloader.png

echo Uninstalled!
