import spotipy
from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()
CLIENT_ID= os.getenv("CLIENT_ID")
CLIENT_SECRET= os.getenv("CLIENT_SECRET")
REDIRECT_URL= os.getenv("REDIRECT_URL")


if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URL]):
    raise ValueError("One or more environment variables are missing!")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URL,
        scope="playlist-read-private user-library-read"
    )
)

def main():
    print("Connecting to spotify...")

    user = sp.current_user()

    print("Connected!")
    print(f"Hello,",user["display_name"])

if __name__ == "__main__":
    main()
