#!/usr/bin/env python

"""Tests for `pysesame3` package."""


import pytest
from pysesame3.history import CHSesame2History

from .utils import load_fixture


class TestCHSesame2History:
    @pytest.fixture(autouse=True)
    def _load_json(self):
        self._json_entries = load_fixture("history.json")

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

        with pytest.raises(ValueError) as excinfo:
            CHSesame2History(type=12345, timeStamp=1597492862, recordID=1)
        assert "12345 is not a valid" in str(excinfo.value)

    def test_CHSesame2History(self):
        h = CHSesame2History(**(self._json_entries[0]))

        assert h.to_dict() == {
            "recordID": 200,
            "timeStamp": "2021/06/07 17:33:20",
            "type": "webUnLock",
            "historyTag": "VGhpc0lzVGVzdA==".encode(),
        }

    def test_CHSesame2History_minimum(self):
        h = CHSesame2History(**(self._json_entries[1]))

        assert h.to_dict() == {
            "recordID": 201,
            "timeStamp": "2021/06/07 17:50:34",
            "type": "manualLocked",
            "historyTag": None,
        }
