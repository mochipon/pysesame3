## Example Usage

```python
import time

from pysesame3.auth import WebAPIAuth
from pysesame3.key import CHSesame2


def main():
    auth = Authenticator(
        apikey="fake_apikey"
    )

    """
    You can get the information you need by decoding a QR code
    from the app.
    https://sesame-qr-reader.vercel.app/
    """
    your_key_uuid = "67d1f7cb-dee0-4c93-b989-0eede693a9ba"
    your_key_secret = "secret-secret-secret"

    device = CHSesame2(
        authenticator=auth,
        device_uuid=your_key_uuid,
        secret_key=your_key_secret
    )

    print((str(device.mechStatus))

    device.unlock()
    time.sleep(5)

    print((str(device.mechStatus))

    device.toggle()
    time.sleep(5)

    print((str(device.mechStatus))

if __name__ == "__main__":
    main()
```
