import requests
import streamlit as st
import pandas as pd

import spotify_api as sa
import analyzer as az
import charts as ct


# ============================================================
# SETUP
# ============================================================

st.set_page_config(
    page_title="Spotify Tracker",
    page_icon="🎵",
    layout="wide"
)

API_BASE = "http://127.0.0.1:5000"


# ============================================================
# AUTHENTICATION
# ============================================================

def check_authentication():

    try:

        response = requests.get(
            f"{API_BASE}/api/auth/me",
            timeout=5
        )

        if response.status_code == 200:

            return response.json()

        return {
            "authenticated": False
        }

    except requests.Timeout:

        st.error(
            "⏱️ The Spotify Tracker API took too long to respond."
        )

        st.info(
            "Make sure your Flask API is running on "
            "http://127.0.0.1:5000"
        )

        st.stop()

    except requests.RequestException as e:

        st.error(
            "Could not contact the Spotify Tracker API."
        )

        st.code(str(e))

        st.stop()


# IMPORTANT:
# There is ONLY ONE authentication check.

user = check_authentication()


# ============================================================
# LOGIN SCREEN
# ============================================================

if not user.get("authenticated", False):

    st.title("🎵 Spotify Tracker")

    st.write(
        "Connect your Spotify account to use Spotify Tracker."
    )

    st.link_button(
        "🟢 Login with Spotify",
        f"{API_BASE}/login",
        use_container_width=True
    )

    st.stop()


# ============================================================
# LOGGED-IN USER
# ============================================================

st.sidebar.success(
    f"Logged in as "
    f"{user.get('display_name', 'Spotify user')}"
)


# ============================================================
# LOGOUT
# ============================================================

if st.sidebar.button(
    "Log out",
    key="logout_button",
    use_container_width=True
):

    try:

        logout_response = requests.post(
            f"{API_BASE}/api/auth/logout",
            timeout=5
        )

        if logout_response.ok:

            st.success("Logged out successfully.")

            st.rerun()

        else:

            st.error(
                "Logout failed."
            )

            st.code(
                logout_response.text
            )

    except requests.Timeout:

        st.error(
            "Logout request timed out."
        )

    except requests.RequestException as e:

        st.error(
            "Could not contact the Spotify Tracker API."
        )

        st.code(str(e))


# ============================================================
# FORMATTING FUNCTIONS
# ============================================================

def format_listening_time(milliseconds):

    if milliseconds is None:
        return "0s"

    milliseconds = int(milliseconds)

    total_seconds = milliseconds // 1000

    hours = total_seconds // 3600

    minutes = (
        total_seconds % 3600
    ) // 60

    seconds = (
        total_seconds % 60
    )

    if hours > 0:

        return (
            f"{hours}h "
            f"{minutes}m "
            f"{seconds}s"
        )

    if minutes > 0:

        return (
            f"{minutes}m "
            f"{seconds}s"
        )

    return f"{seconds}s"


def format_player_time(milliseconds):

    if milliseconds is None:
        return "0:00"

    milliseconds = int(milliseconds)

    total_seconds = milliseconds // 1000

    minutes = total_seconds // 60

    seconds = total_seconds % 60

    return f"{minutes}:{seconds:02d}"


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("🎵 Spotify Tracker")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Playlist Analyzer"
    ],
    key="main_navigation"
)


# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

def show_overview():

    try:

        stats_response = requests.get(
            f"{API_BASE}/api/stats/overview",
            timeout=5
        )

        stats_response.raise_for_status()

        stats = stats_response.json()

    except requests.Timeout:

        st.error(
            "Dashboard statistics request timed out."
        )

        return

    except requests.RequestException as e:

        st.error(
            "Could not load dashboard statistics."
        )

        st.code(str(e))

        return


    total_listening = format_listening_time(
        stats.get("total_listening_ms")
    )

    total_plays = int(
        stats.get(
            "total_plays",
            0
        )
    )

    unique_tracks = int(
        stats.get(
            "unique_tracks",
            0
        )
    )

    unique_artists = int(
        stats.get(
            "unique_artists",
            0
        )
    )

    skips = int(
        stats.get(
            "skips",
            0
        )
    )


    if total_plays > 0:

        skip_rate = (
            skips / total_plays
        ) * 100

    else:

        skip_rate = 0


    st.subheader("Overview")

    st.caption(
        "Tracked Listening reflects only listening recorded "
        "by this application and may not represent your "
        "complete Spotify listening history."
    )


    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.metric(
            "Tracked Listening",
            total_listening
        )


    with col2:

        st.metric(
            "Total Plays",
            total_plays
        )


    with col3:

        st.metric(
            "Unique Tracks",
            unique_tracks
        )


    with col4:

        st.metric(
            "Unique Artists",
            unique_artists
        )


    with col5:

        st.metric(
            "Skip Rate",
            f"{skip_rate:.1f}%"
        )


