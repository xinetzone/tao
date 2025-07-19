import inspect
if not hasattr(inspect, 'getargspec'): # 修复
    inspect.getargspec = inspect.getfullargspec
import logging
from taolib.flows.tasks import sites

logging.basicConfig(level=logging.INFO)
namespace = sites('doc', target='doc/_build/html')
