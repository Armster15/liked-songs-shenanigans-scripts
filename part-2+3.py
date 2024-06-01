import json

THRESHOLD_FOR_SURE = 35
THRESHOLD_FOR_QUESTIONABLE = 10

# This serializing/deserializing logic is required because we can't use dicts as keys for dicts

def serialize_track(title: str, artist: str):
	# `ensure_ascii` flag required to __not__ turn something like "夜" to "\u591c"
	return json.dumps({ "title": title, "artist": artist }, ensure_ascii=False)

def deserialize_track(serialized_str: str):
	return json.loads(serialized_str)

with open("./lastfmstats.json", "r") as f:
	# {
	# 	username: string;
	# 	scrobbles: {
	# 		track: string;
	# 		artist: string;
	# 		album: string;
	# 		date: number; // Unix epoch
	# 	}[]
	# }
	contents = json.load(f)

times_track_scrobbled = {} # { [serialized_track: string]: number }

for scrobble in contents["scrobbles"]:
	key = serialize_track(scrobble["track"], scrobble["artist"])

	if key in times_track_scrobbled:
		times_track_scrobbled[key] = times_track_scrobbled[key] + 1
	else:
		times_track_scrobbled[key] = 1

filtered_tracks = [] # { title: string; artist: string; times_scrobbled: number; threshold: "questionable" | "for_sure" }

for serialized_track, times_scrobbled in times_track_scrobbled.items():
	track = deserialize_track(serialized_track)

	if times_scrobbled >= THRESHOLD_FOR_SURE:
		filtered_tracks.append({
			"title": track["title"],
			"artist": track["artist"],
			"times_scrobbled": times_scrobbled,
			"threshold": "for_sure",
		})

	elif times_scrobbled >= THRESHOLD_FOR_QUESTIONABLE:
		filtered_tracks.append({
			"title": track["title"],
			"artist": track["artist"],
			"times_scrobbled": times_scrobbled,
			"threshold": "questionable",
		})

# Sort `filtered_tracks` by number of times a song has been listened to
filtered_tracks.sort(key=lambda x: x["times_scrobbled"], reverse=False)

# Split `filtered_tracks` into two lists: `questionable_tracks` and `for_sure_tracks`
questionable_tracks = list(filter(lambda x: x["threshold"] == "questionable", filtered_tracks))
for_sure_tracks = list(filter(lambda x: x["threshold"] == "for_sure", filtered_tracks))

# Dump the contents of the two lists into JSON files
with open("./for_sure_tracks.json", "w") as f:
	json.dump(for_sure_tracks, f, indent=2, ensure_ascii=False)
with open("./questionable_tracks.json", "w") as f:
	json.dump(questionable_tracks, f, indent=2, ensure_ascii=False)
