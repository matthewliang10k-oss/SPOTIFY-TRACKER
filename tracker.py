import time
from datetime import datetime, timezone

import spotify_api as sa
import database as db


POLL_INTERVAL = 2


MAX_PROGRESS_JUMP = POLL_INTERVAL * 2.5 * 1000


def get_playlist_id(playback):
    return None

def save_current_session(
    spotify_user_id,
    track,
    played_at,
    milliseconds_played,
    skipped,
    playlist_id
):
    """
    Save the current listening session to MySQL.
    """

    if track is None:
        return

    if milliseconds_played <= 0:
        return

    db.save_listening_event(
        spotify_user_id=spotify_user_id,
        spotify_track_id=track["id"],
        played_at=played_at,
        milliseconds_played=int(milliseconds_played),
        skipped=skipped,
        spotify_playlist_id=playlist_id,
        source="live"
    )

    print(
        f"Saved: {track['name']} "
        f"({int(milliseconds_played)} ms) "
        f"[skipped={skipped}]"
    )


class LiveTracker:

    def __init__(self):
        user = sa.getUserInfo()

        self.spotify_user_id = user["spotify_user_id"]
        self.display_name = user["display_name"]


        self.current_track = None
        self.current_track_id = None
        self.current_playlist_id = None

 
        self.session_start = None


        self.previous_progress = None

        self.milliseconds_played = 0

    def check_current_track(self):
        """
        Check Spotify once and process the current playback.

        This is intentionally ONE polling cycle.
        backend.py can call this repeatedly.
        """

        playback = sa.getCurrentPlayback()


        if playback is None:
            return


        if playback.get("item") is None:
            return

        track = playback["item"]

        track_id = track["id"]
        progress = playback["progress_ms"]
        is_playing = playback["is_playing"]




        if self.current_track is None:

            self.current_track = track
            self.current_track_id = track_id
            self.current_playlist_id = get_playlist_id(playback)

            self.session_start = datetime.now(timezone.utc).replace(tzinfo=None)

            self.previous_progress = progress
            self.milliseconds_played = 0

            db.save_track(track)

            print(
                f"Started: "
                f"{track['name']} - "
                f"{track['artists'][0]['name']}"
            )

            return


        elif track_id != self.current_track_id:

            completion_threshold = 3000

            # IMPORTANT:
            # Use the duration of the PREVIOUS track.
            previous_duration = self.current_track["duration_ms"]

            finished_naturally = (
                self.previous_progress
                >= previous_duration - completion_threshold
            )

            skipped = 0 if finished_naturally else 1

            save_current_session(
                spotify_user_id=self.spotify_user_id,
                track=self.current_track,
                played_at=self.session_start,
                milliseconds_played=self.milliseconds_played,
                skipped=skipped,
                playlist_id=self.current_playlist_id
            )

            # Start da new session
            self.current_track = track
            self.current_track_id = track_id
            self.current_playlist_id = get_playlist_id(playback)

            self.session_start = datetime.now(timezone.utc).replace(tzinfo=None)

            self.previous_progress = progress
            self.milliseconds_played = 0

            db.save_track(track)

            print(
                f"Started: "
                f"{track['name']} - "
                f"{track['artists'][0]['name']}"
            )

            return



        else:

            progress_difference = (
                progress - self.previous_progress
            )

            if is_playing:

                # Normal playback
                if (
                    progress_difference >= 0
                    and progress_difference <= MAX_PROGRESS_JUMP
                ):
                    self.milliseconds_played += progress_difference

                # Seek backwards
                elif progress_difference < 0:
                    print(
                        f"Seek detected: "
                        f"{self.previous_progress} → {progress}"
                    )

                # Seek forwards
                else:
                    print(
                        f"Seek detected: "
                        f"{self.previous_progress} → {progress}"
                    )


            else:
                pass

            self.previous_progress = progress

    def stop(self):
        """
        Save the current listening session when the tracker stops.
        """

        print("\nStopping live tracker...")

        if self.current_track is not None:

            save_current_session(
                spotify_user_id=self.spotify_user_id,
                track=self.current_track,
                played_at=self.session_start,
                milliseconds_played=self.milliseconds_played,
                skipped=1,
                playlist_id=self.current_playlist_id
            )

        print("Live tracker stopped safely.")


def main():

    tracker = LiveTracker()

    print(
        f"Listening tracker started for "
        f"{tracker.display_name}"
    )

    print("Press CTRL+C to stop.")

    try:

        while True:

            tracker.check_current_track()

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:

        tracker.stop()


if __name__ == "__main__":
    main()