import equityscore
import geopandas as gpd
import json
import cufflinks as cf
import pandas as pd
import plotly.express as px
import numpy as np
from fetchshp import downloadshpfile
from equityscore import durhamequity
import yaml
cf.go_offline() 

with open('config.yaml', 'r') as f:
  config = yaml.safe_load(f.read())  

zipurl = config['shpfile']['zipurl']
localpath = config['shpfile']['localpath']

# download shpfile
PA = downloadshpfile(zipurl, localpath)
print("Shape of the dataframe: {}".format(PA.shape))
print("Projection of dataframe: {}".format(PA.crs))
print(PA.tail())

durhamcode = config['acs']['FIPScountycode']

durham = PA[PA.COUNTYFP == durhamcode]
print("Shape of the dataframe: {}".format(durham.shape))
print("Projection of dataframe: {}".format(durham.crs))

# create GeoJson
durham.to_file("durham.geojson", driver = "GeoJSON")
with open("durham.geojson") as geofile:
    j_file = json.load(geofile)

# create idkey
for feature in j_file['features']:
    blockgroup = feature['properties']['BLKGRPCE']
    tract = feature['properties']['TRACTCE']
    feature['id'] = blockgroup + tract

# get 6 digit tract code to standardize key for data table
tracturl = config['shpfile']['tracturl']


table = pd.read_csv(tracturl, sep=';')

# prepare both dataframes to merge
# create equity index table
df = durhamequity()
df.censusTract = pd.to_numeric(df.censusTract)

# separate tract code from state and county code
table.CODE = table.CODE.astype(str)
table.CODE = table.CODE.apply(lambda x: x[5:])

fullTable = pd.merge(df, table, left_on='censusTract', right_on='NAME', how='outer')

# create key to combine table with shp file
fullTable['key'] = fullTable.blockGroup.astype(str) + fullTable.CODE.astype(str)

# combine block group with tract for both data and geofile
import plotly.express as px
fig = px.choropleth_mapbox(fullTable, geojson=j_file, featureidkey='id', 
                            locations='key', color='total',
                            color_continuous_scale="Viridis",
                            range_color=(0, 1),
                            mapbox_style="carto-positron",
                            zoom=10, center = {"lat": 35.9940, "lon": -78.8986},
                            opacity=0.5,
                            labels={'total':'equity score'}
                            )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()