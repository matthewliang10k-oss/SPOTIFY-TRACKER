import spotify_api as sa
import database as db

user = sa.getUserInfo()

print(user)

db.save_user(user)

print("User saved!")

playlists = sa.getAllPlaylistinfo()

print(f"Found {len(playlists)} playlists")

print(playlists[0])

db.save_playlists(
    playlists,
    user["spotify_user_id"]
)

print("Playlists saved!")