#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import json
from unittest.mock import MagicMock, PropertyMock

import boto3
import pytest
import requests_mock
from moto import mock_cognitoidentity

from pysesame3.auth import CognitoAuth, WebAPIAuth
from pysesame3.chsesamebot import CHSesameBot
from pysesame3.const import CHSesame2ShadowStatus
from pysesame3.helper import CHSesameBotMechStatus
from pysesame3.history import CHSesame2History

from .utils import TypeMatcher, load_fixture


@pytest.fixture(autouse=True)
def mock_requests():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43",
            json=load_fixture("button_get_locked.json"),
        )

        mock.get(
            "https://app.candyhouse.co/api/sesame2/e0e56521-63d8-4da5-ba4b-c4a6a5e353f1",
            json=load_fixture("button_get_unlocked.json"),
        )

        mock.post(
            "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43/cmd"
        )

        mock.post(
            "https://app.candyhouse.co/api/sesame2/e0e56521-63d8-4da5-ba4b-c4a6a5e353f1/cmd"
        )

        mock.get(
            "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43/history?page=0&lg=10",
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
        cognito_identity = boto3.client(
            "cognito-identity", region_name="ap-northeast-1"
        )
        identity_pool_data = cognito_identity.create_identity_pool(
            IdentityPoolName="test_identity_pool", AllowUnauthenticatedIdentities=False
        )

        cl = CognitoAuth(
            apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE",
            client_id=identity_pool_data["IdentityPoolId"],
        )
        yield cl


class TestCHSesameBotBroken:
    def test_CHSesameBot_raises_exception_on_missing_arguments(self):
        with pytest.raises(TypeError):
            CHSesameBot()

        with pytest.raises(TypeError):
            CHSesameBot(mock_cloud)

    def test_CHSesameBot_raises_exception_on_invalid_arguments(self):
        with pytest.raises(ValueError):
            key = {
                "device_uuid": "FAKEUUID",
                "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
            }
            CHSesameBot(mock_cloud, **key)

        with pytest.raises(ValueError):
            key = {
                "device_uuid": "126D3D66-9222-4E5A-BCDE-0C6629D48D43",
                "secret_key": "FAKE_SECRET_KEY",
            }
            CHSesameBot(mock_cloud, **key)


class TestCHSesameBot:
    @pytest.fixture(autouse=True)
    def _initialize_key(self, mock_cloud):
        key = {
            "device_uuid": "126D3D66-9222-4E5A-BCDE-0C6629D48D43",
            "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
        }
        self.key_locked = CHSesameBot(mock_cloud, **key)

    def test_CHSesameBot(self):
        assert (
            str(self.key_locked)
            == "CHSesameBot(deviceUUID=126D3D66-9222-4E5A-BCDE-0C6629D48D43, deviceModel=CHProductModel.SesameBot1, mechStatus=CHSesameBotMechStatus(Battery=100% (6.00V), motorStatus=0))"
        )

    def test_CHSesameBot_subscribeMechStatus_raises_exception_with_WebAPI(self):
        def _callback(*_):
            return True

        with pytest.raises(NotImplementedError):
            self.key_locked.subscribeMechStatus(_callback)

    def test_CHSesameBot_getDeviceShadowStatus(self):
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm

    def test_SesameCloud_getHistoryEntries(self):
        entries = self.key_locked.historyEntries

        assert isinstance(entries, list)
        assert len(entries) == 2
        assert isinstance(entries[0], CHSesame2History)
        assert isinstance(entries[1], CHSesame2History)

    def test_CHSesameBot_setDeviceShadowStatus_toggle(self):
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        self.key_locked.setDeviceShadowStatus(CHSesame2ShadowStatus.UnlockedWm)
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_CHSesameBot_setDeviceShadowStatus_raises_exception_on_invalid_status(self):
        with pytest.raises(ValueError):
            self.key_locked.setDeviceShadowStatus("INVALID")

    def test_CHSesameBot_click_fails_HTTP_requests(self):
        with requests_mock.Mocker() as mock:
            mock.post(
                "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43/cmd",
                status_code=500,
            )
            assert not self.key_locked.click()
            assert (
                self.key_locked.getDeviceShadowStatus()
                == CHSesame2ShadowStatus.LockedWm
            )

    def test_CHSesameBot_click(self):
        assert self.key_locked.click()
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm


class TestCHSesameBotCognito:
    @pytest.fixture(autouse=True)
    def _initialize_key(self, mock_cloud_cognito):
        key = {
            "device_uuid": "126D3D66-9222-4E5A-BCDE-0C6629D48D43",
            "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
        }
        self.key_locked = CHSesameBot(mock_cloud_cognito, **key)

        key = {
            "device_uuid": "E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1",
            "secret_key": "0b3e5f1665e143b59180c915fa4b06d9",
        }
        self.key_unlocked = CHSesameBot(mock_cloud_cognito, **key)

    def test_CHSesameBot(self):
        assert (
            str(self.key_locked)
            == "CHSesameBot(deviceUUID=126D3D66-9222-4E5A-BCDE-0C6629D48D43, deviceModel=CHProductModel.SesameBot1, mechStatus=CHSesameBotMechStatus(Battery=100% (6.00V), motorStatus=0))"
        )

    def test_CHSesameBot_iot_shadow_callback_with_missing_mechst(self):
        assert (
            self.key_locked._iot_shadow_callback(
                "$aws/things/sesame2/shadow/name/126D3D66-9222-4E5A-BCDE-0C6629D48D43/update/accepted",
                json.dumps(load_fixture("shadow_missing_mechst.json")).encode(),
            )
            is None
        )
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm

    def test_CHSesameBot_iot_shadow_callback_state_changes_to_unlocked(self):
        assert (
            self.key_locked._iot_shadow_callback(
                "$aws/things/sesame2/shadow/name/126D3D66-9222-4E5A-BCDE-0C6629D48D43/update/accepted",
                json.dumps(load_fixture("lock_shadow_unlocked.json")).encode(),
            )
            is None
        )
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_CHSesameBot_iot_shadow_callback_state_changes_to_locked(self):
        assert (
            self.key_unlocked._iot_shadow_callback(
                "$aws/things/sesame2/shadow/name/E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1/update/accepted",
                json.dumps(load_fixture("lock_shadow_locked.json")).encode(),
            )
            is None
        )
        assert (
            self.key_unlocked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        )

    def test_CHSesameBot_iot_shadow_callback_with_user_dedefined_callback(self):
        m = MagicMock()
        self.key_unlocked._callback = m

        self.key_unlocked._iot_shadow_callback(
            "$aws/things/sesame2/shadow/name/E0E56521-63D8-4DA5-BA4B-C4A6A5E353F1/update/accepted",
            json.dumps(load_fixture("lock_shadow_locked.json")).encode(),
        )
        m.assert_called_once_with(
            TypeMatcher(CHSesameBot), TypeMatcher(CHSesameBotMechStatus)
        )

    def test_CHSesameBot_subscribeMechStatus_raises_exception_on_invalid_arguments(
        self,
    ):
        with pytest.raises(TypeError):
            self.key_locked.subscribeMechStatus("NOT-CALLABLE")

    def test_CHSesameBot_subscribeMechStatus(self):
        # TODO: Make tests using moto
        pass

    def test_CHSesameBot_getDeviceShadowStatus(self):
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

    def test_CHSesameBot_setDeviceShadowStatus_toggle(self):
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
        self.key_locked.setDeviceShadowStatus(CHSesame2ShadowStatus.UnlockedWm)
        assert (
            self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.UnlockedWm
        )

    def test_CHSesameBot_setDeviceShadowStatus_raises_exception_on_invalid_status(self):
        with pytest.raises(ValueError):
            self.key_locked.setDeviceShadowStatus("INVALID")

    def test_CHSesameBot_click_fails_HTTP_requests(self):
        with requests_mock.Mocker() as mock:
            mock.post(
                "https://app.candyhouse.co/api/sesame2/126d3d66-9222-4e5a-bcde-0c6629d48d43/cmd",
                status_code=500,
            )
            assert not self.key_locked.click()
            assert (
                self.key_locked.getDeviceShadowStatus()
                == CHSesame2ShadowStatus.LockedWm
            )

    def test_CHSesameBot_click(self):
        assert self.key_locked.click()
        assert self.key_locked.getDeviceShadowStatus() == CHSesame2ShadowStatus.LockedWm
