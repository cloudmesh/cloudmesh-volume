from cloudmesh.volume.azure.Provider import Provider as AZProvider

p = AZProvider(name="azure",
             configuration="C:\\Users\\plj2861\\.cloudmesh\\cloudmesh.yaml")

# p.volume.service
#
# p.provider
#
# print(p.create_dir())
#
# print(p.list())

print(p)

p.create()