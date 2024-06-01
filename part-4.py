import json
from urllib.parse import quote as encode_uri_component
import requests
import time
from bs4 import BeautifulSoup as BSoup

SPOTIFY_TOKEN = ""
PLAYLIST_ID = ""

def search_track_on_spotify(title: str, artist: str):
	query = title + " " + artist
	r = requests.get(
		"https://api.spotify.com/v1/search", 
		params={
			"q": query,
			"type": "track",
		}, 
		headers={
			"Authorization": "Bearer " + SPOTIFY_TOKEN
		}
	)

	# If error occurred
	if r.status_code >= 400:
		# If we've been rate limited sleep until rate limit is over
		if "Retry-After" in r.headers:
			sleep_time = int(r.headers["Retry-After"])
		# If it's something else just sleep for 20 seconds
		else:
			sleep_time = 20

		print(f"Error occurred searching for song on Spotify for {title} by {artist}. Trying again after {sleep_time}s...", r.status_code)
		time.sleep(sleep_time)
		return search_track_on_spotify(title, artist)

	data = r.json()

	raw_track = data["tracks"]["items"][0]

	return {
		"title": raw_track["name"],
		"spotify_link": raw_track["external_urls"]["spotify"],
		"spotify_uri": raw_track["uri"],
		"spotify_id": raw_track["id"],
		"artist_name": raw_track["artists"][0]["name"],
		"album_name": raw_track["album"]["name"],
		"album_type": raw_track["album"]["album_type"],
	}

def add_songs_to_playlist(spotify_uris: list[str]):
	r = requests.post(
		f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks",
		json={
			"uris": spotify_uris
		},
		headers={
			"Authorization": "Bearer " + SPOTIFY_TOKEN
		}
	)

	# If error occurred
	if r.status_code >= 400:
		# If we've been rate limited sleep until rate limit is over
		if "Retry-After" in r.headers:
			sleep_time = int(r.headers["Retry-After"])
		# If it's something else just sleep for 20 seconds
		else:
			sleep_time = 20

		print(f"Error occurred for adding songs to playlist. Trying again after {sleep_time}s...", r.status_code)
		time.sleep(sleep_time)
		return add_songs_to_playlist(spotify_uris)

	print(f"Added {len(spotify_uris)} songs to playlist", r)

def get_spotify_uri_of_song_from_lastfm(title: str, artist: str):
	url = f"https://www.last.fm/music/{encode_uri_component(artist)}/_/{encode_uri_component(title)}"
	r = requests.get(url)

	if r.status_code >= 400:
		if r.status_code == 404:
			print(f"Couldn't find {title} by {artist}. SKIPPING.")
			return None

		elif r.status_code == 429:
			if "Retry-After" in r.headers:
				sleep_time = int(r.headers["Retry-After"])
			else:
				sleep_time = 20

			print(f"Rate limited when searching Last.fm for {title} by {artist}. Trying again after {sleep_time}s...", r.status_code)
			time.sleep(sleep_time)
			return get_spotify_uri_of_song_from_lastfm(title, artist)

		else:
			print(f"Unexpected error occurred searching Last.fm for {title} by {artist}. SKIPPING.", r.status_code)
			return None
		
	soup = BSoup(r.text, 'html.parser')
	all_spotify_links = soup.find_all("a", class_="play-this-track-playlink--spotify")

	if len(all_spotify_links) <= 0:
		return None

	spotify_web_url = all_spotify_links[0]["href"]
	spotify_id = spotify_web_url.split("/")[-1]

	return f"spotify:track:{spotify_id}"


tracks_data = []

with open("./for_sure_tracks.json") as f:
	tracks_data = tracks_data + json.load(f)
with open("./questionable_tracks.json") as f:
	tracks_data = tracks_data + json.load(f)


track_uris = []
for raw_track in tracks_data:
	track_uri = get_spotify_uri_of_song_from_lastfm(raw_track["title"], raw_track["artist"])

	if track_uri == None:
		print(f"{raw_track["title"]} {raw_track["artist"]} - Track uri not found; fetching from Spotify")
		spotify_track = search_track_on_spotify(raw_track["title"], raw_track["artist"])
		track_uris.append(spotify_track["spotify_uri"])
		print("RAW: ", raw_track["title"], raw_track["artist"], "| SPOTIFY: ", spotify_track["title"], spotify_track["artist_name"])


	else:
		track_uris.append(track_uri)
		print(f"Found track uri for {raw_track["title"]} {raw_track["artist"]}")

	time.sleep(0.3)

	if len(track_uris) >= 95:
		add_songs_to_playlist(track_uris)
		track_uris = []

if len(track_uris) > 0:
	time.sleep(0.3)
	add_songs_to_playlist(track_uris)
	track_uris = []