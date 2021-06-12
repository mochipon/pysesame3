#!/usr/bin/env python

"""Tests for `pysesame3` package."""

import pytest

from pysesame3.auth import WebAPIAuth


def test_WebAPIAuth_raises_exception_on_missing_arguments():
    with pytest.raises(TypeError):
        WebAPIAuth()


def test_WebAPIAuth_raises_exception_on_invalid_apikey():
    with pytest.raises(ValueError) as excinfo:
        WebAPIAuth(apikey="thisisfake")
    assert "length should be 40" in str(excinfo.value)
