import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # nopep8

from authentication import Authentication
from downloader import Downloader
import exceptions
import pathlib
import tpkutils
import shutil
import json
import glob
import os


def main():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    MAPSERVER_URL = config["mapServerUrl"]
    GENERATE_TOKEN_URL = config["generateTokenUrl"]
    MINIMUM_ZOOM_LEVEL = config["minimumZoomLevel"]
    MAXIMUM_ZOOM_LEVEL = config["maximumZoomlevel"]

    USERNAME = os.getenv('TILESET_GENERATOR_USERNAME')
    PASSWORD = os.getenv('TILESET_GENERATOR_PASSWORD')

    tiles_folder = pathlib.Path('tiles')
    if tiles_folder.exists() and tiles_folder.is_dir():
        shutil.rmtree("tiles")
    os.mkdir("tiles")

    authentication = Authentication(GENERATE_TOKEN_URL)
    token = authentication.authenticate(USERNAME, PASSWORD)
    downloader = Downloader(token, MAPSERVER_URL)
    zoom_levels = f"{str(MINIMUM_ZOOM_LEVEL)}-{str(MAXIMUM_ZOOM_LEVEL)}"

    for shapefile in glob.glob("shapefiles/*.shp"):
        attempt = 1
        success = False
        print(f"\nWorking on shapefile: {shapefile}")
        while attempt < 3 and success == False:
            try:
                downloaded_tpk_location = downloader.download(
                    shapefile, zoom_levels)
                shapefile_tiles_folder = pathlib.Path(
                    downloaded_tpk_location).parents[1]

                print("Generating tiles...")
                with tpkutils.TPK(downloaded_tpk_location) as tpk:
                    zoom_list = list(
                        range(MINIMUM_ZOOM_LEVEL, MAXIMUM_ZOOM_LEVEL + 1))
                    tpk.to_disk(f"{shapefile_tiles_folder}/xyz",
                                zoom=zoom_list, drop_empty=True)

                shutil.make_archive(
                    f"{shapefile_tiles_folder}/zip/layer", 'zip', f"{shapefile_tiles_folder}/xyz")
                print("Done!")
                success = True
            except exceptions.InvalidTokenException:
                print("Token expired, generating a new one...")
                token = authentication.authenticate(USERNAME, PASSWORD)
            except Exception as exception:
                print("Unexpected error: ", exception)
                attempt = attempt + 1


if __name__ == "__main__":
    main()
