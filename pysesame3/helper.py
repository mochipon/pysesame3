import importlib
import logging
import re
import sys
from enum import Enum
from typing import Dict, Union

if sys.version_info[:2] >= (3, 8):
    from typing import TypedDict
else:  # pragma: no cover
    from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


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
    SS4: ProductData = {
        "deviceModel": "sesame_4",
        "isLocker": True,
        "productType": 4,
        "deviceFactory": "CHSesame2",
    }
    SesameBot1: ProductData = {
        "deviceModel": "ssmbot_1",
        "isLocker": True,
        "productType": 2,
        "deviceFactory": "CHSesameBot",
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


class CHSesameProtocolMechStatus:
    def __init__(self, rawdata: Union[bytes, str, Dict]) -> None:
        """Represent a mechanical status of a device.

        Args:
            rawdata (Union[bytes, str, dict]): The raw `mechst` data for the device.
        """
        if isinstance(rawdata, str):
            rawdata = bytes.fromhex(rawdata)

        if isinstance(rawdata, bytes):
            self._isInLockRange = rawdata[7] & 2 > 0
            self._isInUnlockRange = rawdata[7] & 4 > 0
            self._isBatteryCritical = rawdata[7] & 32 > 0
        elif isinstance(rawdata, dict):
            self._isInLockRange = (
                True if rawdata["CHSesame2Status"] == "locked" else False
            )
            self._isInUnlockRange = not self._isInLockRange
        else:
            raise TypeError("Invalid input type")

        self._batteryVoltage: float
        self._target: int
        self._position: int
        self._retcode: int

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


class CHSesame2MechStatus(CHSesameProtocolMechStatus):
    def __init__(self, rawdata: Union[bytes, str, Dict]) -> None:
        """Represent a mechanical status of a SESAME3.

        Args:
            rawdata (Union[bytes, str, Dict]): The raw `mechst` data for the device.
        """
        if isinstance(rawdata, str):
            rawdata = bytes.fromhex(rawdata)

        if isinstance(rawdata, bytes):
            super().__init__(rawdata)

            self._batteryVoltage = int.from_bytes(rawdata[0:2], "little") * 7.2 / 1023
            self._target = int.from_bytes(rawdata[2:4], "little", signed=True)
            self._position = int.from_bytes(rawdata[4:6], "little", signed=True)
            self._retcode = rawdata[6]
        elif isinstance(rawdata, dict):
            super().__init__(rawdata)

            self._batteryVoltage = rawdata["batteryVoltage"]
            self._position = rawdata["position"]
        else:
            raise TypeError("Invalid input type")

    def getBatteryPercentage(self) -> int:
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

    def getBatteryPrecentage(self) -> int:
        """Return battery status information as a percentage.
        The method name contains typo, kept for backward compatibility.

        Returns:
            int: Battery power left as a percentage.
        """
        logger.error(
            'This "getBatteryPrecentage" method is duplecated. Please use "getBatteryPercentage" instead.'
        )
        return self.getBatteryPercentage()

    def __str__(self) -> str:
        try:
            return f"CHSesame2MechStatus(Battery={self.getBatteryPercentage()}% ({self.getBatteryVoltage():.2f}V), isInLockRange={self.isInLockRange()}, isInUnlockRange={self.isInUnlockRange()}, retCode={self.getRetCode()}, target={self.getTarget()}, position={self.getPosition()})"
        except NotImplementedError:
            return f"CHSesame2MechStatus(Battery={self.getBatteryPercentage()}% ({self.getBatteryVoltage():.2f}V), isInLockRange={self.isInLockRange()}, isInUnlockRange={self.isInUnlockRange()}, position={self.getPosition()})"


class CHSesameBotMechStatus(CHSesameProtocolMechStatus):
    def __init__(self, rawdata: Union[bytes, str, Dict]) -> None:
        """Represent a mechanical status of a SESAME bot.

        Args:
            rawdata (Union[bytes, str, Dict]): The raw `mechst` data for the device.
        """
        if isinstance(rawdata, str):
            rawdata = bytes.fromhex(rawdata)

        if isinstance(rawdata, bytes):
            super().__init__(rawdata)

            self._batteryVoltage = int.from_bytes(rawdata[0:2], "little") * 3.6 / 1023
            self._motorStatus = rawdata[4]
        elif isinstance(rawdata, dict):
            super().__init__(rawdata)

            # TODO: Watch carefully for any change in the response from SESAME Cloud.
            # The Web API always responds with the same type for all devices at this moment.
            # That is, even for SESAME bot, it also appears to have a battery voltage of 6V,
            # and it also has a position field.
            # This is clearly wrong and is very likely to be changed in the future.
            self._batteryVoltage = rawdata["batteryVoltage"]
            self._motorStatus = rawdata["position"]
        else:
            raise TypeError("Invalid input type")

    def getBatteryPercentage(self) -> int:
        """Return battery status information as a percentage.

        Returns:
            int: Battery power left as a percentage.
        """
        if self._batteryVoltage > 4.5:
            # TODO: Remove this workaround
            # The Web API weirdly answers as if the SESAME bot's
            # rated battery voltage is 6V.
            # This is clearly wrong and is very likely to be changed in the future.
            list_vol = [6.0, 5.8, 5.7, 5.6, 5.4, 5.2, 5.1, 5.0, 4.8, 4.6]
        else:
            list_vol = [3.0, 2.9, 2.85, 2.8, 2.7, 2.6, 2.55, 2.5, 2.4, 2.3]
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

    def getBatteryPrecentage(self) -> int:
        """Return battery status information as a percentage.
        The method name contains typo, kept for backward compatibility.

        Returns:
            int: Battery power left as a percentage.
        """
        logger.error(
            'This "getBatteryPrecentage" method is duplecated. Please use "getBatteryPercentage" instead.'
        )
        return self.getBatteryPercentage()

    def getMotorStatus(self) -> int:
        return self._motorStatus

    def __str__(self) -> str:
        return f"CHSesameBotMechStatus(Battery={self.getBatteryPercentage()}% ({self.getBatteryVoltage():.2f}V), motorStatus={self.getMotorStatus()})"


class RegexHelper:
    @staticmethod
    def get_aws_region(text: str) -> str:
        result = re.search(
            r"(us(-gov)?|ap|ca|cn|eu|sa)-(central|(north|south)?(east|west)?)-\d", text
        )
        if result:
            return result.group(0)
        else:
            raise ValueError("Failed to extract a region name.")
