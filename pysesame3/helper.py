import importlib
import sys
from enum import Enum
from typing import Optional, Union

if sys.version_info[:2] >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class ProductData(TypedDict):
    deviceModel: str
    isLocker: bool
    productType: int
    deviceFactory: Union[str, None]


class CHProductModel(Enum):
    WM2: ProductData = {
        "deviceModel": "wm_2",
        "isLocker": False,
        "productType": 1,
        "deviceFactory": None,
    }
    SS2: ProductData = {
        "deviceModel": "sesame_2",
        "isLocker": True,
        "productType": 0,
        "deviceFactory": "CHSesame2",
    }

    @staticmethod
    def getByModel(model: str) -> "CHProductModel":
        if not isinstance(model, str):
            raise TypeError("Invalid Model")
        try:
            return next(
                e for e in list(CHProductModel) if e.value["deviceModel"] == model
            )
        except StopIteration:
            raise NotImplementedError("This device is not supported.")

    @staticmethod
    def getByValue(val: int) -> "CHProductModel":
        if not isinstance(val, int):
            raise TypeError("Invalid Value")
        try:
            return next(
                e for e in list(CHProductModel) if e.value["productType"] == val
            )
        except StopIteration:
            raise NotImplementedError("This device is not supported.")

    def deviceModel(self) -> str:
        return self.value["deviceModel"]

    def isLocker(self) -> bool:
        return self.value["isLocker"]

    def productType(self) -> int:
        return self.value["productType"]

    def deviceFactory(self) -> Union[type, None]:
        if self.value["deviceFactory"] is None:
            raise NotImplementedError("This device type is not supported.")
        return getattr(
            importlib.import_module(f"pysesame3.{self.value['deviceFactory'].lower()}"),
            self.value["deviceFactory"],
        )


class CHSesame2MechStatus:
    def __init__(
        self, rawdata: Union[bytes, str, None] = None, dictdata: Optional[dict] = None
    ) -> None:
        """Represent a mechanical status of a device.

        Args:
            rawdata (Union[bytes, str]): The raw `mechst` string for the device.
            dictdata (str): The structured `mechst` data for the device.
        """
        if rawdata is not None:
            if isinstance(rawdata, str):
                data_bytes = bytes.fromhex(rawdata)
            else:
                data_bytes = rawdata
            self._batteryVoltage = (
                int.from_bytes(data_bytes[0:2], "little") * 7.2 / 1023
            )
            self._target = int.from_bytes(data_bytes[2:4], "little", signed=True)
            self._position = int.from_bytes(data_bytes[4:6], "little", signed=True)
            self._retcode = data_bytes[6]
            self._isInLockRange = data_bytes[7] & 2 > 0
            self._isInUnlockRange = data_bytes[7] & 4 > 0
            self._isBatteryCritical = data_bytes[7] & 32 > 0
        elif dictdata is not None:
            data_dict = dictdata
            self._batteryVoltage = data_dict["batteryVoltage"]
            self._position = data_dict["position"]
            self._isInLockRange = (
                True if data_dict["CHSesame2Status"] == "locked" else False
            )
            self._isInUnlockRange = not self._isInLockRange
        else:
            raise ValueError("No Input")

    def __str__(self) -> str:
        return f"CHSesame2MechStatus(Battery={self.getBatteryPrecentage()}% ({self.getBatteryVoltage():.2f}V), isInLockRange={self.isInLockRange()}, isInUnlockRange={self.isInUnlockRange()}, Position={self.getPosition()})"

    def getBatteryPrecentage(self) -> int:
        """Return battery status information as a percentage.

        Returns:
            int: Battery power left as a percentage.
        """
        list_vol = [6.0, 5.8, 5.7, 5.6, 5.4, 5.2, 5.1, 5.0, 4.8, 4.6]
        list_pct = [100.0, 50.0, 40.0, 32.0, 21.0, 13.0, 10.0, 7.0, 3.0, 0.0]
        cur_vol = self._batteryVoltage

        if cur_vol >= list_vol[0]:
            return 100
        elif cur_vol <= list_vol[-1]:
            return 0
        else:
            ret = 0
            i = 0
            while i < len(list_vol) - 1:
                if cur_vol > list_vol[i] or cur_vol <= list_vol[i + 1]:
                    i = i + 1
                    continue
                else:
                    f = (cur_vol - list_vol[i + 1]) / (list_vol[i] - list_vol[i + 1])
                    f3 = list_pct[i]
                    f4 = list_pct[i + 1]
                    ret = int(f4 + (f * (f3 - f4)))
                    break

            return ret

    def getBatteryVoltage(self) -> float:
        """Return battery status information as a voltage.

        Returns:
            float: Battery power left as a voltage.
        """
        return self._batteryVoltage

    def getPosition(self) -> int:
        """Return current potision.

        Returns:
            int: The current position (-32767~0~32767)
        """
        return self._position

    def getRetCode(self) -> int:
        """Return a return code.

        Returns:
            int: The result for a locking/unlocking request.
        """
        try:
            return self._retcode
        except AttributeError:
            raise NotImplementedError("Not Implemented in Web API")

    def getTarget(self) -> int:
        """Return target potision.

        Returns:
            int: The target position (-32767~0~32767)
        """
        try:
            return self._target
        except AttributeError:
            raise NotImplementedError("Not Implemented in Web API")

    def isInLockRange(self) -> bool:
        """Return whether a device is currently locked.

        Returns:
            bool: `True` if it is locked, `False` if not.
        """
        return self._isInLockRange

    def isInUnlockRange(self) -> bool:
        """Return whether a device is currently unlocked.

        Returns:
            bool: `True` if it is unlocked, `False` if not.
        """
        return self._isInUnlockRange
