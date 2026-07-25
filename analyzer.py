from spotify_api import *
import spotipy
import json
import pandas 
import statistics
from collections import Counter

# print(getTotalPlaylistDuration(getPlaylistID("composition study")))# 
#an empty list behaves like a false statement during an if statement for some reason wtf
#when using these modules you will need to import spotipy api, then pass in the arguement from the ID, enter the name before hand)
def getTotalTrackNum(playlist_id):
    if getPlaylistTracks(playlist_id) is None:
        return None
    return int(len((getPlaylistTracks(playlist_id))))


def getTotalPlaylistDurationMS(playlist_id):
    tracks = getTrackMetaData(playlist_id)
    if tracks is None:
        return None
    totalTrackDuration = 0
    for track in tracks:
            totalTrackDuration += track['item']['duration_ms']
    return int(round(totalTrackDuration))

def getTotalPlaylistDurationS(playlist_id):
    tracks = getTotalPlaylistDurationMS(playlist_id)
    if tracks is None:
        return None
    return int(tracks/1000)

def getTotalPlaylistDurationM(playlist_id):
    tracks = getTotalPlaylistDurationS(playlist_id)
    if tracks is None:
        return None
    return f"{int(tracks//60)} minutes and {int(tracks%60)} seconds"



def getAvgTrackDurationMS(playlist_id):
     try:
      avgTrackDurationMS = (getTotalPlaylistDurationMS(playlist_id)/getTotalTrackNum(playlist_id))
      return int(round(avgTrackDurationMS))
     except ZeroDivisionError:
          return None

def getAvgTrackDurationSec(playlist_id):
     avg_ms = getAvgTrackDurationMS(playlist_id)
     if avg_ms is None:
         return None
     return int(round(avg_ms)/1000)


