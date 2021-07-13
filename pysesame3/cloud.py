import base64
import time
from typing import TYPE_CHECKING, List, Optional, Union

try:
    import certifi
    from awscrt import io, mqtt
    from awscrt.exceptions import AwsCrtError
    from awsiot import mqtt_connection_builder
except ImportError:
    # Optional deps
    pass

import requests
from Crypto.Cipher import AES
from Crypto.Hash import CMAC

from .const import APIGW_URL, IOT_EP, OFFICIALAPI_URL, AuthType
from .helper import CHSesame2MechStatus
from .history import CHSesame2History

if TYPE_CHECKING:
    from concurrent.futures import Future

    from .auth import CognitoAuth, WebAPIAuth
    from .chsesame2 import CHSesame2, CHSesame2CMD


class SesameCloud:
    def __init__(self, authenticator: Union["WebAPIAuth", "CognitoAuth"]) -> None:
        """Construct and send a Request to the cloud.

        Args:
            authenticator (Union[WebAPIAuth, CognitoAuth]): The authenticator
        """
        self._authenticator = authenticator

    def requestAPI(
        self, method: str, url: str, json: Optional[dict] = None
    ) -> requests.Response:
        """A Wrapper of `requests.request`.

        Args:
            method (str): HTTP method to use: `GET`, `OPTIONS`, `HEAD`, `POST`, `PUT`, `PATCH`, or `DELETE`.
            url (str): URL to send.
            json (Optional[dict], optional): JSON data for the body to attach to the request. Defaults to `None`.

        Raises:
            RuntimeError: An HTTP error occurred.

        Returns:
            requests.Response: The server's response to an HTTP request.
        """
        try:
            response = requests.request(
                method,
                url,
                json=json,
                auth=self._authenticator,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(e)

        return response

    def getSign(self, device: "CHSesame2") -> str:
        """Generate a AES-CMAC tag.

        Returns:
            str: AES-CMAC tag.
        """
        unixtime = int(time.time())
        secret = device.getSecretKey()
        cobj = CMAC.new(secret, ciphermod=AES)
        cobj.update(unixtime.to_bytes(4, "little")[1:4])
        sign = cobj.hexdigest()

        return sign

    def getMechStatus(self, device: "CHSesame2") -> CHSesame2MechStatus:
        """Retrive a mechanical status of a device.

        Args:
            device (CHSesame2): The device for which you want to query.

        Returns:
            CHSesame2MechStatus: Current mechanical status of the device.
        """
        if self._authenticator.login_method == AuthType.WebAPI:
            url = "{}/{}".format(OFFICIALAPI_URL, device.getDeviceUUID())
            response = self.requestAPI("GET", url)
            r_json = response.json()
            return CHSesame2MechStatus(dictdata=r_json)
        else:
            url = "https://{}/things/sesame2/shadow?name={}".format(
                IOT_EP, device.getDeviceUUID()
            )
            response = self.requestAPI("GET", url)
            r_json = response.json()
            return CHSesame2MechStatus(rawdata=r_json["state"]["reported"]["mechst"])

    def sendCmd(
        self, device: "CHSesame2", cmd: "CHSesame2CMD", history_tag: str = "pysesame3"
    ) -> bool:
        """Send a locking/unlocking command.

        Args:
            device (CHSesame2): The device for which you want to query.
            cmd (CHSesame2CMD): Lock, Unlock and Toggle.
            history_tag (CHSesame2CMD): The key tag to sent when locking and unlocking.

        Returns:
            bool: `True` if success, `False` if not.
        """
        if self._authenticator.login_method == AuthType.WebAPI:
            url = "{}/{}/cmd".format(OFFICIALAPI_URL, device.getDeviceUUID())
            sign = self.getSign(device)
        elif self._authenticator.login_method == AuthType.SDK:
            url = "{}/device/v1/iot/sesame2/{}".format(
                APIGW_URL, device.getDeviceUUID()
            )
            sign = self.getSign(device)[0:8]

        payload = {
            "cmd": int(cmd),
            "history": base64.b64encode(history_tag.encode()).decode(),
            "sign": sign,
        }

        try:
            response = self.requestAPI("POST", url, payload)

            return response.ok
        except RuntimeError:
            return False

    def getHistoryEntries(self, device: "CHSesame2") -> List[CHSesame2History]:
        """Retrieve the history of all events with a device.

        Args:
            device (CHSesame2): The device for which you want to query.

        Returns:
            list[CHSesame2History]: A list of events.
        """
        if self._authenticator.login_method == AuthType.WebAPI:
            url = "{}/{}/history?page=0&lg=10".format(
                OFFICIALAPI_URL, device.getDeviceUUID()
            )
        elif self._authenticator.login_method == AuthType.SDK:
            url = "{}/device/v1/sesame2/{}/history?page=0&lg=10&a={}".format(
                APIGW_URL, device.getDeviceUUID(), self.getSign(device)[0:8]
            )

        ret = []

        response = self.requestAPI("GET", url)
        for entry in response.json():
            ret.append(CHSesame2History(**entry))

        return ret


class AWSIoT:
    def __init__(self, authenticator: "CognitoAuth") -> None:
        """Construct and send a request to the AWS IoT.

        Args:
            authenticator (CognitoAuth): The authenticator
        """
        self._authenticator = authenticator
        self.mqtt_connection: mqtt.Connection

    def _on_connection_interrupted(
        self, connection: mqtt.Connection, error: AwsCrtError
    ) -> None:
        """Callback when connection is accidentally lost.

        Args:
            connection (mqtt.Connection): Connection this callback is for.
            error (AwsCrtError): Exception which caused connection loss.
        """
        print("Connection interrupted. error: {}".format(error))

    def _on_connection_resumed(
        self,
        connection: mqtt.Connection,
        return_code: mqtt.ConnectReturnCode,
        session_present: bool,
    ) -> None:
        """Callback when an interrupted connection is re-established.

        Args:
            connection (mqtt.Connection): Connection this callback is for.
            return_code (mqtt.ConnectReturnCode): Connect return code received from the server.
            session_present (bool): `True` if resuming existing session. `False` if new session.
        """
        print(
            "Connection resumed. return_code: {} session_present: {}".format(
                return_code, session_present
            )
        )

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self._on_resubscribe_complete)

    def _on_resubscribe_complete(self, resubscribe_future: "Future") -> None:
        """Callback when resubscribing to existing topics is done.

        Args:
            resubscribe_future (concurrent.futures.Future): Future which completes when resubscribing succeeds or fails.

        Raises:
            ConnectionRefusedError: If the server rejected resubscribe to a topic.
        """
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results["topics"]:
            if qos is None:
                raise ConnectionRefusedError(
                    "Server rejected resubscribe to topic: {}".format(topic)
                )

    def connect(self) -> None:
        """Open the actual connection to the server."""
        if hasattr(self, "mqtt_connection"):
            connect_future = self.mqtt_connection.connect()
            return connect_future.result()

        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        self.mqtt_connection = mqtt_connection_builder.websockets_with_custom_handshake(
            endpoint=IOT_EP,
            client_bootstrap=client_bootstrap,
            websocket_handshake_transform=self._authenticator.iot_websocket_handshake_transform,
            ca_filepath=certifi.where(),
            on_connection_interrupted=self._on_connection_interrupted,
            on_connection_resumed=self._on_connection_resumed,
            client_id=self._authenticator.client_id,
            clean_session=False,
            keep_alive_secs=6,
        )

        connect_future = self.mqtt_connection.connect()
        connect_future.result()
