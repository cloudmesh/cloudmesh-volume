# import cloudmesh.storage.provider.gdrive.Provider as cmProvider
from cloudmesh.volume.azure.Provider import Provider as AZProvider

p = AZProvider(name="azure",
             configuration="C:\\Users\\plj2861\\.cloudmesh\\cloudmesh.yaml")
# cmp = cmProvider(service="azure", config='path to config')

#p.storage.service
# p.volume.service
#
# p.provider
#
# print(p.create_dir())
#
# print(p.list())

print(p)