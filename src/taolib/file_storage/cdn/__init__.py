"""CDN 模块。

导出 CDN 协议和实现。
"""

from taolib.file_storage.cdn.cloudfront import CloudFrontCDNProvider
from taolib.file_storage.cdn.generic import GenericCDNProvider
from taolib.file_storage.cdn.protocols import CDNProviderProtocol

__all__ = [
    "CDNProviderProtocol",
    "CloudFrontCDNProvider",
    "GenericCDNProvider",
]
