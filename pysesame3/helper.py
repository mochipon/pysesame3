from __future__ import annotations

import sys
from enum import Enum
from typing import Union


class CHProductModel(Enum):
    WM2 = {
        "deviceModel": "wm_2",
        "isLocker": False,
        "productType": 1,
        "deviceFactory": None,
    }
    SS2 = {
        "deviceModel": "sesame_2",
        "isLocker": True,
        "productType": 0,
        "deviceFactory": "CHSesame2",
    }

    def getByModel(model: str) -> Union[CHProductModel, None]:
        if not isinstance(model, str):
            raise ValueError("Invalid Model")
        return next(
            (e for e in list(CHProductModel) if e.value["deviceModel"] == model), None
        )

    def getByValue(val: int) -> Union[CHProductModel, None]:
        if not isinstance(val, int):
            raise ValueError("Invalid Value")
        return next(
            (e for e in list(CHProductModel) if e.value["productType"] == val), None
        )

    def deviceModel(self) -> str:
        return self.value["deviceModel"]

    def isLocker(self) -> bool:
        return self.value["isLocker"]

    def productType(self) -> int:
        return self.value["productType"]

    def deviceFactory(self) -> Union[type, None]:
        if self.value["deviceFactory"] is not None:
            return getattr(sys.modules["pysesame3.lock"], self.value["deviceFactory"])
        else:
            return None


class CHSesame2MechStatus:
    def __init__(self, rawdata: str = None, dictdata: dict = None) -> None:
        """Represents a mechanical status of a device.

        Args:
            rawdata (str): The raw `mechst` string for the device from AWS IoT Shadow.
            dictdata (str): The structured `mechst` data for the device from Web API.
        """
        if rawdata is not None:
            data = bytes.fromhex(rawdata)
            self._batteryVoltage = int.from_bytes(data[0:2], "little") * 7.2 / 1023
            self._target = int.from_bytes(data[2:4], "little")
            self._position = int.from_bytes(data[4:6], "little")
            self._retcode = data[6]
            self._isInLockRange = data[7] & 2 > 0
            self._isInUnlockRange = data[7] & 4 > 0
            self._isBatteryCritical = data[7] & 32 > 0
        elif dictdata is not None:
            data = dictdata
            self._batteryVoltage = data["batteryVoltage"]
            self._position = data["position"]
            self._isInLockRange = True if data["CHSesame2Status"] == "locked" else False
            self._isInUnlockRange = (
                True if data["CHSesame2Status"] == "unlocked" else False
            )
        else:
            raise ValueError("No Input")

    def __str__(self) -> str:
        return f"CHSesame2MechStatus(Battery={self.getBatteryPrecentage()}% ({self.getBatteryVoltage():.2f}V), isInLockRange={self.isInLockRange()}, isInUnlockRange={self.isInUnlockRange()}, Position={self.getPosition()})"

    def getBatteryPrecentage(self) -> int:
        """Returns battery status information as a percentage.

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
        """Returns battery status information as a voltage.

        Returns:
            float: Battery power left as a voltage.
        """
        return self._batteryVoltage

    def getPosition(self) -> int:
        """Returns current potision.

        Returns:
            int: The current position (-32767~0~32767)
        """
        return self._position

    def getRetCode(self) -> int:
        """Returns a return code.

        Returns:
            int: The result for a locking/unlocking request.
        """
        try:
            return self._retcode
        except AttributeError:
            raise NotImplementedError("Not Implemented in Web API")

    def getTarget(self) -> int:
        """Returns target potision.

        Returns:
            int: The target position (-32767~0~32767)
        """
        try:
            return self._target
        except AttributeError:
            raise NotImplementedError("Not Implemented in Web API")

    def isInLockRange(self) -> bool:
        """Returns whether a device is currently locked.

        Returns:
            bool: `True` if it is locked, `False` if not.
        """
        return self._isInLockRange

    def isInUnlockRange(self) -> bool:
        """Returns whether a device is currently unlocked.

        Returns:
            bool: `True` if it is unlocked, `False` if not.
        """
        return self._isInUnlockRange
