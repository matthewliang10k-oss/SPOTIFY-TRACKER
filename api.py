from flask import Flask, jsonify, redirect, request
import mysql.connector
import spotify_api as sa
from dotenv import load_dotenv
from login import spotify_oauth
import os
import secrets
import time


# ============================================================
# SETUP
# ============================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "development-secret-key"
)


PROJECT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CACHE_PATH = os.path.join(
    PROJECT_DIR,
    ".spotify_cache"
)


# ============================================================
# AUTHENTICATION
# ============================================================

@app.route("/login")
def login():

    authorization_url = spotify_oauth.get_authorize_url()

    return redirect(authorization_url)


@app.route("/callback")
def callback():

    code = request.args.get("code")

    if not code:

        return jsonify({
            "error": "Spotify authorization failed."
        }), 400

    try:

        spotify_oauth.get_access_token(code)

        print("Spotify authorization successful.")
        print("Spotify token cached successfully.")

        return redirect(
            "http://localhost:8501/"
        )

    except Exception as e:

        print(
            f"Spotify authorization error: {e}"
        )

        return jsonify({
            "error": "Spotify authorization failed."
        }), 500


@app.route("/api/auth/me")
def auth_me():

    try:

        token_info = (
            spotify_oauth
            .cache_handler
            .get_cached_token()
        )

        if not token_info:

            return jsonify({
                "authenticated": False
            })


        user = sa.sp.current_user()

        return jsonify({

            "authenticated": True,

            "spotify_user_id":
                user.get("id"),

            "display_name":
                user.get(
                    "display_name",
                    "Spotify user"
                ),

            "profile_image": (
                user["images"][0]["url"]
                if user.get("images")
                else None
            )
        })

    except Exception as e:

        print(
            f"Authentication check error: {e}"
        )

        return jsonify({
            "authenticated": False
        })


@app.route(
    "/api/auth/logout",
    methods=["POST"]
)
def auth_logout():

    try:

        spotify_oauth.cache_handler.save_token_to_cache(
            {}
        )

        print(
            "Spotify authorization cache cleared."
        )

        return jsonify({
            "authenticated": False,
            "logged_out": True
        })

    except Exception as e:

        print(
            f"Logout error: {e}"
        )

        return jsonify({
            "authenticated": True,
            "logged_out": False,
            "error": str(e)
        }), 500





# ============================================================
# DATABASE
# ============================================================

def open_database():

    db = mysql.connector.connect(

        host="localhost",

        user="root",

        password="REMOVED",

        database="spotify_tracker"

    )

    return db


# ============================================================
# HEALTH
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "ok"
    })


# ============================================================
# LISTENING HISTORY
# ============================================================

@app.route("/api/listening/recent")
def recent_listening():

    db = open_database()

    cursor = db.cursor(
        dictionary=True
    )


    sql = """

        SELECT

            lh.play_id,

            lh.spotify_user_id,

            lh.spotify_track_id,

            t.name AS track_name,

            a.name AS artist_name,

            lh.played_at,

            lh.milliseconds_played,

            lh.skipped,

            lh.source,

            lh.spotify_playlist_id


        FROM listening_history lh


        JOIN tracks t

            ON lh.spotify_track_id =
               t.spotify_track_id


        JOIN artists a

            ON t.spotify_artist_id =
               a.spotify_artist_id


        ORDER BY
            lh.played_at DESC


        LIMIT 50

    """


    cursor.execute(sql)

    results = cursor.fetchall()


    cursor.close()

    db.close()


    return jsonify(results)


# ============================================================
# TRACKS
# ============================================================

@app.route("/api/tracks")
def tracks():

    db = open_database()

    cursor = db.cursor(
        dictionary=True
    )


    sql = """

        SELECT

            t.spotify_track_id,

            t.name AS track_name,

            a.name AS artist_name,

            t.duration_ms


        FROM tracks t


        JOIN artists a

            ON t.spotify_artist_id =
               a.spotify_artist_id


        ORDER BY
            t.name

    """


    cursor.execute(sql)

    results = cursor.fetchall()


    cursor.close()

    db.close()


    return jsonify(results)


# ============================================================
# ARTISTS
# ============================================================

@app.route("/api/artists")
def artists():

    db = open_database()

    cursor = db.cursor(
        dictionary=True
    )


    sql = """

        SELECT

            spotify_artist_id,

            name


        FROM artists


        ORDER BY
            name

    """


    cursor.execute(sql)

    results = cursor.fetchall()


    cursor.close()

    db.close()


    return jsonify(results)


# ============================================================
# OVERVIEW STATISTICS
# ============================================================

@app.route("/api/stats/overview")
def stats_overview():

    db = open_database()

    cursor = db.cursor(
        dictionary=True
    )


    sql = """

        SELECT

            COALESCE(
                SUM(milliseconds_played),
                0
            ) AS total_listening_ms,


            COUNT(*) AS total_plays,


            COUNT(
                DISTINCT spotify_track_id
            ) AS unique_tracks,


            COUNT(
                DISTINCT (
                    SELECT
                        spotify_artist_id

                    FROM tracks t

                    WHERE t.spotify_track_id =
                        listening_history.spotify_track_id
                )
            ) AS unique_artists,


            COALESCE(

                SUM(

                    CASE

                        WHEN skipped = 1
                        THEN 1

                        ELSE 0

                    END

                ),

                0

            ) AS skips


        FROM listening_history

    """


    cursor.execute(sql)

    result = cursor.fetchone()


    cursor.close()

    db.close()


    return jsonify(result)


# ============================================================
# CURRENTLY PLAYING
# ============================================================

@app.route("/api/listening/current")
def current_listening():

    try:

        playback = sa.getCurrentPlayback()


        if playback is None:

            return jsonify({
                "is_playing": False
            })


        track = playback.get(
            "item"
        )


        if track is None:

            return jsonify({
                "is_playing": False
            })


        album = track.get(
            "album",
            {}
        )


        album_images = album.get(
            "images",
            []
        )


        album_image = None


        if album_images:

            album_image = (
                album_images[0].get(
                    "url"
                )
            )


        artists = track.get(
            "artists",
            []
        )


        artist_name = (
            "Unknown Artist"
        )


        if artists:

            artist_name = (
                artists[0].get(
                    "name",
                    "Unknown Artist"
                )
            )


        return jsonify({

            "is_playing":
                playback.get(
                    "is_playing",
                    False
                ),


            "track_name":
                track.get(
                    "name",
                    "Unknown Track"
                ),


            "artist_name":
                artist_name,


            "track_id":
                track.get("id"),


            "album_name":
                album.get(
                    "name",
                    "Unknown Album"
                ),


            "album_image":
                album_image,


            "progress_ms":
                playback.get(
                    "progress_ms",
                    0
                ),


            "duration_ms":
                track.get(
                    "duration_ms",
                    0
                )

        })


    except Exception as e:

        print(
            f"Current playback error: {e}"
        )

        return jsonify({
            "is_playing": False
        })


# ============================================================
# TRACK IMAGE
# ============================================================

@app.route(
    "/api/tracks/<track_id>/image"
)
def track_image(track_id):

    try:

        track = sa.sp.track(
            track_id
        )


        album_images = (
            track
            .get("album", {})
            .get("images", [])
        )


        image = None


        if album_images:

            image = (
                album_images[0]
                .get("url")
            )


        return jsonify({
            "image": image
        })


    except Exception as e:

        print(
            f"Track image error: {e}"
        )

        return jsonify({
            "image": None
        })


# ============================================================
# START API
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
