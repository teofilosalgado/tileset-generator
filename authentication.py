import requests


class Authentication:

    def __init__(self, generate_token_url):
        self.generate_token_url = generate_token_url

    def authenticate(self, username, password):
        data = {"username": username,
                "password": password,
                "referer": "http://www.arcgis.com",
                "f": "json"}

        response = requests.post(self.generate_token_url, data=data)
        token = response.json()["token"]
        return token
