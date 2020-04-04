from cloudmesh.volume.azure.Provider import Provider as AZProvider
from pprint import pprint

p = AZProvider(name="azure",
             configuration="C:\\Users\\plj2861\\.cloudmesh\\cloudmesh.yaml")

print(p)

# pprint(p.create())
# pprint(p.delete())
# pprint(p.list())
pprint(p.attach())
# p.detach()
# p.migrate()
# p.sync()
