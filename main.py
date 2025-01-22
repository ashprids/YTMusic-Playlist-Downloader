# YTMusic Playlist Downloader
# Created by: https://fridg3.org

# PyInstaller command:
# pyinstaller main.py -F -n "YTMusic Playlist Downloader" -c -i images/icon.png

from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials
import os, spotipy, ytmusicapi, eyed3, requests, json, re, gettext, subprocess, sys, platform
eyed3.log.setLevel("ERROR")  # Suppress eyed3 genre warnings

# Fixes translation error for executables
def noop_translation(*args, **kwargs):
    return gettext.NullTranslations()
gettext.translation = noop_translation

# A variable for compiling the script into an executable.
# This affects how certain OS-sensitive variables are set.
#- None = Python
#- 0 = Linux
#- 1 = Windows
environment = 0

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

clear()

system = platform.system()
if environment != None:
    if system == "Linux":
        config_dir = os.path.expanduser("~/.config/YTMusic-Playlist-Downloader")
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        config_dir = os.path.join(os.path.dirname(appdata), "Local", "YTMusic-Playlist-Downloader") if appdata else None
    else:
        config_dir = None
        print("Unknown operating system. Configuration directory will not be created.")
    config_file = os.path.join(config_dir, "config.json") if config_dir else 'config.json'
else:
    config_file = 'config.json'

if not os.path.exists(config_file):
    if config_dir:
        os.makedirs(config_dir)
    with open(config_file, 'w') as f:
        print("\033[33mThis program relies on the Spotify API to fetch metadata (since YouTube music doesn't make it easily accessible). Please enter your Spotify API credentials below.")
        print("You can get them by creating a Spotify Developer account at https://developer.spotify.com/dashboard/applications\033[0m")
        id = input("\nEnter your client ID: ")
        secret = input("Enter your client secret: ")
        clear()
        print("Credentials saved.\nIf necessary, you can update them by editing the 'config.json' file at "+ config_file +".\n")

        if environment == None:
            print("\033[33mFFmpeg is required for this program to work. You can download it from https://ffmpeg.org/download.html.\033[0m")
            ffmpeg_location = input("Input the directory of the FFmpeg executable: ")
            clear()
        elif environment == 0:
            ffmpeg_location = "/usr/bin/ffmpeg"
        elif environment == 1:
            base_location = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
            ffmpeg_location = os.path.join(base_location, 'ffmpeg.exe')

        directory = input("\033[33mWhere would you like to store downloaded playlists?\n\033[0mEnter a directory (or leave blank to use the default directory): ")
        if not directory:
            if environment == None:
                directory = "."
            else:
                directory = os.path.join(os.path.expanduser('~'), 'Music')

        json.dump({"client_id": id, "client_secret": secret, "ffmpeg_location": ffmpeg_location, "directory": directory}, f)
        clear()

with open(config_file, 'r') as f:
    config = json.load(f)

client_id = config['client_id']
client_secret = config['client_secret']
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

os.chdir(config['directory'])
update = False

print("\033[94m\033[1mYT Music Playlist Downloader\033[0m")
print("\033[92mCreated by: https://fridg3.org\n\033[0m")
print("--------------------------------------------------\n")

url = input("Enter the URL of the playlist:\033[32m ")
quality = input("\033[0mEnter the desired bitrate of the audio:\033[32m ")
ytmusic = ytmusicapi.YTMusic()

