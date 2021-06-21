# tileset-generator
This application was intended to make offline maps easier, generating all the tilesets you may need to serve to your apps. We all know, not all map frameworks/libraries use or prefer the same tileset scheme for offline loading. In some applications we need our tiles in `ZXY` folders, sometimes we need it in specific package formats like `.mbtiles` or `.mmpk`. So to mitigate this problem, this script can automatically generate basemaps for most of the tiling schemes out there, based on any given area of interest.

## How it works?
It works by scanning all shapefiles in the `shapefiles` folder and requesting your desired ArcGIS Map Server with all the geometries it found in the aforementioned directory as areas of interest for the cache generation process. After downloading all the resulting `.tpk` files, it organizes everything in folders inside the `tiles` directory, according to the desired tile format.

## How to run it?
First of all, you need to create two environment variables: `TILESET_GENERATOR_USERNAME` and `TILESET_GENERATOR_PASSWORD` to store your desired ArcGIS account credentials. Later on, create a `shapefile` folder (in the same path where `main.py` is located) containing all the shapefiles you need to use as areas of interest. After that, just run:

```
python3 main.py
```

and wait for the execution of the process.

## Minimum requirements:
- Python: 3.5


ArcGIS is a trademark of of ESRI and is used here to refer to specific technologies. No endorsement by ESRI is implied.