# ============================================================
# CURRENTLY PLAYING
# ============================================================

@st.fragment(run_every="2s")
def show_currently_playing():

    try:

        current_response = requests.get(
            f"{API_BASE}/api/listening/current",
            timeout=5
        )

        current_response.raise_for_status()

        current = current_response.json()

    except requests.Timeout:

        st.warning(
            "Currently playing request timed out."
        )

        return

    except requests.RequestException as e:

        st.warning(
            "Could not load currently playing information."
        )

        return


    if not current.get("is_playing"):

        st.info(
            "Nothing is currently playing."
        )

        return


    current_track = current.get(
        "track_name",
        "Unknown Track"
    )

    current_artist = current.get(
        "artist_name",
        "Unknown Artist"
    )

    current_album = current.get(
        "album_name",
        "Unknown Album"
    )

    album_image = current.get(
        "album_image"
    )

    progress_ms = int(
        current.get(
            "progress_ms",
            0
        )
    )

    duration_ms = int(
        current.get(
            "duration_ms",
            0
        )
    )


    current_progress = format_player_time(
        progress_ms
    )

    current_duration = format_player_time(
        duration_ms
    )


    if duration_ms > 0:

        progress_ratio = (
            progress_ms / duration_ms
        )

        progress_ratio = max(
            0.0,
            min(progress_ratio, 1.0)
        )

    else:

        progress_ratio = 0.0


    with st.container(border=True):

        image_col, info_col = st.columns(
            [1, 3]
        )


        with image_col:

            if album_image:

                st.image(
                    album_image,
                    width=180
                )


        with info_col:

            st.subheader(
                current_track
            )

            st.write(
                f"**{current_artist}**"
            )

            st.write(
                current_album
            )

            st.progress(
                progress_ratio
            )

            st.caption(
                f"{current_progress} / "
                f"{current_duration}"
            )


# ============================================================
# LAST PLAYED
# ============================================================

@st.fragment(run_every="2s")
def show_last_played():

    try:

        current_response = requests.get(
            f"{API_BASE}/api/listening/current",
            timeout=5
        )

        current_response.raise_for_status()

        current = current_response.json()

    except requests.RequestException:

        current = {
            "is_playing": False,
            "track_id": None
        }


    try:

        recent_response = requests.get(
            f"{API_BASE}/api/listening/recent",
            timeout=5
        )

        recent_response.raise_for_status()

        recent_listening = recent_response.json()

    except requests.RequestException:

        st.warning(
            "Could not load recent listening history."
        )

        return


    if not recent_listening:

        st.info(
            "No listening history found."
        )

        return


    current_track_id = current.get(
        "track_id"
    )

    current_is_playing = current.get(
        "is_playing",
        False
    )


    last_played = None


    for play in recent_listening:

        play_track_id = play.get(
            "spotify_track_id"
        )

        source = play.get(
            "source"
        )


        if (
            current_is_playing
            and source == "live"
            and play_track_id == current_track_id
        ):

            continue


        last_played = play

        break


    if last_played is None:

        st.info(
            "No previous listening event found."
        )

        return


    play = last_played


    track_name = play.get(
        "track_name",
        "Unknown Track"
    )

    track_id = play.get(
        "spotify_track_id"
    )

    artist_name = play.get(
        "artist_name",
        "Unknown Artist"
    )

    played_at = play.get(
        "played_at",
        "Unknown"
    )

    milliseconds = play.get(
        "milliseconds_played"
    )

    skipped = play.get(
        "skipped"
    )

    source = play.get(
        "source",
        "unknown"
    )


    track_image = None


    if track_id:

        try:

            image_response = requests.get(
                f"{API_BASE}/api/tracks/{track_id}/image",
                timeout=5
            )

            image_response.raise_for_status()

            track_image = image_response.json().get(
                "image"
            )

        except requests.RequestException:

            track_image = None


    if milliseconds is None:

        listening_time = "Not available"

    else:

        listening_time = format_listening_time(
            milliseconds
        )


    if skipped == 1:

        status = "Skipped"

    elif skipped == 0:

        status = "Completed"

    else:

        status = "History event"


    with st.container(border=True):

        image_col, info_col = st.columns(
            [1, 3]
        )


        with image_col:

            if track_image:

                st.image(
                    track_image,
                    width=150
                )

            else:

                st.write(
                    "No artwork"
                )


        with info_col:

            st.subheader(
                track_name
            )

            st.write(
                f"**{artist_name}**"
            )

            st.write(
                f"Played at: {played_at}"
            )

            st.write(
                f"Listening time: {listening_time}"
            )

            st.write(
                f"Status: {status}"
            )

            st.caption(
                f"Source: {source}"
            )


# ============================================================
# DASHBOARD PAGE
# ============================================================

