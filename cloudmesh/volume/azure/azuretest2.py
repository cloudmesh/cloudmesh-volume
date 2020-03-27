# import cloudmesh.storage.provider.gdrive.Provider as cmProvider
import cloudmesh.volume.provider.azureblob.Provider as Provider

p = Provider(service="azureblob", config='path to config')

#p.storage.service
p.volume.service

print(p.create_dir())

print(p.list())
