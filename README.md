# pysesame3

_Unofficial Python Library for SESAME products from CANDY HOUSE, Inc._

[![PyPI](https://img.shields.io/pypi/v/pysesame3)](https://pypi.python.org/pypi/pysesame3)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysesame3)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/mochipon/pysesame3/dev%20workflow/main)
[![Documentation Status](https://readthedocs.org/projects/pysesame3/badge/?version=latest)](https://pysesame3.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/mochipon/pysesame3/branch/main/graph/badge.svg?token=2Y7OPZTILT)](https://codecov.io/gh/mochipon/pysesame3)
![PyPI - License](https://img.shields.io/pypi/l/pysesame3)

This project aims to control SESAME devices by using **[the cloud service](https://doc.candyhouse.co/ja/flow_charts#candy-house-cloud-%E3%81%A8-wifi-module-%E7%B5%8C%E7%94%B1%E3%81%A7-sesame-%E3%82%92%E9%81%A0%E9%9A%94%E6%93%8D%E4%BD%9C)**.

* Free software: MIT license
* Documentation: [https://pysesame3.readthedocs.io](https://pysesame3.readthedocs.io)

## Supported devices

- [SESAME 3](https://jp.candyhouse.co/products/sesame3)
- [SESAME 4](https://jp.candyhouse.co/products/sesame4)
- [SESAME bot](https://jp.candyhouse.co/products/sesame3-bot)

## Features

* Retrieve the device status (battery level, locked, handle position, etc.).
* Retrieve recent events (locked, unlocked, etc.) associated with a lock.
* Needless to say, locking, unlocking and clicking (for the bot)!

## Usage

Please take a look at [the documentation](https://pysesame3.readthedocs.io/en/latest/usage/).

## Related Projects

### Libraries
| Name | Lang | Communication Method |
----|----|----
| [pysesame](https://github.com/trisk/pysesame) | Python | [Sesame API v1/v2](https://docs.candyhouse.co/v1.html)
| [pysesame2](https://github.com/yagami-cerberus/pysesame2) | Python | [Sesame API v3](https://docs.candyhouse.co/)
| [pysesame3](https://github.com/mochipon/pysesame3) | Python | [Web API](https://doc.candyhouse.co/ja/SesameAPI), [CognitoAuth (The official android SDK reverse-engineered)](https://doc.candyhouse.co/ja/android)
| [pysesameos2](https://github.com/mochipon/pysesameos2) | Python | [Bluetooth](https://doc.candyhouse.co/ja/android)

### Integrations
| Name | Description | Communication Method |
----|----|----
| [doorman](https://github.com/jp7eph/doorman) | Control SESAME3 from Homebridge by MQTT | [Web API](https://doc.candyhouse.co/ja/SesameAPI)
| [Doorlock](https://github.com/kishikawakatsumi/Doorlock) | iOS widget for Sesame 3 smart lock | [Web API](https://doc.candyhouse.co/ja/SesameAPI)
| [gopy-sesame3](https://github.com/orangekame3/gopy-sesame3) | NFC (Felica) integration | [Web API](https://doc.candyhouse.co/ja/SesameAPI)
| [homebridge-open-sesame](https://github.com/yasuoza/homebridge-open-sesame) | Homebridge plugin for SESAME3 | Cognito integration
| [homebridge-sesame-os2](https://github.com/nzws/homebridge-sesame-os2) | Homebridge Plugin for SESAME OS2 (SESAME3) | [Web API](https://doc.candyhouse.co/ja/SesameAPI)
| [sesame3-webhook](https://github.com/kunikada/sesame3-webhook) | Send SESAME3 status to specified url. (HTTP Post) | CognitoAuth (based on `pysesame3`)

## Credits & Thanks

* A huge thank you to all at [CANDY HOUSE](https://jp.candyhouse.co/) and their crowdfunding contributors!
* Thanks to [@Chabiichi](https://github.com/Chabiichi)-san for [the offer](https://github.com/mochipon/pysesame3/issues/25) to get my SESAME bot!
* This project was inspired and based on [tchellomello/python-ring-doorbell](https://github.com/tchellomello/python-ring-doorbell) and [snjoetw/py-august](https://github.com/snjoetw/py-august).
