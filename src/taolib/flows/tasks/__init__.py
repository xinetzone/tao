from invoke import Collection
from . import doc

def sites(source='doc', target='.temp/html', children=''):
    source = children if children else source
    _config = {"sphinx": {
        "source": source,
        "target": f"{target}/{children}"
    }}
    namespace = Collection()
    namespace.add_collection(doc)
    namespace.collections['doc'].configure(_config)
    return namespace
