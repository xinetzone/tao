class QRCodeError(Exception):
    pass


class InvalidContentError(QRCodeError):
    pass


class InvalidColorError(QRCodeError):
    pass


class InvalidSizeError(QRCodeError):
    pass


class LogoProcessingError(QRCodeError):
    pass
