import uvicorn

from taolib.testing.qrcode.server.app import create_app
from taolib.testing.qrcode.server.config import QRCodeServerConfig


def main() -> None:
    config = QRCodeServerConfig()
    app = create_app()
    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()


