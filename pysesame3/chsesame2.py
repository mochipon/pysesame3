import json
from enum import Enum, IntEnum, auto
from typing import TYPE_CHECKING, Callable, List, Optional, Union

try:
    import certifi
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
except ImportError:
    # Optional deps
    pass

from pysesame3.auth import CognitoAuth
from pysesame3.cloud import SesameCloud
from pysesame3.const import IOT_EP
from pysesame3.device import SesameLocker
from pysesame3.helper import CHSesame2MechStatus

if TYPE_CHECKING:
    from pysesame3.auth import WebAPIAuth
    from pysesame3.history import CHSesame2History


class CHSesame2CMD(IntEnum):
    LOCK = 82
    UNLOCK = 83
    TOGGLE = 88


class CHSesame2ShadowStatus(Enum):
    LockedWm = auto()
    UnlockedWm = auto()
    MovedWm = auto()


class CHSesame2(SesameLocker):
    def __init__(
        self,
        authenticator: Union["WebAPIAuth", "CognitoAuth"],
        device_uuid: str,
        secret_key: str,
    ) -> None:
        """SESAME3 Device Specific Implementation.

        Args:
            authenticator (Union[WebAPIAuth, CognitoAuth]):
            device_uuid (str): The UUID of the device
            secret_key (str): The secret key of the device
        """
        super().__init__(authenticator)

        self.setDeviceUUID(device_uuid)
        self.setSecretKey(secret_key)
        self._iot_client: Optional[AWSIoTMQTTClient] = None
        self._callback: Optional[
            Callable[[CHSesame2, CHSesame2MechStatus], None]
        ] = None

        # Initial sync of `self._deviceShadowStatus`
        self.mechStatus

    @property
    def mechStatus(self) -> CHSesame2MechStatus:
        """Return a mechanical status of a device.

        Returns:
            CHSesame2MechStatus: Current mechanical status of the device.
        """
        status = SesameCloud(self).getMechStatus()

        if status.isInLockRange():
            self.setDeviceShadowStatus(CHSesame2ShadowStatus.LockedWm)
        else:
            self.setDeviceShadowStatus(CHSesame2ShadowStatus.UnlockedWm)

        return status

    def _iot_shadow_callback(self, client, userdata, message) -> None:  # type: ignore
        """Callback for updated shadows.

        Args:
            message (dict): The device shadow
        """
        try:
            shadow = json.loads(message.payload)
            status = CHSesame2MechStatus(rawdata=shadow["state"]["reported"]["mechst"])

            original_status = self.getDeviceShadowStatus()

            # It is possible that both isInLockRange and isInUnlockRange are true.
            # This probably indicates that the key is rotating.
            # We have to carefully check the status just to make sure that
            # it has been definitely toggled.
            if not status.isInLockRange() and status.isInUnlockRange():
                self.setDeviceShadowStatus(CHSesame2ShadowStatus.UnlockedWm)
            if status.isInLockRange() and not status.isInUnlockRange():
                self.setDeviceShadowStatus(CHSesame2ShadowStatus.LockedWm)

            if original_status != self.getDeviceShadowStatus():
                if self._callback is not None and callable(self._callback):
                    self._callback(self, status)
        except Exception as err:  # noqa: F841
            # TODO: handle exceptions correctly
            pass

    def subscribeMechStatus(
        self,
        callback: Optional[Callable[["CHSesame2", CHSesame2MechStatus], None]] = None,
    ) -> None:
        """Subscribe to a topic at AWS IoT

        Args:
            callback (Callable[[CHSesame2, CHSesame2MechStatus], None], optional): The registered callback will be executed once an update is delivered. Defaults to `None`.

        Raises:
            NotImplementedError: If the authenticator is not `AuthType.SDK`.
        """
        if not isinstance(self.authenticator, CognitoAuth):
            raise NotImplementedError("This feature is not suppoted by the Web API.")

        if callable(callback) or callback is None:
            self._callback = callback
        else:
            raise TypeError("callback should be callable.")

        if self._iot_client is not None:
            raise RuntimeError(
                "subscribeMechStatus is already called for the device, update the callback anyway."
            )

        (access_key_id, secret_key, session_token) = self.authenticator.authenticate()

        self._iot_client = AWSIoTMQTTClient(
            self.authenticator.client_id, useWebsocket=True
        )
        self._iot_client.configureEndpoint(IOT_EP, 443)
        self._iot_client.configureCredentials(certifi.where())
        self._iot_client.configureIAMCredentials(
            access_key_id, secret_key, session_token
        )
        self._iot_client.connect()
        self._iot_client.subscribe(
            "$aws/things/sesame2/shadow/name/{}/update/accepted".format(
                self.getDeviceUUID()
            ),
            1,
            self._iot_shadow_callback,
        )

    @property
    def historyEntries(self) -> List["CHSesame2History"]:
        """Return the history of all events with a device.

        Returns:
            list[CHSesame2History]: A list of events.
        """
        return SesameCloud(self).getHistoryEntries()

    def getDeviceShadowStatus(self) -> CHSesame2ShadowStatus:
        """Return a cached shadow status of a device.
        In order to refresh the shadow, run `mechStatus`.

        Returns:
            CHSesame2ShadowStatus: Shadow (assumed) status of the device.
        """
        return self._deviceShadowStatus

    def setDeviceShadowStatus(self, status: CHSesame2ShadowStatus) -> None:
        """Set a shadow status of a device.

        Args:
            status (CHSesame2ShadowStatus): Desired shadow (assumed) status

        Raises:
            ValueError: If `status` is invalid.
        """
        if not isinstance(status, CHSesame2ShadowStatus):
            raise ValueError("Invalid CHSesame2ShadowStatus")
        self._deviceShadowStatus = status

    def lock(self, history_tag: str = "pysesame3") -> bool:
        """Locking.

        Args:
            history_tag (str): The key tag to sent when locking and unlocking. Defaults to `pysesame3`.

        Returns:
            bool: `True` if it is successfully locked, `False` if not.
        """
        result = SesameCloud(self).sendCmd(CHSesame2CMD.LOCK, history_tag)
        if result:
            self.setDeviceShadowStatus(CHSesame2ShadowStatus.LockedWm)
        return result

    def unlock(self, history_tag: str = "pysesame3") -> bool:
        """Unlocking.

        Args:
            history_tag (str): The key tag to sent when locking and unlocking. Defaults to `pysesame3`.

        Returns:
            bool: `True` if it is successfully unlocked, `False` if not.
        """
        result = SesameCloud(self).sendCmd(CHSesame2CMD.UNLOCK, history_tag)
        if result:
            self.setDeviceShadowStatus(CHSesame2ShadowStatus.UnlockedWm)
        return result

    def toggle(self, history_tag: str = "pysesame3") -> bool:
        """Toggle.

        Args:
            history_tag (str): The key tag to sent when locking and unlocking. Defaults to `pysesame3`.

        Returns:
            bool: `True` if it is successfully toggled, `False` if not.
        """
        if self.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm:
            return self.unlock(history_tag)
        else:
            return self.lock(history_tag)

    def __str__(self) -> str:
        """Return a string representation of an object.

        Returns:
            str: The string representation of the object.
        """
        return f"CHSesame2(deviceUUID={self.getDeviceUUID()}, deviceModel={self.productModel}, mechStatus={self.mechStatus})"
