import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # nopep8

from authentication import Authentication
from downloader import Downloader
import pathlib
import shutil
import json
import glob
import os

if __name__ == "__main__":

    with open("config.json", "r") as config_file:
        config = json.loads(config_file)

    MAPSERVER_URL = config["mapServerUrl"]
    GENERATE_TOKEN_URL = config["generateTokenUrl"]
    USERNAME = os.getenv('TILESET_GENERATOR_USERNAME')
    PASSWORD = os.getenv('TILESET_GENERATOR_PASSWORD')

    tiles_folder = pathlib.Path('tiles')
    if tiles_folder.exists() and tiles_folder.is_dir():
        shutil.rmtree("tiles")
    os.mkdir("tiles")

    authentication = Authentication(GENERATE_TOKEN_URL)
    token = authentication.authenticate(USERNAME, PASSWORD)
    downloader = Downloader(token, MAPSERVER_URL)

    for shapefile in glob.glob("shapefiles/*.shp"):
        downloaded_tpk_path = downloader.download(shapefile, "10")

        # with tpkutils.TPK("temp.tpk") as tpk:
        #     tpk.to_disk('tiles/T1600055', zoom=[11], drop_empty=True)
        # os.remove("temp.tpk")
