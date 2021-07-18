#!/usr/bin/env python

"""Tests for `pysesame3` package."""


import pytest

from pysesame3.history import CHSesame2History

from .utils import load_fixture


class TestCHSesame2History:
    @pytest.fixture(autouse=True)
    def _load_json(self):
        self._json_entries = load_fixture("history.json")
        self._json_entries_webapi = load_fixture("history_webapi.json")

    def test_CHSesame2History_raises_exception_on_missing_arguments(self):
        with pytest.raises(TypeError):
            CHSesame2History()

    def test_CHSesame2History_raises_exception_on_unknown_event_type(self):
        with pytest.raises(AttributeError) as excinfo:
            CHSesame2History.EventType.UNDEFINEDEVENTFORTEST
        assert str(excinfo.value) == "UNDEFINEDEVENTFORTEST"

        with pytest.raises(ValueError) as excinfo:
            CHSesame2History.EventType(12345)
        assert "12345 is not a valid" in str(excinfo.value)

    def test_CHSesame2History_passes_on_unknown_event_type(self):
        his = CHSesame2History(type=12345, timeStamp=1597492862, recordID=1)
        assert his.event_type == CHSesame2History.EventType.unknown

    def test_CHSesame2History(self):
        h = CHSesame2History(**(self._json_entries[0]))

        assert h.to_dict() == {
            "recordID": 200,
            "timeStamp": "2021/06/07 17:33:20",
            "type": "webUnLock",
            "historyTag": "ThisIsTest",
            "devicePk": None,
            "parameter": None,
        }

    def test_CHSesame2History_minimum(self):
        h = CHSesame2History(**(self._json_entries[1]))

        assert h.to_dict() == {
            "recordID": 201,
            "timeStamp": "2021/06/07 17:50:34",
            "type": "manualLocked",
            "historyTag": None,
            "devicePk": None,
            "parameter": None,
        }

    def test_CHSesame2History_WebAPI(self):
        h = CHSesame2History(**(self._json_entries_webapi[0]))

        assert h.to_dict() == {
            "recordID": 255,
            "timeStamp": "1970/01/19 20:44:52",
            "type": "bleUnLock",
            "historyTag": "ドラえもん",
            "devicePk": "5469bc01e40fe65ca2b7baaf55171ddb",
            "parameter": None,
        }
