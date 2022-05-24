#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import asyncio
import sys

import boto3

if sys.version_info[:2] < (3, 8):
    from asynctest import patch
else:
    from unittest.mock import patch

import pytest
import requests_mock
from moto import mock_cognitoidentity

from pysesame3.auth import CognitoAuth
from pysesame3.cloud import AWSIoT, SesameCloud

from .utils import load_fixture


@pytest.fixture(autouse=True)
def mock_requests():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://app.candyhouse.co/api/sesame2/FAKEUUID/history?page=0&lg=10",
            json=load_fixture("history.json"),
        )
        yield mock


class TestSesameCloudBroken:
    def test_SesameCloud_raises_exception_on_authenticator_missing(self):
        with pytest.raises(TypeError) as excinfo:
            SesameCloud()
        assert "missing 1 required positional argument" in str(excinfo.value)


class TestAWSIoTBroken:
    def test_AWSIoT_raises_exception_on_authenticator_missing(self):
        with pytest.raises(TypeError) as excinfo:
            AWSIoT()
        assert "missing 1 required positional argument" in str(excinfo.value)


class TestAWSIoT:
    @pytest.fixture(autouse=True)
    def aws_iot(self):
        with mock_cognitoidentity():
            cognito_identity = boto3.client(
                "cognito-identity", region_name="ap-northeast-1"
            )
            identity_pool_data = cognito_identity.create_identity_pool(
                IdentityPoolName="test_identity_pool",
                AllowUnauthenticatedIdentities=False,
            )
            cl = CognitoAuth(
                apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE",
                client_id=identity_pool_data["IdentityPoolId"],
            )
            yield AWSIoT(cl)

    def test_AWSIoT_connect(self, aws_iot):
        with patch("pysesame3.cloud.mqtt.Connection.connect") as connect:

            def _connect(*args, **kwargs):
                f = asyncio.Future()
                f.set_result(True)
                return f

            connect.side_effect = _connect
            aws_iot.connect()
            connect.assert_called_once()

            aws_iot.connect()
            assert connect.call_count == 2
