from cloudmesh.volume.azure.Provider import Provider as AZProvider

p = AZProvider(name="azure",
             configuration="C:\\Users\\plj2861\\.cloudmesh\\cloudmesh.yaml")

print(p)

# p.create()
p.attach()
