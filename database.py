import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def open_database():
    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    return db



def save_user(user):
    db = open_database()
    cursor = db.cursor()

    sql = """
        INSERT INTO users
        (spotify_user_id, display_name, profile_image)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            display_name = VALUES(display_name),
            profile_image = VALUES(profile_image)
    """

    cursor.execute(sql, (
        user["spotify_user_id"],
        user["display_name"],
        user["profile_image"]
    ))

    db.commit()

    cursor.close()
    db.close()

def save_playlists(playlists, spotify_user_id):
    db = open_database()
    cursor = db.cursor()

    sql = """
        INSERT INTO playlists
        (spotify_playlist_id, spotify_user_id, name, description)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            description = VALUES(description)
    """

    for playlist in playlists:
        cursor.execute(sql, (
            playlist["playlist_id"],
            spotify_user_id,
            playlist["name"],
            playlist["description"]
        ))

    db.commit()

    cursor.close()
    db.close()

def save_artist(artist_id, artist_name):
    db = open_database()
    cursor = db.cursor()

    sql = """
        INSERT INTO artists
        (spotify_artist_id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name)
    """

    cursor.execute(sql, (
        artist_id,
        artist_name
    ))

    db.commit()

    cursor.close()
    db.close()


def save_track(track):
    db = open_database()
    cursor = db.cursor()

    artist = track["artists"][0]

    # Make sure the artist exists first
    artist_sql = """
        INSERT INTO artists
        (spotify_artist_id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name)
    """

    cursor.execute(artist_sql, (
        artist["id"],
        artist["name"]
    ))

    track_sql = """
        INSERT INTO tracks
        (spotify_track_id, name, spotify_artist_id, duration_ms)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            spotify_artist_id = VALUES(spotify_artist_id),
            duration_ms = VALUES(duration_ms)
    """

    cursor.execute(track_sql, (
        track["id"],
        track["name"],
        artist["id"],
        track["duration_ms"]
    ))

    db.commit()

    cursor.close()
    db.close()


def save_listening_event(
    spotify_user_id,
    spotify_track_id,
    played_at,
    milliseconds_played,
    skipped,
    spotify_playlist_id=None,
    source="live"
):
    db = open_database()
    cursor = db.cursor()

    # First check whether this event was already recorded
    check_sql = """
        SELECT play_id, source, milliseconds_played
        FROM listening_history
        WHERE spotify_user_id = %s
          AND spotify_track_id = %s
          AND ABS(
              TIMESTAMPDIFF(
                  MICROSECOND,
                  played_at,
                  %s
              )
          ) <= %s * 1000000
        ORDER BY ABS(
            TIMESTAMPDIFF(
                MICROSECOND,
                played_at,
                %s
            )
        )
        LIMIT 1
    """

    tolerance_seconds = 10

    cursor.execute(
        check_sql,
        (
            spotify_user_id,
            spotify_track_id,
            played_at,
            tolerance_seconds,
            played_at
        )
    )

    existing = cursor.fetchone()

    # -------------------------------------------------
    # EVENT ALREADY EXISTS
    # -------------------------------------------------

    if existing is not None:

        play_id = existing[0]
        existing_source = existing[1]
        existing_milliseconds = existing[2]

        # If live tracking has better information,
        # update the history row instead of creating
        # a duplicate.
        if (
            source == "live"
            and existing_source == "history"
        ):
            update_sql = """
                UPDATE listening_history
                SET
                    milliseconds_played = %s,
                    skipped = %s,
                    spotify_playlist_id = %s,
                    source = 'live'
                WHERE play_id = %s
            """

            cursor.execute(
                update_sql,
                (
                    milliseconds_played,
                    skipped,
                    spotify_playlist_id,
                    play_id
                )
            )

            print(
                f"Merged live event with history event "
                f"(play_id={play_id})"
            )

        db.commit()
        cursor.close()
        db.close()

        return

    # -------------------------------------------------
    # NEW EVENT
    # -------------------------------------------------

    sql = """
        INSERT INTO listening_history
        (
            spotify_user_id,
            spotify_track_id,
            spotify_playlist_id,
            played_at,
            milliseconds_played,
            skipped,
            source
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            spotify_user_id,
            spotify_track_id,
            spotify_playlist_id,
            played_at,
            milliseconds_played,
            skipped,
            source
        )
    )

    db.commit()

    cursor.close()
    db.close()

def listening_event_exists_nearby(
    spotify_user_id,
    spotify_track_id,
    played_at,
    tolerance_seconds=10
):
    db = open_database()
    cursor = db.cursor()

    sql = """
        SELECT play_id
        FROM listening_history
        WHERE spotify_user_id = %s
          AND spotify_track_id = %s
          AND ABS(TIMESTAMPDIFF(MICROSECOND, played_at, %s))
              <= %s * 1000000
        LIMIT 1
    """

    cursor.execute(sql, (
        spotify_user_id,
        spotify_track_id,
        played_at,
        tolerance_seconds
    ))

    result = cursor.fetchone()

    cursor.close()
    db.close()

    return result is not None



def get_last_history_sync(spotify_user_id):
    db = open_database()
    cursor = db.cursor()

    sql = """
        SELECT last_synced_at
        FROM history_sync
        WHERE spotify_user_id = %s
    """

    cursor.execute(sql, (spotify_user_id,))
    result = cursor.fetchone()

    cursor.close()
    db.close()

    if result is None:
        return None

    return result[0]


def save_history_sync(spotify_user_id, synced_at):
    db = open_database()
    cursor = db.cursor()

    sql = """
        INSERT INTO history_sync
        (spotify_user_id, last_synced_at)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            last_synced_at = VALUES(last_synced_at)
    """

    cursor.execute(sql, (
        spotify_user_id,
        synced_at
    ))

    db.commit()

    cursor.close()
    db.close()