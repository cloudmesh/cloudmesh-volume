# import cloudmesh.storage.provider.gdrive.Provider as cmProvider
import cloudmesh.volume.provider.azureblob.Provider as Provider

p = Provider(service="azureblob", config='path to config')
cmp = cmProvider(service="azureblob", config='path to config')

#p.storage.service
p.volume.service

p.provider

print(p.create_dir())

print(p.list())





# # oracle list
#
# def list(self, **kwargs):
#     if kwargs["--refresh"]:
#         block_storage = oci.core.BlockstorageClient(self.config)
#         v = block_storage.list_volumes(self.config['compartment_id'])
#         results = v.data
#         result = self.update_dict(results)
#         print(self.Print(result, kind='volume', output=kwargs['output']))
#     else:
#         # read record from mongoDB
#         refresh = False
#
#
# # openstack list
#
#     def list(self,**kwargs):
#         if kwargs["--refresh"]:
#             con = openstack.connect(**self.config)
#             results = con.list_volumes()
#             result = self.update_dict(results)
#             print(self.Print(result, kind='volume', output=kwargs['output']))
#         else:
#             # read record from mongoDB
#             refresh = False
#
#
# # aws list
#
#     def list(self,**kwargs):
#         client = boto3.client('ec2')
#         dryrun = kwargs['--dryrun']
#         result = client.describe_volumes(
#             DryRun=dryrun,
#         result = self.update_dict(result)
#         return result