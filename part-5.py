import requests
import time

SPOTIFY_TOKEN = ""
PLAYLIST_ID = ""

spotify_track_ids = []

def like_song_ids(ids: list[str]):
	r = requests.put(
		"https://api.spotify.com/v1/me/tracks", 
		json={
			"ids": ids
		},
		headers={
			"Authorization": "Bearer " + SPOTIFY_TOKEN
		}
	)

	print(f"Dumped {len(ids)} in liked songs", r)

def recursively_get_spotify_track_ids_from_playlist(url=f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"):
	r = requests.get(
		url,
		headers={
			"Authorization": "Bearer " + SPOTIFY_TOKEN
		}
	)

	data = r.json()

	print(r)
	print(f"Fetched {len(data["items"])} song ids from offset {data["offset"]}")

	for item in data["items"]:
		if "track" not in item or item["track"] == None:
			print(f"Warning: item at offset {data["offset"]} does not have a valid track object", item)
		else:
			spotify_track_ids.append(item["track"]["id"])
	
	if "next" in data and data["next"] != None:
		recursively_get_spotify_track_ids_from_playlist(url=data["next"])
		time.sleep(0.5)

	else:
		print("Done fetching song ids")

# Fetch all songs from playlist
recursively_get_spotify_track_ids_from_playlist()

# Now go through every track id and add to liked songs in increments of 50 (that is maximum)
batched_track_ids = []

for track_id in spotify_track_ids:
	batched_track_ids.append(track_id)

	if len(batched_track_ids) >= 49:
		like_song_ids(batched_track_ids)
		batched_track_ids = []
		time.sleep(0.5)

if len(batched_track_ids) > 0:
	like_song_ids(batched_track_ids)
	batched_track_ids = []
	time.sleep(0.5)
