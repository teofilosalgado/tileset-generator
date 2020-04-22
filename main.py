import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # nopep8

from authentication import Authentication
from downloader import Downloader
import pathlib
import shutil
import glob
import os

MAPSERVER_URL = "https://tiledbasemaps.arcgis.com/arcgis/rest/services/World_Imagery/MapServer"
GENERATE_TOKEN_URL = "https://www.arcgis.com/sharing/rest/generateToken"

if __name__ == "__main__":
    tiles_folder = pathlib.Path('tiles')
    if tiles_folder.exists() and tiles_folder.is_dir():
        shutil.rmtree("tiles")
    os.mkdir("tiles")

    authentication = Authentication(GENERATE_TOKEN_URL)
    token = authentication.authenticate("teofilosalgado", "Casa32123955#")
    downloader = Downloader(token, MAPSERVER_URL)

    for shapefile in glob.glob("shapefiles/*.shp"):
        downloaded_tpk_path = downloader.download(shapefile, "10")

        # with tpkutils.TPK("temp.tpk") as tpk:
        #     tpk.to_disk('tiles/T1600055', zoom=[11], drop_empty=True)
        # os.remove("temp.tpk")
