from enum import Enum, auto

OFFICIALAPI_URL = "https://app.candyhouse.co/api/sesame2"
APIGW_URL = "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod"
IOT_EP = "a3i4hui4gxwoo8-ats.iot.ap-northeast-1.amazonaws.com"


class AuthType(Enum):
    WebAPI = auto()
    SDK = auto()
