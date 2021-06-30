import sys

try:
    import boto3
    from requests_aws4auth import AWS4Auth
except ImportError:
    # Optional deps
    pass
import requests

from .const import IOT_EP, AuthType


class WebAPIAuth(requests.auth.AuthBase):
    def __init__(self, apikey: str):
        """Generic Implementation for Web API Authentication.

        Args:
            apikey (str): API Key
        """
        self._apikey = apikey

        if len(self._apikey) != 40:
            raise ValueError("Invalid API Key - length should be 40.")

    @property
    def login_method(self):
        return AuthType.WebAPI

    def __call__(self, r):
        r.headers["x-api-key"] = self._apikey
        return r


class CognitoAuth:
    def __init__(self, apikey: str, client_id: str):
        """Generic Implementation for Web API Authentication.

        Args:
            apikey (str): API Key
            client_id (str): Client ID
        """
        self._apikey = apikey
        self._client_id = client_id

        if len(self._apikey) != 40:
            raise ValueError("Invalid API Key - length should be 40.")

        if "AWSIoTPythonSDK" not in sys.modules or "certifi" not in sys.modules:
            raise RuntimeError(
                "Failed to load AWSIoTPythonSDK or certifi. Did you run `pip install pysesame3[cognito]`?"
            )

    @property
    def login_method(self) -> AuthType:
        return AuthType.SDK

    @property
    def client_id(self) -> str:
        return self._client_id

    def authenticate(self):
        region_name = self.client_id.split(":")[0]

        cognitoIdentityClient = boto3.client(
            "cognito-identity", region_name=region_name
        )
        temporaryIdentityId = cognitoIdentityClient.get_id(
            IdentityPoolId=self.client_id
        )
        identityID = temporaryIdentityId["IdentityId"]

        temporaryCredentials = cognitoIdentityClient.get_credentials_for_identity(
            IdentityId=identityID
        )
        access_key_id = temporaryCredentials["Credentials"]["AccessKeyId"]
        secret_key = temporaryCredentials["Credentials"]["SecretKey"]
        session_token = temporaryCredentials["Credentials"]["SessionToken"]

        return (access_key_id, secret_key, session_token)

    def __call__(self, r):
        (access_key_id, secret_key, session_token) = self.authenticate()

        if IOT_EP in r.url:
            service = "iotdata"
        else:
            r.headers["x-api-key"] = self._apikey
            service = "execute-api"

        auth = AWS4Auth(
            access_key_id,
            secret_key,
            "ap-northeast-1",
            service,
            session_token=session_token,
        )
        r = auth(r)

        return r