# Check FFmpeg is recognised properly
ffmpeg_executable = os.path.join(config['ffmpeg_location'])
if os.path.isfile(ffmpeg_executable):
    try:
        result = subprocess.run([ffmpeg_executable, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            input("\n\033[31mAn error occured while running FFmpeg.\nTry reinstalling FFmpeg or check the path in the 'config.json' file.\033[0m")
            exit()
    except Exception as e:
        input("\n\033[31mError when running FFmpeg:", e + "\nTry reinstalling FFmpeg, and if the error persists, contact me (https://fridg3.org/contact).\033[0m")
        exit()
else:
    if environment == 1:
        input("\n\033[31mFFmpeg could not be found.\nTry reinstalling the program, and if the error persists, contact me (https://fridg3.org/contact).\033[0m")
        exit()
    else:
        input("\n\033[31mFFmpeg is required to run this program.\nPlease download it, and try running the program again.\033[0m")
        exit()

ydl_opts = {
            'quiet': True,
            'noprogress': True,
            'format': 'bestaudio/best',
            'no_warnings': True,
            'outtmpl': '.temp/output.%(ext)s',
            'ffmpeg_location': config['ffmpeg_location'],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
        }

with YoutubeDL(ydl_opts) as ydl:
    print("\n\033[33mFetching playlist data, this may take a while...\033[0m")

    try:
        playlist = ydl.extract_info(url, download=False)
    except Exception as e:
        input(f"\033[31mAn error occurred while fetching the playlist data.\nPlease ensure the playlist link is correct, and there aren't any unavailable videos in the playlist.\033[0m ")
        exit()

    playlist_title = re.sub(r'[<>:"/\|?*]', '_', playlist['title'])
    if not os.path.exists(playlist_title):
        os.mkdir(playlist_title)
    else:
        print("\n\033[31mA folder with the name '" + playlist_title + "' already exists. Do you wish to update this playlist?\033[0m")
        update = input("Enter 'y' to update, or 'n' to cancel: ")
        if update.lower() != 'y':
            print("\033[31mOperation cancelled.\033[0m")
            exit()
        else:
            update = True
            
    if not os.path.exists('.temp'):
        os.mkdir('.temp')

    # Handle .m3u playlist file
    playlist_file_path = os.path.join(playlist_title, f"{playlist_title}.m3u")
    if not update:
        with open(playlist_file_path, 'w', encoding='utf-8') as playlist_file:
            playlist_file.write(f"#EXTM3U\n")

    print('\033[32mDownloading songs from playlist: "' + playlist['title'] + '"\033[0m')
    nodata = []
    for entry in playlist['entries']:
        video_id = entry['id']
        song_info = ytmusic.get_song(video_id)
        song_artist = song_info["videoDetails"]["author"]
        song_title = song_info["videoDetails"]["title"]

        # Sanitize the song_artist and song_title to remove invalid characters
        sanitized_artist = re.sub(r'[<>:"/\|?*]', '_', song_artist)
        sanitized_title = re.sub(r'[<>:"/\|?*]', '_', song_title)

        # Download + mp3 conversion
        finalOutput = playlist_title + '/' + sanitized_artist + ' - ' + sanitized_title + '.mp3'
        if os.path.exists(finalOutput):
            print("\n" + song_artist + " - " + song_title + " is already downloaded. \n\033[33mSkipping...\033[0m")
            continue
        print("\nDownloading " + song_artist + " - " + song_title)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([entry['webpage_url']])

        # Move and rename the downloaded file
        os.rename('.temp/output.mp3', finalOutput)

        # Add song to .m3u playlist file
        with open(playlist_file_path, 'a', encoding='utf-8') as playlist_file:
            playlist_file.write(f"#EXTINF:-1,{song_artist} - {song_title}\n")
            playlist_file.write(sanitized_artist + ' - ' + sanitized_title + '.mp3\n')

        # Metadata (will be saved if Spotify data can't be found)
        audiofile = eyed3.load(finalOutput)
        audiofile.tag.artist = song_artist
        audiofile.tag.album_artist = song_artist
        audiofile.tag.title = song_title

        # Metadata from Spotify
        query = f"track:{song_title} artist:{song_artist}"
        results = sp.search(q=query, limit=1, type='track')
        if results['tracks']['items']:

            track = results['tracks']['items'][0]
            audiofile.tag.album = track['album']['name']
            audiofile.tag.artist = track['artists'][0]['name']
            release_date = int(track['album']['release_date'].split('-')[0])
            audiofile.tag.recording_date = eyed3.core.Date(year=release_date)
            audiofile.tag.track_num = track['track_number']
            genres = sp.artist(track['artists'][0]['id'])['genres']
            audiofile.tag.genre = genres[0].capitalize() if genres else ''
            audiofile.tag.images.set(3, requests.get(track['album']['images'][0]['url']).content, 'image/jpeg')

        else:
            print("\033[33mNOTE: No Spotify data found for " + song_artist + " - " + song_title + ". Only title and artist metadata will be added.\033[0m")
            nodata.append(song_artist + " - " + song_title)
        
        audiofile.tag.save()
        print("\033[32mDone!\033[0m")
  
os.rmdir('.temp')
clear()
if nodata:
    print("\n\033[33mThe following songs couldn't have their metadata fetched from Spotify:\033[0m")
    for song in nodata:
        print(song)

if os.name == 'nt':
    input("\033[32m\nPlaylist completed. You can find your downloads at:\n\033[33m" + config['directory'] + "\\" + playlist_title + "\033[0m\n")
else:
    input("\033[32m\nPlaylist completed. You can find your downloads at:\n\033[33m" + config['directory'] + "/" + playlist_title + "\033[0m\n")

exit()
