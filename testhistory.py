import spotify_api as sa

user = sa.getUserInfo()

print(f"Checking recent history for {user['display_name']}...\n")

recent = sa.getRecentlyPlayed(limit=10)

for item in recent["items"]:
    track = item["track"]

    print(
        f"{item['played_at']} | "
        f"{track['name']} - "
        f"{track['artists'][0]['name']}"
    )