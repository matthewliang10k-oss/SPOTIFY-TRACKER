import plotly.express as pz
import plotly as pt
import analyzer as az
import pandas as pd
import spotify_api as sa

def getDecadeChart(playlist_id):
 decade_data = az.getSongsbyDecade(playlist_id)
 if decade_data is None:
  return None
 decade_dataframe = pd.DataFrame(decade_data)
 decade_fig = pz.bar(decade_dataframe,
         x = "decade",
         y= "count",
         title="Songs By Decade")
 return decade_fig

def getPercentageChart(playlist_id):
 artistpercents = az.getArtistpercentage(playlist_id)
 artistnamepercent = [percents['artist'] for percents in artistpercents]
 artistpercentnumber = [percents['percentage'] for percents in artistpercents]
 percentage_chart = pz.pie(
        values=artistpercentnumber,
        names=artistnamepercent
     )
 return percentage_chart

def getReleaseYearChart(playlist_id):
 release_years = az.getReleaseYears(playlist_id)
 if release_years is None:
  return None
 release_dataframe = pd.DataFrame(release_years)
 release_fig = pz.histogram(release_dataframe,
                      x="released",
                      title="songs by release year")
 return release_fig