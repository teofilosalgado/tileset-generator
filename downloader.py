import os
import glob
import tqdm
import time
import json
import arcgis
import requests
import exceptions


class Downloader:

    def __init__(self, token, mapserver_url):
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.mapserver_url = mapserver_url

    def download(self, shapefile, levels):
        featureset = self._shapefile_to_featureset(shapefile)
        result = self._estimate_export_tiles_size(featureset, levels)
        print(f"Total tiles to export: {result['totalTilesToExport']}")
        print(f"Estimated download size: {result['totalSize']/1000}KB")

        url = self._export_tiles(featureset, levels)
        folder_name = shapefile.split("/")[1].split(".")[0]

        item_folder_path = f"tiles/{folder_name}"
        tpk_folder_path = f"tiles/{folder_name}/tpk"
        os.mkdir(item_folder_path)
        os.mkdir(tpk_folder_path)

        self._download_tpk(url, f"{tpk_folder_path}/layer.tpk")
        return f"{tpk_folder_path}/layer.tpk"

    def _result_handler(self, response):
        try:
            job = response.json()['jobId']
            results = self._get_job_results(job)
            return results['value']
        except KeyError:
            self._exception_handler(response)

    def _exception_handler(self, response):
        error = response.json()['error']
        if error["code"] == 498:
            raise exceptions.InvalidTokenException

    def _estimate_export_tiles_size(self, featureset, levels):
        data = {"f": "json",
                "storageFormatType": "Compact",
                "tilePackage": "true",
                "exportExtent": "DEFAULT",
                "exportBy": "levelId",
                "levels": levels,
                "areaOfInterest": featureset.to_json}
        response = requests.post(
            f"{self.mapserver_url}/estimateExportTilesSize", data=data, headers=self.headers)
        return self._result_handler(response)

    def _export_tiles(self, featureset, levels):
        data = {"f": "json",
                "storageFormatType": "Compact",
                "tilePackage": "true",
                "exportExtent": "DEFAULT",
                "optimizeTilesForSize": "false",
                "compressionQuality": "",
                "exportBy": "levelId",
                "levels": levels,
                "areaOfInterest": featureset.to_json}
        response = requests.post(
            f"{self.mapserver_url}/exportTiles", data=data, headers=self.headers)
        return self._result_handler(response)

    def _get_job_status(self, job):
        parameters = {"f": "json"}
        response = requests.get(
            f"{self.mapserver_url}/jobs/{job}", params=parameters, headers=self.headers)
        status = response.json()
        return status

    def _get_job_results(self, job):
        status = self._get_job_status(job)
        while(status['jobStatus'] in ["esriJobSubmitted", "esriJobExecuting", "esriJobWaiting"]):
            status = self._get_job_status(job)
            time.sleep(1)

        if(status['jobStatus'] == "esriJobSucceeded"):
            parameters = {"f": "json"}
            response = requests.get(
                f"{self.mapserver_url}/jobs/{job}/results/out_service_url", params=parameters, headers=self.headers)
            return response.json()
        else:
            raise exceptions.JobFailedException(status)

    def _download_tpk(self, url, filename, attempt=1):
        parameters = {"f": "json"}
        response = requests.get(url, params=parameters, headers=self.headers)

        for item in response.json()['files']:
            file_size = int(requests.head(
                item['url']).headers["Content-Length"])
            bar = tqdm.tqdm(total=file_size, unit='B',
                            unit_scale=True, desc=filename)

            with open(filename, "wb") as tpk:
                response = requests.get(
                    item['url'], headers=self.headers, stream=True)
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        tpk.write(chunk)
                        bar.update(4096)
            bar.close()
            if file_size == os.path.getsize(filename):
                print("File downloaded successfully!")
            else:
                if attempt > 2:
                    raise exceptions.DownloadFailedException(
                        f"Couldn't download {filename}")
                else:
                    print("Download failed unexpectedly, trying again...")
                    self._download_tpk(url, filename, attempt=attempt + 1)

    def _shapefile_to_featureset(self, shapefile):
        return arcgis.features.GeoAccessor.from_featureclass(shapefile).spatial.to_featureset()
