#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import pytest

from pysesame3.auth import CognitoAuth, WebAPIAuth


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
        CognitoAuth(apikey="FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE")
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
