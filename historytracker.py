import spotify_api as sa
import database as db
from datetime import datetime


def sync_recent_history():

    user = sa.getUserInfo()
    spotify_user_id = user["spotify_user_id"]

    print(f"Checking Spotify history for {user['display_name']}...")
    print(f"Spotify ID from API: {spotify_user_id}")

    last_sync = db.get_last_history_sync(spotify_user_id)

    print(f"Last sync returned from database: {last_sync}")

    # --------------------------------
    # GET RECENT HISTORY
    # --------------------------------

    if last_sync is None:

        print("No previous sync found. Getting recent history...")

    else:

        print(f"Last sync: {last_sync}")

    print("Requesting latest Spotify history...")

    # We fetch the recent history and filter it ourselves
    # using last_sync.
    recent = sa.getRecentlyPlayed(limit=50)

    # --------------------------------
    # CHECK RESPONSE
    # --------------------------------

    if not recent:

        print("Spotify returned None.")
        return

    items = recent.get("items", [])

    print(f"Spotify returned {len(items)} history items.")

    if not items:

        print("No listening history returned.")
        return

    # --------------------------------
    # PROCESS HISTORY
    # --------------------------------

    newest_play = None
    new_events = 0

    for item in items:

        track = item["track"]

        played_at = datetime.fromisoformat(
            item["played_at"].replace("Z", "+00:00")
        ).replace(tzinfo=None)

        # --------------------------------
        # IGNORE EVENTS WE ALREADY SYNCED
        # --------------------------------

        if last_sync is not None and played_at <= last_sync:
            continue

        # Keep track of the newest event
        if newest_play is None or played_at > newest_play:
            newest_play = played_at

        # --------------------------------
        # CHECK FOR DUPLICATE
        # --------------------------------

        already_tracked = db.listening_event_exists_nearby(
            spotify_user_id=spotify_user_id,
            spotify_track_id=track["id"],
            played_at=played_at
        )

        if already_tracked:
            continue

        # --------------------------------
        # SAVE NEW EVENT
        # --------------------------------

        db.save_track(track)

        db.save_listening_event(
            spotify_user_id=spotify_user_id,
            spotify_track_id=track["id"],
            spotify_playlist_id=None,
            played_at=played_at,
            milliseconds_played=None,
            skipped=None,
            source="history"
        )

        new_events += 1

        print(
            f"New history event: "
            f"{track['name']} - "
            f"{track['artists'][0]['name']} "
            f"at {played_at}"
        )

    # --------------------------------
    # UPDATE LAST SYNC
    # --------------------------------

    if newest_play is not None:

        db.save_history_sync(
            spotify_user_id,
            newest_play
        )

    # --------------------------------
    # RESULT
    # --------------------------------

    if new_events == 0:

        print("No new listening history found.")

    else:

        print(
            f"History sync complete. "
            f"Saved {new_events} new event(s)."
        )


if __name__ == "__main__":
    sync_recent_history()