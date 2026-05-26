"""CDN 模块。

导出 CDN 协议和实现。
"""

from taolib.testing.file_storage.cdn.cloudfront import CloudFrontCDNProvider
from taolib.testing.file_storage.cdn.generic import GenericCDNProvider
from taolib.testing.file_storage.cdn.protocols import CDNProviderProtocol

__all__ = [
    "CDNProviderProtocol",
    "CloudFrontCDNProvider",
    "GenericCDNProvider",
]


