#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import uuid

import pytest

from pysesame3.auth import WebAPIAuth
from pysesame3.device import CHDevices, SesameLocker
from pysesame3.helper import CHProductModel


@pytest.fixture(autouse=True)
def cl():
    yield WebAPIAuth(apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE")


class TestCHDevices:
    def test_CHDevices_deviceId_raises_exception_on_invalid_uuid(self):
        d = CHDevices(cl)

        with pytest.raises(ValueError):
            d.setDeviceId("INVALID-UUID")

        with pytest.raises(ValueError):
            d.setDeviceId(12345)

    def test_CHDevices_deviceId(self):
        d = CHDevices(cl)

        assert d.deviceId is None

        test_uuid = "42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1"
        assert d.setDeviceId(test_uuid) is None
        assert d.deviceId == test_uuid

        test_uuid2 = uuid.UUID("42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1")
        assert d.setDeviceId(test_uuid2) is None
        assert d.deviceId == str(test_uuid2).upper()

    def test_CHDevices_productModel_raises_exception_on_invalid_uuid(self):
        d = CHDevices(cl)

        with pytest.raises(ValueError):
            d.setProductModel("INVALID-PRODUCT")

    def test_CHDevices_productModel(self):
        d = CHDevices(cl)

        assert d.productModel is None

        test_model = CHProductModel.SS2
        assert d.setProductModel(test_model) is None
        assert d.productModel == test_model


class TestSesameLocker:
    def test_SesameLocker_deviceUUID_raises_exception_on_invalid_uuid(self):
        d = SesameLocker(cl)

        with pytest.raises(ValueError):
            d.setDeviceUUID("INVALID-UUID")

    def test_CHDevices_deviceUUID(self):
        d = SesameLocker(cl)

        assert d.getDeviceUUID() is None

        test_uuid = "42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1"
        assert d.setDeviceUUID(test_uuid) is None
        assert d.getDeviceUUID() == test_uuid

        test_uuid2 = uuid.UUID("42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1")
        assert d.setDeviceUUID(test_uuid2) is None
        assert d.getDeviceUUID() == str(test_uuid2).upper()

    def test_CHDevices_secretKey_raises_exception_on_invalid_value(self):
        k = SesameLocker(cl)

        with pytest.raises(TypeError) as excinfo:
            k.setSecretKey(123)
        assert "should be str or bytes" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            k.setSecretKey("FAKE")
        assert "non-hexadecimal number found" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            k.setSecretKey("FEED")
        assert "length should be 16" in str(excinfo.value)

    def test_CHDevices_secretKey(self):
        k = SesameLocker(cl)

        assert k.getSecretKey() is None

        secret_str = "34344f4734344b3534344f4934344f47"
        secret_bytes = bytes.fromhex(secret_str)

        assert k.setSecretKey(secret_bytes) is None
        assert k.getSecretKey() == secret_bytes

        assert k.setSecretKey(secret_str) is None
        assert k.getSecretKey() == secret_bytes

    def test_CHDevices(self):
        d = SesameLocker(cl)

        test_uuid = "42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1"
        d.setDeviceUUID(test_uuid)

        test_model = CHProductModel.SS2
        d.setProductModel(test_model)

        secret = "34344f4734344b3534344f4934344f47"
        d.setSecretKey(secret)

        assert (
            str(d)
            == "SesameLocker(deviceUUID=42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1, deviceModel=CHProductModel.SS2)"
        )
