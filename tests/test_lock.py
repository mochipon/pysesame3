#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import pytest
import requests_mock
from moto import mock_cognitoidentity

from pysesame3.auth import CognitoAuth, WebAPIAuth
from pysesame3.history import CHSesame2History
from pysesame3.lock import CHSesame2, CHSesame2ShadowStatus

from .utils import load_fixture


@pytest.fixture(autouse=True)
def mock_requests():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43",
            json=load_fixture("lock_get_locked.json"),
        )

        mock.get(
            "https://app.candyhouse.co/api/sesame2/e0e56521-63d8-4da5-ba4b-c4a6a5e353f1",
            json=load_fixture("lock_get_unlocked.json"),
        )

        mock.post(
            "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43/cmd"
        )

        mock.post(
            "https://app.candyhouse.co/api/sesame2/e0e56521-63d8-4da5-ba4b-c4a6a5e353f1/cmd"
        )

        mock.get(
            "https://a3i4hui4gxwoo8-ats.iot.ap-northeast-1.amazonaws.com/things/sesame2/shadow?name=126D3D66-9222-4E5A-BCDE-0C6629D48D43",
            json=load_fixture("lock_shadow_locked.json"),
        )

        mock.get(
            "https://a3i4hui4gxwoo8-ats.iot.ap-northeast-1.amazonaws.com/things/sesame2/shadow?name=E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1",
            json=load_fixture("lock_shadow_unlocked.json"),
        )

        mock.post(
            "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod/device/v1/iot/sesame2/126D3D66-9222-4E5A-BCDE-0C6629D48D43"
        )

        mock.post(
            "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod/device/v1/iot/sesame2/E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1"
        )

        mock.get(
            "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43/history?page=0&lg=10",
            json=load_fixture("history.json"),
        )

        mock.get(
            "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod/device/v1/sesame2/126D3D66-9222-4E5A-BCDE-0C6629D48D43/history",
            json=load_fixture("history.json"),
        )
        yield mock


