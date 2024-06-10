from pytube import YouTube, Playlist
from spotipy.oauth2 import SpotifyClientCredentials
import os, ytmusicapi, ffmpeg, spotipy, eyed3, requests, json

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
clear()
if not os.path.exists('credentials.json'):
    with open('credentials.json', 'w') as f:
        print("\033[33mThis program relies on the Spotify API to fetch metadata (since YouTube music doesn't make it easily accessible). Please enter your Spotify API credentials below.")
        print("You can get them by creating a Spotify Developer account at https://developer.spotify.com/dashboard/applications\033[0m")
        id = input("\nEnter your client ID: ")
        secret = input("Enter your client secret: ")
        json.dump({"client_id": id, "client_secret": secret}, f)
        clear()
        print("Credentials saved.\nIf necessary, you can update them by editing the 'credentials.json' file.\n")

with open('credentials.json', 'r') as f:
    credentials = json.load(f)

client_id = credentials['client_id']
client_secret = credentials['client_secret']
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

url = input("Enter the URL of the playlist: ")

playlist = Playlist(url)
ytmusic = ytmusicapi.YTMusic()
os.mkdir(playlist.title)
os.mkdir(playlist.title+"/.temp")
print("\033[33mSelected playlist: " + playlist.title + "\033[0m")

for video in playlist.video_urls:
    yt = YouTube(video)
    video_id = yt.video_id
    song_info = ytmusic.get_song(video_id)
    song_artist = song_info["videoDetails"]["author"]
    song_title = song_info["videoDetails"]["title"]
    print("\nDownloading " + song_artist + " - " + song_title)

    # Download + mp3 conversion
    finalOutput = playlist.title + "/" + song_artist + " - " + song_title + ".mp3"
    yt.streams.get_highest_resolution().download(output_path=playlist.title+ "/.temp", filename="output.mp4")
    ffmpeg.input(playlist.title+"/.temp/output.mp4").output(finalOutput).run(capture_stdout=True, capture_stderr=True)
    os.remove(playlist.title+"/.temp/output.mp4")

    # Metadata (will be saved if Spotify data can't be found)
    audiofile = eyed3.load(finalOutput)
    audiofile.tag.artist = song_artist
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
        audiofile.tag.images.set(3, requests.get(track['album']['images'][0]['url']).content, 'image/jpeg')

    else:
        print("\033[33mNOTE: No Spotify data found for " + song_artist + " - " + song_title + ". Only basic metadata will be added.\033[0m")

    audiofile.tag.save()
    print("\033[32mDone!\033[0m")

os.rmdir(playlist.title+"/.temp")
print("\033[32m\nAll downloads completed.\nYou can find your downloads at: \033[0m"+os.path.dirname(os.path.realpath(__file__))+"/"+playlist.title)
