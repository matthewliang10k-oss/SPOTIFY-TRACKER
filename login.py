import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")


if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URL]):
    raise ValueError(
        "One or more environment variables are missing!"
    )


SPOTIFY_SCOPE = (
    "playlist-read-private "
    "user-library-read "
    "user-read-playback-state "
    "user-read-currently-playing "
    "user-read-recently-played"
)


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CACHE_PATH = os.path.join(
    BASE_DIR,
    ".spotify_cache"
)


spotify_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URL,
    scope=SPOTIFY_SCOPE,
    cache_path=CACHE_PATH
)


sp = spotipy.Spotify(
    auth_manager=spotify_oauth
)
