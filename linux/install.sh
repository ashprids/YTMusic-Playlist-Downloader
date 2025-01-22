#!/bin/sh

if [ $(id -u) -ne 0 ]
  then echo Please run this script as root or using sudo!
  exit
fi

chmod +x ytmusic-playlist-downloader
chmod +x ytmusic-playlist-downloader.desktop

cp ytmusic-playlist-downloader /usr/bin/
cp ytmusic-playlist-downloader.desktop /usr/share/applications/
cp ytmusic-playlist-downloader.png /usr/share/icons/hicolor/128x128/apps/

echo Installed!
