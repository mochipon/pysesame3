from enum import Enum, IntEnum, auto

OFFICIALAPI_URL = "https://app.candyhouse.co/api/sesame2"
APIGW_URL = "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod"
IOT_EP = "a3i4hui4gxwoo8-ats.iot.ap-northeast-1.amazonaws.com"


class AuthType(Enum):
    WebAPI = auto()
    SDK = auto()


class CHSesame2CMD(IntEnum):
    LOCK = 82
    UNLOCK = 83
    TOGGLE = 88
    CLICK = 89


class CHSesame2ShadowStatus(Enum):
    LockedWm = auto()
    UnlockedWm = auto()
    MovedWm = auto()
