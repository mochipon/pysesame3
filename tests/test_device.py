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

    def test_SesameLocker_secretKey_raises_exception_on_invalid_value(self):
        d = SesameLocker(cl)

        with pytest.raises(ValueError) as excinfo:
            d.setSecretKey(123)
        assert "should be string" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            d.setSecretKey("FAKE")
        assert "length should be 32" in str(excinfo.value)

    def test_CHDevices_secretKey(self):
        d = SesameLocker(cl)

        assert d.getSecretKey() is None

        secret = "FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE"

        assert d.setSecretKey(secret) is None
        assert d.getSecretKey() == secret

    def test_SesameLocker_sesame2PublicKey_raises_exception_on_invalid_value(self):
        d = SesameLocker(cl)

        with pytest.raises(ValueError):
            d.setSesame2PublicKey(123)

    def test_CHDevices_sesame2PublicKey(self):
        d = SesameLocker(cl)

        assert d.getSesame2PublicKey() is None

        pubkey = "TestPubKey"

        assert d.setSesame2PublicKey(pubkey) is None
        assert d.getSesame2PublicKey() == pubkey

    def test_CHDevices(self):
        d = SesameLocker(cl)

        test_uuid = "42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1"
        d.setDeviceUUID(test_uuid)

        test_model = CHProductModel.SS2
        d.setProductModel(test_model)

        secret = "FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE"
        d.setSecretKey(secret)

        pubkey = "TestPubKey"
        d.setSesame2PublicKey(pubkey)

        assert (
            str(d)
            == "SesameLocker(deviceUUID=42918AD1-8154-4AFF-BD1F-F0CDE88A8DE1, deviceModel=CHProductModel.SS2, sesame2PublicKey=TestPubKey)"
        )
