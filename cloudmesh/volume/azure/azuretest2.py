from cloudmesh.volume.azure.Provider import Provider as AZProvider
from pprint import pprint
from cloudmesh.common.util import path_expand

configuration = path_expand("~/.cloudmesh/cloudmesh.yaml")

p = AZProvider(name="azure",
             configuration=configuration)

print(p)

# pprint(p.create())
# pprint(p.delete())
# pprint(p.list())
# pprint(p.attach())
pprint(p.detach())
# pprint(p.status())
# pprint(p.info())
# pprint(p.add_tag())
# pprint(p.migrate())
# pprint(p.sync())
