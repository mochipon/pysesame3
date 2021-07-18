import base64
from datetime import datetime
from enum import IntEnum
from typing import Optional


class CHSesame2History:
    """A class for representing a historical event of SESAME devices.

    Attributes:
        type (int): Type of event as defined in `CHSesame2History.EventType` class.
        timeStamp (int): Timestamp in milliseconds since 1970/1/1 00:00:00.
        recordID (int): Unique ID in a device.
        historyTag (bytes): Tag on the key that triggered this event.
    """

    class EventType(IntEnum):
        unknown = -1
        none = 0
        bleLock = 1
        bleUnLock = 2
        timeChanged = 3
        autoLockUpdated = 4
        mechSettingUpdated = 5
        autoLock = 6
        manualLocked = 7
        manualUnlocked = 8
        manualElse = 9
        driveLocked = 10
        driveUnlocked = 11
        driveFailed = 12
        bleAdvParameterUpdated = 13
        wm2Lock = 14
        wm2UnLock = 15
        webLock = 16
        webUnLock = 17
        # 18 will be wm2Click or webClick
        EVENT_18 = 18
        driveClick = 21
        manualClick = 22

    def __init__(
        self,
        type: int,
        timeStamp: float,
        recordID: int,
        historyTag: Optional[str] = None,
        devicePk: Optional[str] = None,
        parameter=None,
    ) -> None:
        try:
            self.event_type = CHSesame2History.EventType(type)
        except ValueError:
            self.event_type = CHSesame2History.EventType.unknown
        self.timestamp = datetime.fromtimestamp(timeStamp / 1000)
        self.record_id = recordID
        self.historytag = historyTag
        self.devicePk = devicePk
        self.parameter = parameter

    def to_dict(self) -> dict:
        """Return a dict representation of an object.

        Returns:
            dist: The dict representation of the object.
        """
        return {
            "recordID": self.record_id,
            "timeStamp": self.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            "type": self.event_type.name,
            "historyTag": base64.b64decode(self.historytag).decode("utf-8")
            if self.historytag is not None
            else None,
            "devicePk": self.devicePk,
            "parameter": self.parameter,
        }
