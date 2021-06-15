#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import pytest
import requests_mock
from moto import mock_cognitoidentity

from pysesame3.cloud import SesameCloud

from .utils import load_fixture


@pytest.fixture(autouse=True)
def mock_requests():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://app.candyhouse.co/api/sesame2/FAKEUUID/history?page=0&lg=10",
            json=load_fixture("history.json"),
        )

        mock.get(
            "https://jhcr1i3ecb.execute-api.ap-northeast-1.amazonaws.com/prod/device/v1/sesame2/FAKEUUID/history",
            json=load_fixture("history.json"),
        )
        yield mock


class TestSesameCloudBroken:
    def test_SesameCloud_raises_exception_on_authenticator_missing(self):
        with pytest.raises(TypeError) as excinfo:
            SesameCloud()
        assert "missing 1 required positional argument" in str(excinfo.value)
