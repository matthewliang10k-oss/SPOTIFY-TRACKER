from login import sp
import json

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
  Playlist = getPlaylists()
  for playlist in Playlist['items']:
    playlist_info.append({
      "name": playlist['name'],
      "description": playlist['description'],
      "Track Length": playlist['items']['total'],
      "public": playlist['public'],
      "id": playlist['id'],
      "url": playlist["external_urls"]["spotify"],
      "image_link": playlist['images'][0]['url']})
  
  return playlist_info

def getPlaylistIcons():
    playlistInfo = getAllPlaylistinfo()
    playlistIcons = {}

    for playlist in playlistInfo:
        playlistIcons[playlist['id']] = {
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
   for playlists in playlistsInfo:
      if playlist_id == playlists['id']:
         return playlists['name']
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

if __name__ == "__main__":
  pass


