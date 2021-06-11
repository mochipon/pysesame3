import requests


class WebAPIAuth(requests.auth.AuthBase):
    def __init__(self, apikey: str):
        """Generic Implementation for Web API Authentication.

        Args:
            apikey (str): API Key
        """
        self._apikey = apikey

    def __call__(self, r):
        r.headers["x-api-key"] = self._apikey
        return r
