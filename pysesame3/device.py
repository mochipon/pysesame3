import logging
import uuid
from typing import TYPE_CHECKING, Optional, Union

from pysesame3.helper import CHSesame2MechStatus

if TYPE_CHECKING:
    from pysesame3.auth import CognitoAuth, WebAPIAuth
    from pysesame3.helper import CHProductModel

logger = logging.getLogger(__name__)


class CHDevices:
    def __init__(self, authenticator: Union["WebAPIAuth", "CognitoAuth"]):
        """Generic Implementation for Candyhouse products.

        Args:
            authenticator (Union[WebAPIAuth, CognitoAuth]): The authenticator for the device
        """
        self._authenticator = authenticator
        self._deviceId: Optional[uuid.UUID] = None
        self._productModel: Optional[CHProductModel] = None

    @property
    def authenticator(self) -> Union["WebAPIAuth", "CognitoAuth"]:
        return self._authenticator

    @property
    def deviceId(self) -> Optional[str]:
        """Return a device id of a specific device.

        Returns:
            str: The UUID of the device.
        """
        if self._deviceId is not None:
            return str(self._deviceId).upper()
        else:
            return None

    @property
    def productModel(self) -> Optional["CHProductModel"]:
        """Return a model information of a specific device.

        Returns:
            CHProductModel: The product model of the device.
        """
        return self._productModel

    def setDeviceId(self, id: Union[uuid.UUID, str]) -> None:
        """Set a device id of a specific device.

        Args:
            id (Union[uuid.UUID, str]): The UUID of the device.

        Raises:
            ValueError: If `id` is invalid.
        """
        if isinstance(id, str):
            id = uuid.UUID(id)
        elif not isinstance(id, uuid.UUID):
            raise ValueError("Invalid UUID")
        logger.debug("setDeviceId={}".format(id))
        self._deviceId = id

    def setProductModel(self, model: "CHProductModel") -> None:
        """Set a model information of a specific device.

        Args:
            model (CHProductModel): The product model of the device.

        Raises:
            ValueError: If `model` is invalid.
        """
        if type(model).__name__ != "CHProductModel":
            raise ValueError("Invalid CHProductModel")
        logger.debug("setProductModel={}".format(model))
        self._productModel = model


class SesameLocker(CHDevices):
    def __init__(self, authenticator: Union["WebAPIAuth", "CognitoAuth"]):
        """Generic Implementation for Candyhouse smart locks.

        Args:
            authenticator (Union[WebAPIAuth, CognitoAuth]): The authenticator for the device
        """
        super().__init__(authenticator)
        self._mechStatus: Optional[CHSesame2MechStatus] = None
        self._secretKey: Optional[bytes] = None
        self._sesame2PublicKey: Optional[bytes] = None

    def getDeviceUUID(self) -> Optional[str]:
        """Get a device UUID of a specific device.

        Returns:
            str: The UUID of the device.
        """
        return self.deviceId

    def getSecretKey(self) -> Optional[bytes]:
        """Get a secret key of a specific device.

        Returns:
            str: The secret key for controlling the device.
        """
        return self._secretKey

    def setDeviceUUID(self, id: Union[uuid.UUID, str]) -> None:
        """Set a device UUID of a specific device.

        Args:
            id (Union[uuid.UUID, str]): The UUID of the device.
        """
        self.setDeviceId(id)

    def setSecretKey(self, key: Union[bytes, str]) -> None:
        """Set a secret key for a specific device.

        Args:
            key (str): The secret key for controlling the device.

        Raises:
            ValueError: If `key` is invalid.
        """
        if not isinstance(key, bytes) and not isinstance(key, str):
            raise TypeError("Invalid SecretKey - should be str or bytes.")
        if not isinstance(key, bytes):
            key = bytes.fromhex(key)
        if len(key) != 16:
            raise ValueError("Invalid SecretKey - length should be 16.")
        logger.debug("setSecretKey=*******")
        self._secretKey = key

    def __str__(self) -> str:
        """Return a string representation of an object.

        Returns:
            str: The string representation of the object.
        """
        return f"SesameLocker(deviceUUID={self.getDeviceUUID()}, deviceModel={self.productModel})"
