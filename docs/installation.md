# Installation

## Stable release

To install pysesame3, run this command in your
terminal:

``` console
$ pip install pysesame3
```

If you want to use `CognitoAuth`, run this command instead.

``` console
$ pip install pysesame3[cognito]
```

!!! Note
    `pysesame3[cognito]` depends on [`awscrt`](https://github.com/awslabs/aws-crt-python), which makes use of **C** extensions. [Precompiled wheels](https://pypi.org/project/awscrt/#files) are automatically installed for major platforms ([manylinux](https://github.com/pypa/manylinux#readme) including Raspberry Pi OS, macOS and Windows) so there is no additional dependency in most environments.

    If wheels are unavailable for your platform, you may encounter some issues in installation. Please rerfer to [the document](https://github.com/aws/aws-iot-device-sdk-python-v2#installation-issues).


This is the preferred method to install pysesame3, as it will always install the most recent stable release.

If you don't have [pip][] installed, this [Python installation guide][]
can guide you through the process.

## From source

The source for pysesame3 can be downloaded from
the [Github repo][].

You can either clone the public repository:

``` console
$ git clone git://github.com/mochipon/pysesame3
```

Or download the [tarball][]:

``` console
$ curl -OJL https://github.com/mochipon/pysesame3/tarball/master
```

Once you have a copy of the source, you can install it with:

``` console
$ poetry install --no-dev
```

If you want to use `CognitoAuth`, run this command instead.

``` console
$ poetry install --no-dev -E cognito
```



  [pip]: https://pip.pypa.io
  [Python installation guide]: http://docs.python-guide.org/en/latest/starting/installation/
  [Github repo]: https://github.com/mochipon/pysesame3
  [tarball]: https://github.com/mochipon/pysesame3/tarball/main
