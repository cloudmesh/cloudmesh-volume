# import cloudmesh.storage.provider.gdrive.Provider as Provider
import cloudmesh.volume.provider.azureblob.Provider as Provider

p = Provider(service="azure", config='path to config')

#p.storage.service
p.volume.service

print(p.create_dir())

print(p.list())
