from __future__ import annotations

import base64
import time
from typing import TYPE_CHECKING, Optional

import requests
from Crypto.Cipher import AES
from Crypto.Hash import CMAC

from .const import OFFICIALAPI_URL
from .helper import CHSesame2MechStatus
from .history import CHSesame2History

if TYPE_CHECKING:
    from .lock import CHSesame2, CHSesame2CMD


class SesameCloud:
    def __init__(self, device: CHSesame2) -> None:
        """Constructs and sends a Request to the cloud.

        Args:
            device (CHSesame2): The device for which you want to query.
        """
        self._device = device

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
                auth=self._device.authenticator,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(e)

        return response

    def getMechStatus(self) -> CHSesame2MechStatus:
        """Retrives a mechanical status of a device.

        Returns:
            CHSesame2MechStatus: Current mechanical status of the device.
        """
        url = "{}/{}".format(OFFICIALAPI_URL, self._device.getDeviceUUID())
        response = self.requestAPI("GET", url)
        r_json = response.json()

        return CHSesame2MechStatus(dictdata=r_json)

    def sendCmd(self, cmd: CHSesame2CMD, history_tag: str = "pysesame3") -> bool:
        """Sends a locking/unlocking command.

        Args:
            cmd (CHSesame2CMD): Lock, Unlock and Toggle.
            history_tag (CHSesame2CMD): The key tag to sent when locking and unlocking.

        Returns:
            bool: `True` if success, `False` if not.
        """
        url = "{}/{}/cmd".format(OFFICIALAPI_URL, self._device.getDeviceUUID())

        j2 = int(time.time())
        bArr = []
        bArr.append(((j2 >> 8) & 65535) & 0xFF)
        bArr.append(((j2 >> 16) & 65535) & 0xFF)
        bArr.append(((j2 >> 24) & 65535) & 0xFF)
        secret = bytes.fromhex(self._device.getSecretKey())
        cobj = CMAC.new(secret, ciphermod=AES)
        cobj.update(bArr)
        sign = cobj.hexdigest()

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

    def getHistoryEntries(self) -> list[CHSesame2History]:
        """Retrieves the history of all events with a device.

        Returns:
            list[CHSesame2History]: A list of events.
        """
        url = "{}/{}/history?page=0&lg=10".format(
            OFFICIALAPI_URL, self._device.getDeviceUUID()
        )

        ret = []

        response = self.requestAPI("GET", url)
        for entry in response.json():
            ret.append(CHSesame2History(**entry))

        return ret
