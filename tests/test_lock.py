#!/usr/bin/env python

"""Tests for `pysesame3` package."""


import pytest


def test_lock_module_shows_warning(caplog):
    import pysesame3.lock

    assert 'This "lock" module is duplecated' in caplog.text


def test_lock_module_provides_backward_compatibility():
    from pysesame3.lock import CHSesame2

    assert CHSesame2.__module__ == "pysesame3.chsesame2"
    assert CHSesame2.__name__ == "CHSesame2"
