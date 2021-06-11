from datetime import datetime
from enum import IntEnum


class CHSesame2History:
    """A class for representing a historical event of SESAME devices.

    Attributes:
        type (int): Type of event as defined in `CHSesame2History.EventType` class.
        timeStamp (int): Timestamp in milliseconds since 1970/1/1 00:00:00.
        recordID (int): Unique ID in a device.
        historyTag (bytes): Tag on the key that triggered this event.
    """

    class EventType(IntEnum):
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

    def __init__(
        self, type: int, timeStamp: int, recordID: int, historyTag: bytes = None
    ) -> None:
        self.event_type = CHSesame2History.EventType(type)
        self.timestamp = datetime.fromtimestamp(timeStamp / 1000)
        self.record_id = recordID
        self.historytag = historyTag.encode() if historyTag is not None else None

    def to_dict(self) -> dict:
        """Returns a dict representation of an object.

        Returns:
            dist: The dict representation of the object.
        """
        return {
            "recordID": self.record_id,
            "timeStamp": self.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            "type": self.event_type.name,
            "historyTag": self.historytag,
        }