def show_dashboard():

    st.title("Spotify Tracker")

    st.caption(
        "Your personal Spotify listening analytics"
    )

    show_overview()

    st.subheader(
        "Currently Playing"
    )

    show_currently_playing()

    st.subheader(
        "Last Played"
    )

    show_last_played()


# ============================================================
# PLAYLIST ANALYZER
# ============================================================

def show_playlist_analyzer():

    st.title(
        "Playlist Analyzer"
    )


    try:

        playlist_names = (
            sa.getPlaylistNameandId()
        )

    except Exception as e:

        st.error(
            "Could not load Spotify playlists."
        )

        st.code(str(e))

        return


    if not playlist_names:

        st.warning(
            "No playlists found."
        )

        return


    st.sidebar.divider()

    st.sidebar.subheader(
        "Playlist"
    )


    selected_playlist = st.sidebar.selectbox(
        "Select a playlist",
        playlist_names.keys(),
        format_func=lambda x: playlist_names[x],
        key="playlist_selector"
    )


    st.subheader(
        f"Playlist Name: "
        f"{sa.getPlaylistName(selected_playlist)}"
    )


    playlist_icon = sa.getPlaylistIcon(
        selected_playlist
    )


    if playlist_icon:

        st.image(
            playlist_icon
        )


    st.warning(
        "If Spotify makes one of your tracks unavailable, "
        "it may affect the analyzer data. Do not blindly "
        "follow this data."
    )


    try:

        tracks = sa.getPlaylistTracks(
            selected_playlist
        )

        artists = az.getUniqueArtists(
            selected_playlist
        )


        with st.expander(
            "View Songs"
        ):

            st.subheader(
                f"Total songs: {len(tracks)}"
            )

            st.subheader(
                "Avg song duration: "
                f"{az.getAvgTrackDurationMin(selected_playlist)}"
            )

            st.subheader(
                "Total playlist duration: "
                f"{az.getTotalPlaylistDurationM(selected_playlist)}"
            )

            st.dataframe(
                pd.DataFrame(
                    {
                        "Songs": tracks
                    }
                ),
                use_container_width=True,
                hide_index=True
            )


        with st.expander(
            "View all artists"
        ):

            st.dataframe(
                pd.DataFrame(
                    {
                        "Artist": artists
                    }
                ),
                use_container_width=True,
                hide_index=True
            )


        with st.expander(
            "Artist Statistics"
        ):

            st.subheader(
                "Most Common Artist"
            )

            st.dataframe(
                pd.DataFrame(
                    [
                        az.getMostCommonArtist(
                            selected_playlist
                        )
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )


            st.subheader(
                "Least Common Artist"
            )

            st.dataframe(
                pd.DataFrame(
                    [
                        az.getLeastCommonArtist(
                            selected_playlist
                        )
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )


            st.subheader(
                "Top 5 Artists"
            )

            st.dataframe(
                pd.DataFrame(
                    az.getTop5Artists(
                        selected_playlist
                    )
                ),
                use_container_width=True,
                hide_index=True
            )


            percentage_chart = (
                ct.getPercentageChart(
                    selected_playlist
                )
            )


            st.subheader(
                "Artist Percentages"
            )

            st.plotly_chart(
                percentage_chart,
                use_container_width=True
            )


        with st.expander(
            "Release Years"
        ):

            release_chart = (
                ct.getReleaseYearChart(
                    selected_playlist
                )
            )


            if release_chart is not None:

                st.plotly_chart(
                    release_chart,
                    use_container_width=True
                )

            else:

                st.write(
                    "Release years not available."
                )


            st.subheader(
                "Oldest Song(s)"
            )

            st.dataframe(
                pd.DataFrame(
                    az.getOldestsong(
                        selected_playlist
                    )
                ),
                use_container_width=True,
                hide_index=True
            )


            st.subheader(
                "Newest Song(s)"
            )

            st.dataframe(
                pd.DataFrame(
                    az.getYoungestsong(
                        selected_playlist
                    )
                ),
                use_container_width=True,
                hide_index=True
            )


            st.subheader(
                "Release Years by Decade"
            )


            decade_chart = (
                ct.getDecadeChart(
                    selected_playlist
                )
            )


            if decade_chart is not None:

                st.plotly_chart(
                    decade_chart,
                    use_container_width=True
                )

            else:

                st.write(
                    "No data available for this playlist."
                )


            st.subheader(
                "Average release year: "
                f"{az.getavgReleaseYear(selected_playlist)}"
            )

            st.subheader(
                "Median release year: "
                f"{az.getMedianReleaseYear(selected_playlist)}"
            )


    except TypeError:

        st.error(
            "Something went wrong. A playlist or track "
            "may not be available right now."
        )

    except Exception as e:

        st.error(
            "Something went wrong while analyzing the playlist."
        )

        st.code(str(e))


# ============================================================
# PAGE ROUTING
# ============================================================

if page == "Dashboard":

    show_dashboard()

elif page == "Playlist Analyzer":

    show_playlist_analyzer()
