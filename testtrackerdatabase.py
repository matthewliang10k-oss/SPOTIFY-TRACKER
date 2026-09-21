import spotify_api as sa
import database as db


playback = sa.getCurrentPlayback()

if playback is None:
    print("Nothing is currently playing.")
    exit()


track = playback["item"]

print("Saving track:")
print(track["name"])
print(track["artists"][0]["name"])

db.save_track(track)

print("Track saved!")