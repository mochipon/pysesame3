# pysesame3

_Unofficial Python Library to communicate with Sesame smart locks made by CANDY HOUSE, Inc._

[![PyPI](https://img.shields.io/pypi/v/pysesame3)](https://pypi.python.org/pypi/pysesame3)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysesame3)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/mochipon/pysesame3/dev%20workflow/main)
[![Documentation Status](https://readthedocs.org/projects/pysesame3/badge/?version=latest)](https://pysesame3.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/mochipon/pysesame3/branch/main/graph/badge.svg?token=2Y7OPZTILT)](https://codecov.io/gh/mochipon/pysesame3)
![PyPI - License](https://img.shields.io/pypi/l/pysesame3)

* Free software: MIT license
* Documentation: [https://pysesame3.readthedocs.io](https://pysesame3.readthedocs.io)

## Features

Please note that `pysesame3` can only control [SESAME 3](https://jp.candyhouse.co/products/sesame3) at this moment.

* Retrive a list of SESAME locks that the user is authorized to use.
* Retrive a status of a SESAME lock (locked, handle position, etc.).
* Retrive recent events (locked, unlocked, etc.) associated with a lock.
* Needless to say, locking and unlocking!

## Usage

Please take a look at [the documentation](https://pysesame3.readthedocs.io/en/latest/usage/).

## Credits & Thanks

* A huge thank you to all who assisted with [CANDY HOUSE](https://jp.candyhouse.co/).
* This project was inspired and based on [tchellomello/python-ring-doorbell](https://github.com/tchellomello/python-ring-doorbell) and [snjoetw/py-august](https://github.com/snjoetw/py-august).
