# YouTube Music Playlist Downloader
A command-line Python utility for downloading YouTube Music Playlists with ID3 tagging (title, artist, album, album art, track number and release date) at original YouTube upload quality, using Spotify as a resource for metadata.

## Requirements
### Spotify API
You are required to provide your own Spotify Client ID and Secret. To obtain these, go to https://developer.spotify.com/.
1. Log in, go to the dashboard and click "Create App"
2. Fill in mandatory text fields with anything, ensure Redirect URIs has one URL
3. Tick "Web API", then click "I understand..." and Save
4. Go to your new app and click on "Settings"
   
This page will contain your Client ID and Secret.
### Python
Ensure the latest version of Python 3 is installed. To install required libraries, clone the repository and run the following command within its directory:
```pip install -r requirements.txt```

## Usage
On first run, the program will ask you for your Spotify Client ID and Client Secret. Provide these as prompted.

You can then paste the URL for a YouTube or YouTube Music playlist and the program will do the rest. In the event that the program cannot find the song on Spotify, you'll be notified and only the title and artist metadata will be saved.

All downloaded playlists are put in their own directory within the same directory as main.py.
