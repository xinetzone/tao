from invoke import Collection

from . import doc
from . import release

# def site(name='docs', target='output/html'):
#     if name == 'docs':
#         out = ''
#     else:
#         out = name
#     _config = {"sphinx": {
#         "source": name,
#         "target": f"{target}/{out}"
#     }}
#     namespace = Collection()
#     namespace.add_collection(release)
#     namespace.add_collection(docs)
#     namespace.collections['docs'].configure(_config)
#     return namespace

def site(source='docs', target='output/html', children=''):
    source = children if children else source
    _config = {"sphinx": {
        "source": source,
        "target": f"{target}/{children}"
    }}
    namespace = Collection()
    namespace.add_collection(release)
    namespace.add_collection(doc)
    namespace.collections['doc'].configure(_config)
    return namespace