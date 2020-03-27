# import cloudmesh.storage.provider.gdrive.Provider as cmProvider
import cloudmesh.volume.provider.azureblob.Provider as Provider

p = Provider(service="azureblob", config='path to config')
cmp = cmProvider(service="azureblob", config='path to config')

#p.storage.service
p.volume.service

p.provider

print(p.create_dir())

print(p.list())
