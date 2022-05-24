import sys
from typing import TYPE_CHECKING, Tuple

try:
    import boto3
    from awscrt import auth
    from requests_aws4auth import AWS4Auth
except ImportError:  # pragma: no cover
    pass
import requests

from .cloud import AWSIoT, SesameCloud
from .const import CLIENT_ID, IOT_EP, AuthType
from .helper import RegexHelper

if TYPE_CHECKING:
    try:
        from awscrt import mqtt
    except ImportError:  # pragma: no cover
        pass


class WebAPIAuth(requests.auth.AuthBase):
    def __init__(self, apikey: str):
        """Generic Implementation for Web API Authentication.

        Args:
            apikey (str): API Key
        """
        if len(apikey) != 40:
            raise ValueError("Invalid API Key - length should be 40.")

        self._apikey = apikey
        self._sesame_cloud = SesameCloud(self)

    @property
    def login_method(self) -> AuthType:
        """Return a login method of this authentication.

        Returns:
            AuthType: `WebAPI` or `SDK`
        """
        return AuthType.WebAPI

    @property
    def sesame_cloud(self) -> SesameCloud:
        return self._sesame_cloud

    @property
    def aws_iot(self):
        raise NotImplementedError("Not supported with WebAPI.")

    def __call__(
        self, request: requests.models.PreparedRequest
    ) -> requests.models.PreparedRequest:
        """Function to transform HTTP request with `requests.Request`.

        This function aims to be called during request setup.

        Args:
            request (requests.models.PreparedRequest): The HTTP request to be transformed.
        """
        request.headers["x-api-key"] = self._apikey
        return request


class CognitoAuth:
    def __init__(self, apikey: str, client_id: str = CLIENT_ID):
        """Generic Implementation for Cognito Authentication.

        Args:
            apikey (str): API Key
            client_id (str): Client ID (Optional)
        """
        if len(apikey) != 40:
            raise ValueError("Invalid API Key - length should be 40.")

        if (
            "awsiot" not in sys.modules or "certifi" not in sys.modules
        ):  # pragma: no cover
            raise RuntimeError(
                "Failed to load awsiotsdk or certifi. Did you run `pip install pysesame3[cognito]`?"
            )

        self._apikey = apikey
        self._client_id = client_id

        self._sesame_cloud = SesameCloud(self)
        self._aws_iot = AWSIoT(self)

    @property
    def login_method(self) -> AuthType:
        """Return a login method of this authentication.

        Returns:
            AuthType: `WebAPI` or `SDK`
        """
        return AuthType.SDK

    @property
    def sesame_cloud(self) -> SesameCloud:
        return self._sesame_cloud

    @property
    def aws_iot(self) -> AWSIoT:
        return self._aws_iot

    @property
    def client_id(self) -> str:
        """Return a client id.

        Returns:
            str: Client ID
        """
        return self._client_id

    def authenticate(self) -> Tuple[str, str, str]:
        """Authenticate and get a credential from AWS Cognito.

        Returns:
            Tuple[str, str, str]: `access_key_id`, `secret_key` and `session_token`
        """
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

    def iot_websocket_handshake_transform(
        self, transform_args: "mqtt.WebsocketHandshakeTransformArgs"
    ) -> None:
        """Function to transform websocket handshake request within `awscrt.mqtt.Connection`.

        This function aims to be called each time a websocket connection is attempted.

        Args:
            transform_args (mqtt.WebsocketHandshakeTransformArgs): Contains HTTP request to be transformed. The function calls `transform_args.done()` when complete.
        """
        try:
            (
                access_key_id,
                secret_key,
                session_token,
            ) = self.authenticate()

            cred_provider = auth.AwsCredentialsProvider.new_static(
                access_key_id=access_key_id,
                secret_access_key=secret_key,
                session_token=session_token,
            )

            signing_config = auth.AwsSigningConfig(
                algorithm=auth.AwsSigningAlgorithm.V4,
                signature_type=auth.AwsSignatureType.HTTP_REQUEST_QUERY_PARAMS,
                credentials_provider=cred_provider,
                region=RegexHelper.get_aws_region(IOT_EP),
                service="iotdevicegateway",
                omit_session_token=True,  # IoT is weird and does not sign X-Amz-Security-Token
            )

            signing_future = auth.aws_sign_request(
                transform_args.http_request, signing_config
            )
            signing_future.add_done_callback(
                lambda x: transform_args.set_done(x.exception())
            )
        except Exception as e:
            transform_args.set_done(e)

    def __call__(
        self, request: requests.models.PreparedRequest
    ) -> requests.models.PreparedRequest:
        """Function to transform HTTP request with `requests.Request`.

        This function aims to be called during request setup.

        Args:
            request (requests.models.PreparedRequest): The HTTP request to be transformed.
        """
        if request.url is None:
            raise TypeError("Failed to retrive HTTP URL to send the request to.")

        request.headers["x-api-key"] = self._apikey
        return request
