#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import pytest

from pysesame3.helper import (
    CHProductModel,
    CHSesame2MechStatus,
    CHSesameBotMechStatus,
    CHSesameProtocolMechStatus,
    RegexHelper,
)


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

        with pytest.raises(NotImplementedError):
            wm2.deviceFactory()

    def test_CHProductModel_getByModel_raises_exception_on_invalid_arguments(self):
        with pytest.raises(TypeError):
            CHProductModel.getByModel(123)

    def test_CHProductModel_getByModel_returns_None_for_unknown_model(self):
        with pytest.raises(NotImplementedError):
            CHProductModel.getByModel("sesame_99")

    def test_CHProductModel_getByModel_returns_SS2(self):
        assert CHProductModel.getByModel("sesame_2") is CHProductModel.SS2

    def test_CHProductModel_getByValue_raises_exception_on_invalid_arguments(self):
        with pytest.raises(TypeError):
            CHProductModel.getByValue("0")

    def test_CHProductModel_getByValue_returns_None_for_unknown_model(self):
        with pytest.raises(NotImplementedError):
            CHProductModel.getByValue(999)

    def test_CHProductModel_getByValue_returns_SS2(self):
        assert CHProductModel.getByValue(0) is CHProductModel.SS2


class TestCHSesameProtocolMechStatus:
    def test_TestCHSesameProtocolMechStatus_raises_exception_on_emtry_arguments(self):
        with pytest.raises(TypeError):
            CHSesameProtocolMechStatus()

    def test_CHSesameProtocolMechStatus_raises_exception_on_non_string_argument(self):
        with pytest.raises(TypeError):
            CHSesameProtocolMechStatus(10)

    def test_CHSesameProtocolMechStatus(self):
        status = CHSesameProtocolMechStatus(rawdata="60030080f3ff0002")
        assert status.isInLockRange()

        status = CHSesameProtocolMechStatus(rawdata=bytes.fromhex("60030080f3ff0002"))
        assert status.isInLockRange()


class TestCHSesame2MechStatus:
    def test_CHSesame2MechStatus_raises_exception_on_emtry_arguments(self):
        with pytest.raises(TypeError):
            CHSesame2MechStatus()

    def test_CHSesame2MechStatus_raises_exception_on_non_string_argument(self):
        with pytest.raises(TypeError):
            CHSesame2MechStatus(10)

    def test_CHSesame2MechStatus_dictdata_locked(self):
        status = CHSesame2MechStatus(
            {
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
            == "CHSesame2MechStatus(Battery=67% (5.87V), isInLockRange=True, isInUnlockRange=False, position=11)"
        )

    def test_CHSesame2MechStatus_dictdata_unlocked(self):
        status = CHSesame2MechStatus(
            {
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
            == "CHSesame2MechStatus(Battery=67% (5.87V), isInLockRange=False, isInUnlockRange=True, position=11)"
        )

    def test_CHSesame2MechStatus_dictdata_various_battery(self):
        status = CHSesame2MechStatus(
            {
                "batteryVoltage": 0.0,
                "position": 0,
                "CHSesame2Status": "locked",
            }
        )
        assert status.getBatteryPrecentage() == 0
        assert status.getBatteryVoltage() == 0.0

        status2 = CHSesame2MechStatus(
            {
                "batteryVoltage": 5.5,
                "position": 0,
                "CHSesame2Status": "locked",
            }
        )
        assert status2.getBatteryPrecentage() == 26
        assert status2.getBatteryVoltage() == 5.5

    def test_CHSesame2MechStatus_rawdata_locked(self):
        status = CHSesame2MechStatus("60030080f3ff0002")

        assert status.getBatteryPrecentage() == 100.0
        assert status.getBatteryVoltage() == 6.0809384164222875
        assert status.getPosition() == -13
        assert status.getRetCode() == 0
        assert status.getTarget() == -32768
        assert status.isInLockRange()
        assert not status.isInUnlockRange()
        assert (
            str(status)
            == "CHSesame2MechStatus(Battery=100% (6.08V), isInLockRange=True, isInUnlockRange=False, retCode=0, target=-32768, position=-13)"
        )

    def test_CHSesame2MechStatus_rawdata_unlocked(self):
        status = CHSesame2MechStatus("5c030503e3020004")

        assert status.getBatteryPrecentage() == 100.0
        assert status.getBatteryVoltage() == 6.052785923753666
        assert status.getPosition() == 739
        assert status.getRetCode() == 0
        assert status.getTarget() == 773
        assert not status.isInLockRange()
        assert status.isInUnlockRange()
        assert (
            str(status)
            == "CHSesame2MechStatus(Battery=100% (6.05V), isInLockRange=False, isInUnlockRange=True, retCode=0, target=773, position=739)"
        )


class TestCHSesameBotMechStatus:
    def test_CHSesameBotMechStatus_raises_exception_on_emtry_arguments(self):
        with pytest.raises(TypeError):
            CHSesameBotMechStatus()

    def test_CHSesameBotMechStatus_raises_exception_on_non_string_argument(self):
        with pytest.raises(TypeError):
            CHSesameBotMechStatus(10)

    def test_CHSesameBotMechStatus_rawdata_locked(self):
        status = CHSesameBotMechStatus(rawdata="5503000000000102")

        assert status.getBatteryPrecentage() == 100.0
        assert status.getBatteryVoltage() == 3.001759530791789
        assert status.isInLockRange()
        assert not status.isInUnlockRange()
        assert status.getMotorStatus() == 0
        assert (
            str(status) == "CHSesameBotMechStatus(Battery=100% (3.00V), motorStatus=0)"
        )

        status = CHSesameBotMechStatus(rawdata=bytes.fromhex("5503000000000102"))
        assert (
            str(status) == "CHSesameBotMechStatus(Battery=100% (3.00V), motorStatus=0)"
        )

    def test_CHSesameBotMechStatus_rawdata_unlocked(self):
        status = CHSesameBotMechStatus(rawdata="5503000000000104")

        assert status.getBatteryPrecentage() == 100.0
        assert status.getBatteryVoltage() == 3.001759530791789
        assert not status.isInLockRange()
        assert status.isInUnlockRange()
        assert status.getMotorStatus() == 0
        assert (
            str(status) == "CHSesameBotMechStatus(Battery=100% (3.00V), motorStatus=0)"
        )

    def test_CHSesameBotMechStatus_rawdata_lowpower(self):
        status = CHSesameBotMechStatus(rawdata="3003000000000102")
        assert status.getBatteryPrecentage() == 44
        assert status.getBatteryVoltage() == 2.8715542521994135

        status2 = CHSesameBotMechStatus(rawdata="4802000000000102")
        assert status2.getBatteryPrecentage() == 0


class TestRegexHelper:
    def test_get_aws_region_raises_exception_with_unknown_str(self):
        with pytest.raises(ValueError):
            RegexHelper.get_aws_region("INVALID")

    def test_get_aws_region(self):
        assert (
            RegexHelper.get_aws_region(
                "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod"
            )
            == "ap-northeast-1"
        )
        assert (
            RegexHelper.get_aws_region(
                "a3i4hui4gxwoo8-ats.iot.ap-northeast-1.amazonaws.com"
            )
            == "ap-northeast-1"
        )
        assert (
            RegexHelper.get_aws_region("us-west-1:126D3D66-9222-4E5A-BCDE-0C6629D48D43")
            == "us-west-1"
        )
