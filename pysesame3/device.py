from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from pysesame3.auth import WebAPIAuth
    from pysesame3.helper import CHProductModel


class CHDevices:
    def __init__(self, authenticator: WebAPIAuth):
        """Generic Implementation for Candyhouse products.

        Args:
            authenticator (WebAPIAuth): The authenticator for the device
        """
        self._authenticator = authenticator
        self._deviceId = None
        self._productModel = None

    @property
    def authenticator(self) -> WebAPIAuth:
        return self._authenticator

    @property
    def deviceId(self) -> str:
        """Returns a device id of a specific device.

        Returns:
            str: The UUID of the device.
        """
        if self._deviceId is not None:
            return str(self._deviceId).upper()
        else:
            return None

    @property
    def productModel(self) -> CHProductModel:
        """Returns a model information of a specific device.

        Returns:
            CHProductModel: The product model of the device.
        """
        return self._productModel

    def setDeviceId(self, id: Union[uuid.UUID, str]) -> None:
        """Sets a device id of a specific device.

        Args:
            id (Union[uuid.UUID, str]): The UUID of the device.

        Raises:
            ValueError: If `id` is invalid.
        """
        if isinstance(id, str):
            id = uuid.UUID(id)
        elif not isinstance(id, uuid.UUID):
            raise ValueError("Invalid UUID")
        self._deviceId = id

    def setProductModel(self, model: CHProductModel) -> None:
        """Sets a model information of a specific device.

        Args:
            model (CHProductModel): The product model of the device.

        Raises:
            ValueError: If `model` is invalid.
        """
        if type(model).__name__ != "CHProductModel":
            raise ValueError("Invalid CHProductModel")
        self._productModel = model


class SesameLocker(CHDevices):
    def __init__(self, authenticator: WebAPIAuth):
        """Generic Implementation for Candyhouse smart locks.

        Args:
            authenticator (WebAPIAuth): The authenticator for the device
        """
        super().__init__(authenticator)
        self._mechStatus = None
        self._secretKey = None
        self._sesame2PublicKey = None

    def getDeviceUUID(self) -> str:
        """Gets a device UUID of a specific device.

        Returns:
            str: The UUID of the device.
        """
        return self.deviceId

    def getSecretKey(self) -> str:
        """Gets a secret key of a specific device.

        Returns:
            str: The secret key for controlling the device.
        """
        return self._secretKey

    def getSesame2PublicKey(self) -> str:
        """Gets a public key of a specific device.

        Returns:
            str: The public key of the device.
        """
        return self._sesame2PublicKey

    def setDeviceUUID(self, id: Union[uuid.UUID, str]) -> None:
        """Sets a device UUID of a specific device.

        Args:
            id (Union[uuid.UUID, str]): The UUID of the device.
        """
        self.setDeviceId(id)

    def setSecretKey(self, key: str) -> None:
        """Sets a secret key for a specific device.

        Args:
            key (str): The secret key for controlling the device.

        Raises:
            ValueError: If `key` is invalid.
        """
        if not isinstance(key, str):
            raise ValueError("Invalid SecretKey - should be string.")
        if len(key) != 32:
            raise ValueError("Invalid SecretKey - length should be 32.")
        self._secretKey = key

    def setSesame2PublicKey(self, key: str) -> None:
        """Sets a public key of a specific device.

        Args:
            key (str): The public key of the device.

        Raises:
            ValueError: If `key` is invalid.
        """
        if not isinstance(key, str):
            raise ValueError("Invalid Sesame2PublicKey")
        self._sesame2PublicKey = key

    def __str__(self) -> str:
        """Returns a string representation of an object.

        Returns:
            str: The string representation of the object.
        """
        return f"SesameLocker(deviceUUID={self.getDeviceUUID()}, deviceModel={self.productModel}, sesame2PublicKey={self.getSesame2PublicKey()})"
