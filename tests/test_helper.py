#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import pytest
from pysesame3.helper import CHProductModel, CHSesame2MechStatus


class TestCHProductModel:
    def test_CHProductModel_raises_exception_on_invalid_model(self):
        with pytest.raises(AttributeError):
            CHProductModel.SS99

    def test_CHProductModel_SS2(self):
        ss2 = CHProductModel.SS2
        assert ss2.deviceModel() == "sesame_2"
        assert ss2.isLocker()
        assert ss2.productType() == 0
        assert ss2.deviceFactory().__name__ == "CHSesame2"

    def test_CHProductModel_WM2(self):
        wm2 = CHProductModel.WM2
        assert wm2.deviceModel() == "wm_2"
        assert not wm2.isLocker()
        assert wm2.productType() == 1
        assert wm2.deviceFactory() is None

    def test_CHProductModel_getByModel_raises_exception_on_invalid_arguments(self):
        with pytest.raises(ValueError):
            CHProductModel.getByModel(123)

    def test_CHProductModel_getByModel_returns_None_for_unknown_model(self):
        assert CHProductModel.getByModel("sesame_99") is None

    def test_CHProductModel_getByModel_returns_SS2(self):
        assert CHProductModel.getByModel("sesame_2") is CHProductModel.SS2

    def test_CHProductModel_getByValue_raises_exception_on_invalid_arguments(self):
        with pytest.raises(ValueError):
            CHProductModel.getByValue("0")

    def test_CHProductModel_getByValue_returns_None_for_unknown_model(self):
        assert CHProductModel.getByValue(999) is None

    def test_CHProductModel_getByValue_returns_SS2(self):
        assert CHProductModel.getByValue(0) is CHProductModel.SS2


class TestCHSesame2MechStatus:
    def test_CHSesame2MechStatus_raises_exception_on_emtry_arguments(self):
        with pytest.raises(ValueError):
            CHSesame2MechStatus()

    def test_CHSesame2MechStatus_raises_exception_on_non_string_argument(self):
        with pytest.raises(TypeError):
            CHSesame2MechStatus(10)

    def test_CHSesame2MechStatus_dictdata_locked(self):
        status = CHSesame2MechStatus(
            dictdata={
                "batteryVoltage": 5.869794721407625,
                "position": 11,
                "CHSesame2Status": "locked",
            }
        )

        assert status.getBatteryPrecentage() == 67
        assert status.getBatteryVoltage() == 5.869794721407625
        assert status.getPosition() == 11
        with pytest.raises(NotImplementedError):
            status.getRetCode()
        with pytest.raises(NotImplementedError):
            status.getTarget()
        assert status.isInLockRange()
        assert not status.isInUnlockRange()
        assert (
            str(status)
            == "CHSesame2MechStatus(Battery=67% (5.87V), isInLockRange=True, isInUnlockRange=False, Position=11)"
        )

    def test_CHSesame2MechStatus_dictdata_unlocked(self):
        status = CHSesame2MechStatus(
            dictdata={
                "batteryVoltage": 5.869794721407625,
                "position": 11,
                "CHSesame2Status": "unlocked",
            }
        )

        assert status.getBatteryPrecentage() == 67
        assert status.getBatteryVoltage() == 5.869794721407625
        assert status.getPosition() == 11
        with pytest.raises(NotImplementedError):
            status.getRetCode()
        with pytest.raises(NotImplementedError):
            status.getTarget()
        assert not status.isInLockRange()
        assert status.isInUnlockRange()
        assert (
            str(status)
            == "CHSesame2MechStatus(Battery=67% (5.87V), isInLockRange=False, isInUnlockRange=True, Position=11)"
        )

    def test_CHSesame2MechStatus_dictdata_various_battery(self):
        status = CHSesame2MechStatus(
            dictdata={
                "batteryVoltage": 0.0,
                "position": 0,
                "CHSesame2Status": "locked",
            }
        )
        assert status.getBatteryPrecentage() == 0
        assert status.getBatteryVoltage() == 0.0

        status2 = CHSesame2MechStatus(
            dictdata={
                "batteryVoltage": 5.5,
                "position": 0,
                "CHSesame2Status": "locked",
            }
        )
        assert status2.getBatteryPrecentage() == 26
        assert status2.getBatteryVoltage() == 5.5

    def test_CHSesame2MechStatus_rawdata_locked(self):
        status = CHSesame2MechStatus(rawdata="60030080f3ff0002")

        assert status.getBatteryPrecentage() == 100.0
        assert status.getBatteryVoltage() == 6.0809384164222875
        assert status.getPosition() == 65523
        assert status.getRetCode() == 0
        assert status.getTarget() == 32768
        assert status.isInLockRange()
        assert not status.isInUnlockRange()
        assert (
            str(status)
            == "CHSesame2MechStatus(Battery=100% (6.08V), isInLockRange=True, isInUnlockRange=False, Position=65523)"
        )

    def test_CHSesame2MechStatus_rawdata_unlocked(self):
        status = CHSesame2MechStatus(rawdata="5c030503e3020004")

        assert status.getBatteryPrecentage() == 100.0
        assert status.getBatteryVoltage() == 6.052785923753666
        assert status.getPosition() == 739
        assert status.getRetCode() == 0
        assert status.getTarget() == 773
        assert not status.isInLockRange()
        assert status.isInUnlockRange()
        assert (
            str(status)
            == "CHSesame2MechStatus(Battery=100% (6.05V), isInLockRange=False, isInUnlockRange=True, Position=739)"
        )