@pytest.fixture()
def mock_cloud():
    cl = WebAPIAuth(apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE")
    yield cl


@pytest.fixture()
def mock_cloud_cognito():
    with mock_cognitoidentity():
        cl = CognitoAuth(
            apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE",
            client_id="ap-northeast-1:fakefakefake",
        )
        yield cl


class TestCHSesame2Broken:
    def test_CHSesame2_raises_exception_on_missing_arguments(self):
        with pytest.raises(TypeError):
            CHSesame2()

        with pytest.raises(TypeError):
            CHSesame2(mock_cloud)

    def test_CHSesame2_raises_exception_on_invalid_arguments(self):
        with pytest.raises(ValueError):
            key = {
                "device_uuid": "FAKEUUID",
                "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
            }
            CHSesame2(mock_cloud, **key)

        with pytest.raises(ValueError):
            key = {
                "device_uuid": "126D3D66-9222-4E5A-BCDE-0C6629D48D43",
                "secret_key": "FAKE_SECRET_KEY",
            }
            CHSesame2(mock_cloud, **key)


class TestCHSesame2:
    @pytest.fixture(autouse=True)
    def _initialize_key(self, mock_cloud):
        key = {
            "device_uuid": "126D3D66-9222-4E5A-BCDE-0C6629D48D43",
            "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
        }
        self.key_locked = CHSesame2(mock_cloud, **key)

        key = {
            "device_uuid": "E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1",
            "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
        }
        self.key_unlocked = CHSesame2(mock_cloud, **key)

    def test_CHSesame2(self):
        assert (
            str(self.key_locked)
            == "CHSesame2(deviceUUID=126D3D66-9222-4E5A-BCDE-0C6629D48D43, deviceModel=None, sesame2PublicKey=None, mechStatus=CHSesame2MechStatus(Battery=67% (5.87V), isInLockRange=True, isInUnlockRange=False, Position=11))"
        )

    def test_CHSesame2_getDeviceShadowStatus(self):
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        assert (
            self.key_unlocked.getDeviceShadowStatus()
            == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_SesameCloud_getHistoryEntries(self):
        entries = self.key_locked.historyEntries

        assert isinstance(entries, list)
        assert len(entries) == 2
        assert isinstance(entries[0], CHSesame2History)
        assert isinstance(entries[1], CHSesame2History)

    def test_CHSesame2_setDeviceShadowStatus_toggle(self):
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        self.key_locked.setDeviceShadowStatus(CHSesame2ShadowStatus.UnlockedWm)
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_CHSesame2_setDeviceShadowStatus_raises_exception_on_invalid_status(self):
        with pytest.raises(ValueError):
            self.key_locked.setDeviceShadowStatus("INVALID")

    def test_CHSesame2_lock_fails_HTTP_requests(self):
        with requests_mock.Mocker() as mock:
            mock.post(
                "https://app.candyhouse.co/api/sesame2/e0e56521-63d8-4da5-ba4b-c4a6a5e353f1/cmd",
                status_code=500,
            )
            assert not self.key_unlocked.lock()
            assert (
                self.key_unlocked.getDeviceShadowStatus()
                == CHSesame2ShadowStatus.UnlockedWm
            )

    def test_CHSesame2_lock(self):
        assert self.key_unlocked.lock()
        assert (
            self.key_unlocked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        )

    def test_CHSesame2_unlock(self):
        assert self.key_locked.unlock()
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_CHSesame2_toggle(self):
        assert self.key_locked.toggle()
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )
        assert self.key_locked.toggle()
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm

        assert self.key_unlocked.toggle()
        assert (
            self.key_unlocked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        )
        assert self.key_unlocked.toggle()
        assert (
            self.key_unlocked.getDeviceShadowStatus()
            == CHSesame2ShadowStatus.UnlockedWm
        )


class TestCHSesame2Cognito:
    @pytest.fixture(autouse=True)
    def _initialize_key(self, mock_cloud_cognito):
        key = {
            "device_uuid": "126D3D66-9222-4E5A-BCDE-0C6629D48D43",
            "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
        }
        self.key_locked = CHSesame2(mock_cloud_cognito, **key)

        key = {
            "device_uuid": "E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1",
            "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
        }
        self.key_unlocked = CHSesame2(mock_cloud_cognito, **key)

    def test_CHSesame2(self):
        assert (
            str(self.key_locked)
            == "CHSesame2(deviceUUID=126D3D66-9222-4E5A-BCDE-0C6629D48D43, deviceModel=None, sesame2PublicKey=None, mechStatus=CHSesame2MechStatus(Battery=100% (6.11V), isInLockRange=True, isInUnlockRange=False, Position=29))"
        )

    def test_CHSesame2_getDeviceShadowStatus(self):
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        assert (
            self.key_unlocked.getDeviceShadowStatus()
            == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_SesameCloud_getHistoryEntries(self):
        entries = self.key_locked.historyEntries

        assert isinstance(entries, list)
        assert len(entries) == 2
        assert isinstance(entries[0], CHSesame2History)
        assert isinstance(entries[1], CHSesame2History)

    def test_CHSesame2_setDeviceShadowStatus_toggle(self):
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        self.key_locked.setDeviceShadowStatus(CHSesame2ShadowStatus.UnlockedWm)
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_CHSesame2_setDeviceShadowStatus_raises_exception_on_invalid_status(self):
        with pytest.raises(ValueError):
            self.key_locked.setDeviceShadowStatus("INVALID")

    def test_CHSesame2_lock_fails_HTTP_requests(self):
        with requests_mock.Mocker() as mock:
            mock.post(
                "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod/device/v1/iot/sesame2/E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1",
                status_code=500,
            )
            assert not self.key_unlocked.lock()
            assert (
                self.key_unlocked.getDeviceShadowStatus()
                == CHSesame2ShadowStatus.UnlockedWm
            )

    def test_CHSesame2_lock(self):
        assert self.key_unlocked.lock()
        assert (
            self.key_unlocked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        )

    def test_CHSesame2_unlock(self):
        assert self.key_locked.unlock()
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_CHSesame2_toggle(self):
        assert self.key_locked.toggle()
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )
        assert self.key_locked.toggle()
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm

        assert self.key_unlocked.toggle()
        assert (
            self.key_unlocked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        )
        assert self.key_unlocked.toggle()
        assert (
            self.key_unlocked.getDeviceShadowStatus()
            == CHSesame2ShadowStatus.UnlockedWm
        )
