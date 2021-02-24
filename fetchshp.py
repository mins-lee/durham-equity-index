import geopandas as gpd
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

# TODO: add doc string
def downloadshpfile(zipurl, localpath):


    print('Downloading shapefile...')
    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(localpath)
    print('Done')

    filenames = [y for y in sorted(zfile.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)] 
    # print(filenames)

    dbf, prf, shp, shx = [filename for filename in filenames]
    return gpd.read_file(localpath + shp)
