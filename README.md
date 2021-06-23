# pysesame3

_Unofficial Python Library to communicate with SESAME 3 series products from CANDY HOUSE, Inc._

This project aims to control SESAME 3 series devices by using **[the cloud service](https://doc.candyhouse.co/ja/flow_charts#%E9%80%8F%E9%81%8E-candy-house-cloud--wifi-module-%E5%82%B3%E9%80%81%E6%8C%87%E4%BB%A4%E7%B5%A6-sesame)**.
If you want to control them directly via **Bluetooth connection**, please check [pysesameos2](https://github.com/mochipon/pysesameos2). 

[![PyPI](https://img.shields.io/pypi/v/pysesame3)](https://pypi.python.org/pypi/pysesame3)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysesame3)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/mochipon/pysesame3/dev%20workflow/main)
[![Documentation Status](https://readthedocs.org/projects/pysesame3/badge/?version=latest)](https://pysesame3.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/mochipon/pysesame3/branch/main/graph/badge.svg?token=2Y7OPZTILT)](https://codecov.io/gh/mochipon/pysesame3)
![PyPI - License](https://img.shields.io/pypi/l/pysesame3)


* Free software: MIT license
* Documentation: [https://pysesame3.readthedocs.io](https://pysesame3.readthedocs.io)

## Features

Please note that `pysesame3` can only control [SESAME 3 Smart Lock](https://jp.candyhouse.co/products/sesame3) at this moment. It could technically support [SESAME Bot](https://jp.candyhouse.co/collections/frontpage/products/sesame3-bot) as well, but I don't have that device. PRs are always welcome!

* Retrieve a status of a SESAME lock (locked, handle position, etc.).
* Retrieve recent events (locked, unlocked, etc.) associated with a lock.
* Needless to say, locking and unlocking!

## Usage

Please take a look at [the documentation](https://pysesame3.readthedocs.io/en/latest/usage/).

## Credits & Thanks

* A huge thank you to all who assisted with [CANDY HOUSE](https://jp.candyhouse.co/).
* This project was inspired and based on [tchellomello/python-ring-doorbell](https://github.com/tchellomello/python-ring-doorbell) and [snjoetw/py-august](https://github.com/snjoetw/py-august).