def getAvgTrackDurationMin(playlist_id):
     totalSeconds = getAvgTrackDurationSec(playlist_id)
     if totalSeconds is None:
         return None
     duration ={'minutes':int(totalSeconds//60),
                'seconds': int(totalSeconds%60)} 
     return f"{int(totalSeconds//60)} minutes and {int(totalSeconds%60)} seconds"


def getLongestSongDuration(playlist_id):
     tracks = getTrackMetaData(playlist_id)
     if not tracks:     
         return None
     track_lengths = []
     for track in tracks:
          track_lengths.append(track['item']['duration_ms'])
     track_lengths = int(max(track_lengths))
     return track_lengths

def getShortestSongDuration(playlist_id):
     tracks = getTrackMetaData(playlist_id)
     if not tracks:     
         return None
     track_lengths = []
     for track in tracks:
          track_lengths.append(track['item']['duration_ms'])
     track_lengths = int(min(track_lengths))
     return track_lengths

def getShortestSongName (playlist_id):
     shortest_song = getShortestSongDuration(playlist_id)
     if shortest_song is None:
          return None
     all_tracks = getTrackMetaData(playlist_id)
     for tracks in all_tracks:
      if int(shortest_song) == int(tracks['item']['duration_ms']):
          return tracks['item']['name']
     

def getLongestSongName(playlist_id):
     longest_song = getLongestSongDuration(playlist_id)
     if longest_song is None:
          return None
     all_tracks = getTrackMetaData(playlist_id)
     for tracks in all_tracks:
      if int(longest_song) == int(tracks['item']['duration_ms']):
          return tracks['item']['name']


def getArtistcounts(playlist_id):
     artists = getAllArtists(playlist_id)
     if artists is None:
        return None
     if not artists:
        return None
     return Counter(artists)

def getMostCommonArtist(playlist_id):
    countArtists = getArtistcounts(playlist_id)
    if not countArtists:
        return None
    frequency = float('-inf')
    commonArtists = []
    for artist in countArtists:
          if countArtists[artist] > frequency:
               frequency = countArtists[artist]
               commonArtists = [artist]
          elif countArtists[artist] == frequency:
              commonArtists.append(artist)

    if len(commonArtists) == 1:
        return {"artists":commonArtists,
                 "count": frequency}
    else:
        return {"artists": commonArtists,
                "count": frequency} 

def getLeastCommonArtist(playlist_id):
    countArtists = getArtistcounts(playlist_id)
    if not countArtists:
        return None
    frequency = float('inf')
    commonArtists = []
    for artist in countArtists:
          if countArtists[artist] < frequency:
               frequency = countArtists[artist]
               commonArtists = [artist]
          elif countArtists[artist] == frequency:
              commonArtists.append(artist)

    if len(commonArtists) == 1:
        return {"artists":commonArtists,
                 "count": frequency}
    else:
        return {"artists": commonArtists,
                "count": frequency} 
         
            
def getUniqueArtists(playlist_id):
 allArtists = getAllArtists(playlist_id)
 if allArtists is None:
    return None
 uniqueArtists = []
 for artist in allArtists:
     if artist not in uniqueArtists:
         uniqueArtists.append(artist)
 return uniqueArtists

def getExplicitSongPercentage(playlist_id):
    all_tracks = getTrackMetaData(playlist_id)
    explicit_count = 0
    if all_tracks is None:
        return None
    if len(all_tracks) == 0:
        return 0

    for track in all_tracks:
        if track['item']['explicit']: #dont need the true because it automatically assumes its true i think
            explicit_count +=1
    explicit_ratio = explicit_count/len(all_tracks)
    return explicit_ratio * 100
            

def getReleaseYears(playlist_id):
 tracks = getTrackMetaData(playlist_id)
 if tracks is None:
     return None
 if not tracks:
     return None
 all_dates = []
 for track in tracks:
     all_dates.append({
         'name': track['item']['name'], 'released': int(track['item']['album']['release_date'][:4])
     })
 return all_dates

def getOldestsong(playlist_id):
    dates = getReleaseYears(playlist_id)
    if not dates:
        return None
    oldest_song = float('inf')
    oldest_songs = []
    oldest_name = ''
    for date in dates:
        if int(date['released']) < oldest_song:
            oldest_song = int(date['released'])
            oldest_name = date['name']
            oldest_songs = []
            oldest_songs.append(date)
        elif int(date['released']) == oldest_song:
            oldest_songs.append(date)    
    
    if len(oldest_songs) > 1:
     return oldest_songs
    else:
     return oldest_songs


def getYoungestsong(playlist_id):
    dates = getReleaseYears(playlist_id)
    if not dates:
        return None
    youngest_song = float('-inf')
    youngest_songs = []
    youngest_name = ''
    for date in dates:
        if int(date['released']) > youngest_song:
            youngest_song = int(date['released'])
            youngest_name = date['name']
            youngest_songs = []
            youngest_songs.append(date)
        elif int(date['released']) == youngest_song:
            youngest_songs.append(date)    
    
    if len(youngest_songs) > 1:
     return youngest_songs
    else:
     return youngest_songs

    

def getOnlyReleaseYears(playlist_id):
    dates = getReleaseYears(playlist_id)
    release_years_only = []
    for date in dates:
        release_years_only.append(int(date['released']))    

    if not release_years_only:
        return None
    return release_years_only


def getavgReleaseYear(playlist_id):
    release_years_only = getOnlyReleaseYears(playlist_id)

    if not release_years_only:
        return None
    
    return round(sum(release_years_only)/len(release_years_only))
        
def getMedianReleaseYear(playlist_id):
    release_years_only = getOnlyReleaseYears(playlist_id)
    if not release_years_only:
        return None
    median = statistics.median(release_years_only)
    return median

def getSongsbyDecade(playlist_id):
    release_years_only = getOnlyReleaseYears(playlist_id)
    if not release_years_only:
        return None
    release_years_only.sort()
    year_decade = []
    for years in release_years_only:
     year_decade.append((f"{(years//10)*10}s"))
    if not year_decade:
        return None
    
    year_decade_count = Counter(year_decade)
    release_decades = []
    for count in year_decade_count:
        release_decades.append({
        'decade': count,
        'count': int(year_decade_count[count])
        })
    return release_decades

def getTop5Artists(playlist_name):
   countArtists = getArtistcounts(playlist_name)
   top5_artists = []
   for artist, count in countArtists.most_common(5):
       if len(top5_artists) < 5:
           top5_artists.append({'artist': artist,
                               'count': count})
    
   if not top5_artists:
       return None
   return top5_artists
    


def getTop5ArtistsAllTime():
    playlistname = getAllPlaylistName()
    if not playlistname:
        return None
    artistlist = []
    for playlist in playlistname:
        if playlist is None:
            continue
        artistlist.append(getAllArtists(getPlaylistID(playlist)))
    allartists = []
    for artists in artistlist:
        for artist in artists:
            allartists.append(artist)
    if not allartists:
        return None 
    top5artists = Counter(allartists)
    top5artist = []

    for artists, count in top5artists.most_common(5):
        if len(top5artist) < 5:
           top5artist.append({'artist': artists,
                               'count': count})

    return top5artist

def getArtistpercentage(playlist_name):
    artists = getAllArtists(playlist_name)
    artistcounts = Counter(artists)
    if not artists or not artistcounts:
        return None
    
    artistcount = []
    for artist in artistcounts:
        artistcount.append({
            'artist': artist,
            'count': artistcounts[artist]
          })
    if not artistcount:
        return None
    artistpercentage = []    
    for artist in artistcount:
        percentage = ((artist['count'])/len(artists)*100)
        artistpercentage.append({'artist': artist['artist'],
                                  'percentage': f"{percentage}%"})
    return artistpercentage


if __name__ == "__main__":
    pass






