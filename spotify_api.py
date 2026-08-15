from login import sp
import json

def getUserInfo():
    user = sp.current_user()

    return {
        "spotify_user_id": user["id"],
        "display_name": user["display_name"],
        "profile_image": user["images"][0]["url"] if user["images"] else None
    }

def getPlaylists():
 return sp.current_user_playlists(limit=50)

def getPlaylistID(name):
    Playlist = getPlaylists()

    for playlist in Playlist['items']:
        if playlist['name'].lower() == name.lower():
            return playlist['id']

    return None

def getAllPlaylistinfo():
    playlist_info = []
    playlists = getPlaylists()

    user = sp.current_user()
    user_id = user['id']

    for playlist in playlists['items']:
        playlist_info.append({
            "playlist_id": playlist['id'],
            "user_id": user_id,
            "name": playlist['name'],
            "description": playlist['description']
        })

    return playlist_info

def getPlaylistIcon(playlist_id):
   playlists = getPlaylists()
   if not playlists:
      return None
   for playlist in playlists['items']:
      if playlist_id == playlist['id']:
         return playlist['images'][0]['url']
   return None

def getPlaylistIcons():
    playlistInfo = getAllPlaylistinfo()
    playlistIcons = {}

    for playlist in playlistInfo:
        playlistIcons[playlist['playlist_id']] = {
            "name": playlist['name'],
            "image": playlist['image_link']
        }

    return playlistIcons

 

def getAllPlaylistinfoJSON():
  playlistInfo_JSON = json.dumps(getAllPlaylistinfo(), indent = 4)
  return playlistInfo_JSON


def getAllPlaylistName():
    return [playlist["name"] for playlist in getAllPlaylistinfo()]



def getPlaylistTracks(playlist_id):
    playlist_info = sp.playlist_items(playlist_id)
    tracks = []

    for item in playlist_info["items"]:
            if item["item"] is not None:
                tracks.append(item["item"]["name"])
    return tracks


def getPlaylistName(playlist_id):
    playlistsInfo = getAllPlaylistinfo()

    for playlist in playlistsInfo:
        if playlist_id == playlist['playlist_id']:
            return playlist['name']

    return None 
   

def getPlaylistNameandId():
   Names = getAllPlaylistName()
   NameandId = {}
   for name in Names:
      NameandId[f'{getPlaylistID(f'{name}')}'] = name
   return NameandId



def getTrackMetaData(playlist_id):
  Track_MetaData = (sp.playlist_items(playlist_id, additional_types = 'track'))
  return (Track_MetaData['items'])



def getTrackMetaDataJSON(playlist_id):
  TrackInfo_JSON = json.dumps(getTrackMetaData(playlist_id), indent = 4)
  return TrackInfo_JSON

def getArtistforTrack(playlist_id,index):
 all_tracks = getTrackMetaData(getPlaylistID(playlist_id))
 artists = all_tracks[index]['item']['artists']
 Creator = []
 for artist in artists:
     Creator.append(artist['name'])
 return Creator
# yo so ^^^ this function is kinda chopped u gotta call this without using getplaylist Id, u gotta put down the actual
# name of the playlist :sob:

def getAllArtists(playlist_id):
    all_artists = []
    allTracks = getTrackMetaData(playlist_id)
    for track in allTracks:
      if track.get("item") is None:
          continue
      artists = track['item']['artists']
      for artist in artists:
            all_artists.append(artist['name'])

    return all_artists

def getCurrentPlayback():
    return sp.current_playback()

def getRecentlyPlayed(limit=50, after=None):
    if after is None:
        return sp.current_user_recently_played(limit=limit)

    return sp.current_user_recently_played(
        limit=limit,
        after=after
    )


def getRecentlyPlayed(limit=50, after=None):

    if after is None:
        return sp.current_user_recently_played(limit=limit)

    return sp.current_user_recently_played(
        limit=limit,
        after=after
    )


def getRecentlyPlayed(limit=50, after=None):
    if after is None:
        return sp.current_user_recently_played(limit=limit)

    return sp.current_user_recently_played(
        limit=limit,
        after=after
    )

if __name__ == "__main__":
  pass


