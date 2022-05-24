#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import boto3
import pytest
import requests
from moto import mock_cognitoidentity

from pysesame3.auth import CognitoAuth, WebAPIAuth
from pysesame3.const import CLIENT_ID


def test_WebAPIAuth_raises_exception_on_missing_arguments():
    with pytest.raises(TypeError):
        WebAPIAuth()


def test_WebAPIAuth_raises_exception_on_invalid_apikey():
    with pytest.raises(ValueError) as excinfo:
        WebAPIAuth(apikey="thisisfake")
    assert "length should be 40" in str(excinfo.value)


def test_CognitoAuth_raises_exception_on_missing_arguments():
    with pytest.raises(TypeError) as excinfo:
        CognitoAuth()
    assert "required positional argument" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        CognitoAuth(client_id="us-east-1:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    assert "required positional argument" in str(excinfo.value)


def test_CognitoAuth_raises_exception_on_invalid_apikey():
    with pytest.raises(ValueError) as excinfo:
        CognitoAuth(
            apikey="fake", client_id="us-east-1:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        )
    assert "length should be 40" in str(excinfo.value)


@mock_cognitoidentity
def test_CognitoAuth_call_raises_exception_on_broken_PreparedRequest():
    cognito_identity = boto3.client("cognito-identity", region_name="ap-northeast-1")
    identity_pool_data = cognito_identity.create_identity_pool(
        IdentityPoolName="test_identity_pool", AllowUnauthenticatedIdentities=False
    )

    c = CognitoAuth(
        apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE",
        client_id=identity_pool_data["IdentityPoolId"],
    )
    req = requests.PreparedRequest()

    with pytest.raises(TypeError):
        c(req)


def test_CognitoAuth_uses_default_CLIENT_ID():
    c = CognitoAuth(
        apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE",
    )
    assert c.client_id == CLIENT_ID


@mock_cognitoidentity
def test_CognitoAuth_authenticate():
    cognito_identity = boto3.client("cognito-identity", region_name="ap-northeast-1")
    identity_pool_data = cognito_identity.create_identity_pool(
        IdentityPoolName="test_identity_pool", AllowUnauthenticatedIdentities=False
    )

    c = CognitoAuth(
        apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE",
        client_id=identity_pool_data["IdentityPoolId"],
    )

    (access_key_id, secret_key, session_token) = c.authenticate()

    assert access_key_id == "TESTACCESSKEY12345"
    assert secret_key == "ABCSECRETKEY"
    assert session_token == "ABC12345"
