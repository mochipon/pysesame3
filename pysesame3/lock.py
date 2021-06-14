from __future__ import annotations

from enum import Enum, IntEnum, auto
from typing import TYPE_CHECKING

from pysesame3.cloud import SesameCloud
from pysesame3.device import SesameLocker

if TYPE_CHECKING:
    from pysesame3.auth import WebAPIAuth
    from pysesame3.helper import CHSesame2MechStatus


class CHSesame2CMD(IntEnum):
    LOCK = 82
    UNLOCK = 83
    TOGGLE = 88


class CHSesame2ShadowStatus(Enum):
    LockedWm = auto()
    UnlockedWm = auto()
    MovedWm = auto()


class CHSesame2(SesameLocker):
    """ """

    def __init__(
        self, authenticator: WebAPIAuth, device_uuid: str, secret_key: str
    ) -> None:
        """SESAME3 Device Specific Implementation.

        Args:
            authenticator (WebAPIAuth):
            device_uuid (str): The UUID of the device
            secret_key (str): The secret key of the device
        """
        super().__init__(authenticator)

        self.setDeviceUUID(device_uuid)
        self.setSecretKey(secret_key)

        if self.mechStatus.isInLockRange():
            self._deviceShadowStatus = CHSesame2ShadowStatus.LockedWm
        else:
            self._deviceShadowStatus = CHSesame2ShadowStatus.UnlockedWm

    @property
    def mechStatus(self) -> CHSesame2MechStatus:
        """Returns a mechanical status of a device.

        Returns:
            CHSesame2MechStatus: Current mechanical status of the device.
        """
        return SesameCloud(self).getMechStatus()

    def getDeviceShadowStatus(self) -> CHSesame2ShadowStatus:
        """Returns a shadow status of a device.

        Returns:
            CHSesame2ShadowStatus: Shadow (assumed) status of the device.
        """
        return self._deviceShadowStatus

    def setDeviceShadowStatus(self, status: CHSesame2ShadowStatus) -> None:
        """Sets a shadow status of a device.

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
        elif self.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm:
            return self.lock(history_tag)

    def __str__(self) -> str:
        """Return a string representation of an object.

        Returns:
            str: The string representation of the object.
        """
        return f"CHSesame2(deviceUUID={self.getDeviceUUID()}, deviceModel={self.productModel}, sesame2PublicKey={self.getSesame2PublicKey()}, mechStatus={self.mechStatus})"
