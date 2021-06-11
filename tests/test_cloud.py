#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import pytest
import requests_mock
from pysesame3.cloud import SesameCloud
from pysesame3.history import CHSesame2History

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


class TestSesameCloudOfficial:
    @pytest.fixture(autouse=True)
    def _load_SesameCloud(self):
        class FakeDevice:
            @property
            def authenticator(self):
                return None

            def getDeviceUUID(self):
                return "FAKEUUID"

        self.cl = SesameCloud(FakeDevice())

    def test_SesameCloud_getHistoryEntries(self):
        entries = self.cl.getHistoryEntries()

        assert isinstance(entries, list)
        assert len(entries) == 2
        assert isinstance(entries[0], CHSesame2History)
        assert isinstance(entries[1], CHSesame2History)
