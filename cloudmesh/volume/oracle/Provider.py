import pprint
import oci
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.Printer import Printer


class Provider(VolumeABC):
    kind = "oracle"

    sample = """
    cloudmesh:
      volume:
        {name}:
          cm:
            active: true
            heading: {name}
            host: TBD
            label: {name}
            kind: oracle
            version: TBD
            service: volume
          credentials:
            version: TBD
            user: TBD
            fingerprint: TBD
            key_file: oci_api_key.pem
            pass_phrase: TBD
            tenancy: TBD
            compartment_id: TBD
            region: TBD
            availability_domain: TBD
          default:
    """

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "availability_domain",
                      "time_created",
                      "size_in_gbs",
                      "lifecycle_state",
                      "id"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Availability Zone",
                       "Created At",
                       "Size(Gb)",
                       "Status",
                       "Id"
                       ],
        }
    }

    def Print(self, data, output=None, kind=None):
        order = self.output["volume"]['order']
        header = self.output["volume"]['header']
        print(Printer.flatwrite(data,
                                sort_keys=["name"],
                                order=order,
                                header=header,
                                output=output,
                                )
              )

    def update_dict(self, results):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements.
        Libcloud
        returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used
        internally.

        :param results: the original dicts.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """

        if results is None:
            return None

        d = []

        for entry in results:
            display_name = entry.__getattribute__("display_name")
            availability_domain = entry.__getattribute__("availability_domain")
            time_created = entry.__getattribute__("time_created")
            size_in_gbs = entry.__getattribute__("size_in_gbs")
            lifecycle_state = entry.__getattribute__("lifecycle_state")
            id = entry.__getattribute__("id")

            entry = {
                "availability_domain": availability_domain,
                "time_created": time_created,
                "size_in_gbs": size_in_gbs,
                "id": id,
                "lifecycle_state": lifecycle_state
            }

            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": display_name,
            })
            d.append(entry)

        return d

    def __init__(self, name):
        self.cloud = name
        self.config = Config()["cloudmesh.volume.oracle.credentials"]
        self.defaults = Config()["cloudmesh.volume.oracle.default"]

    def getVolumeIdFromName(self,block_storage,name):
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        volumeId = None
        for entry in results:
            display_name = entry.__getattribute__("display_name")
            if(name==display_name):
                volumeId=entry.__getattribute__("id")
                break
        return volumeId

    def getAttachmentIdFromName(self,block_storage,name):
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        attachmentid = None
        for entry in results:
            display_name = entry.__getattribute__("display_name")
            if(name==display_name):
                tags = entry.__getattribute__("freeform_tags")
                attachmentid = tags['attachmentid']
                break
        return attachmentid

    def status(self, name):
        block_storage = oci.core.BlockstorageClient(self.config)
        v = block_storage.list_volumes(self.config['compartment_id'])
        volumes = v.data
        result = []
        for entry in volumes:
            display_name = entry.__getattribute__("display_name")
            if (name == display_name):
                break
        result.append(entry)
        result = self.update_dict(result)
        return result

    def create(self, **kwargs):
        arguments = dotdict(kwargs)
        block_storage = oci.core.BlockstorageClient(self.config)
        result = block_storage.create_volume(
            oci.core.models.CreateVolumeDetails(
                                        compartment_id=self.config['compartment_id'],
                                        availability_domain=self.config['availability_domain'],
                                        display_name=arguments.NAME
                                    ))
        #wait for availability of volume
        volume = oci.wait_until(
            block_storage,
            block_storage.get_volume(result.data.id),
            'lifecycle_state',
            'AVAILABLE'
        ).data

        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        result = self.update_dict(results)
        return result
        #print(self.Print(result, kind='volume', output=kwargs['output']))

    def delete(self, name=None):
        block_storage = oci.core.BlockstorageClient(self.config)
        print("oracle delete volume",name)
        volumeId = self.getVolumeIdFromName(block_storage,name)
        if(volumeId!=None):
            block_storage.delete_volume(volume_id=volumeId)
            #wait for termination
            volume = oci.wait_until(
                block_storage,
                block_storage.get_volume(volumeId),
                'lifecycle_state',
                'TERMINATED'
            ).data
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        result = self.update_dict(results)
        #print(self.Print(result, kind='volume', output='table'))
        return result

    def attach(self, NAMES=None, vm=None):
        compute_client = oci.core.ComputeClient(self.config)
        #get instance id from VM name
        i = compute_client.list_instances(self.config['compartment_id'])
        instances = i.data;
        instanceId = None
        for entry in instances:
            display_name = entry.__getattribute__("display_name")
            if(vm==display_name):
                instanceId=entry.__getattribute__("id")
                break

        #get volumeId from Volume name
        block_storage = oci.core.BlockstorageClient(self.config)
        volumeId = self.getVolumeIdFromName(block_storage, NAMES[0])
        #attach volume to vm
        a = compute_client.attach_volume(
            oci.core.models.AttachIScsiVolumeDetails(
                display_name='IscsiVolAttachment',
                instance_id=instanceId,
                volume_id=volumeId
            )
        )

        #tag volume with attachment id. This needed during detach.
        result = block_storage.update_volume(
            volumeId,
            oci.core.models.UpdateVolumeDetails(
                freeform_tags={'attachmentid':a.data.id},
            ))

        #wait until attached
        oci.wait_until(
            compute_client,
            compute_client.get_volume_attachment(
                a.data.id),
            'lifecycle_state',
            'ATTACHED'
        )
        #return result after attach
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        results = self.update_dict(results)
        return results

    def detach(self, NAME=None):
        compute_client = oci.core.ComputeClient(self.config)
        block_storage = oci.core.BlockstorageClient(self.config)
        attachmentId = self.getAttachmentIdFromName(block_storage, NAME)
        compute_client.detach_volume(attachmentId)
        #wait for detachment
        oci.wait_until(
            compute_client,
            compute_client.get_volume_attachment(attachmentId),
            'lifecycle_state',
            'DETACHED'
        )
        #return result after detach
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        results = self.update_dict(results)
        return results[0]

    def list(self, **kwargs):
        block_storage = oci.core.BlockstorageClient(self.config)
        if kwargs and kwargs['NAME']:
            v = block_storage.list_volumes(self.config['compartment_id'])
            results = v.data
            for entry in results:
                display_name = entry.__getattribute__("display_name")
                if (kwargs["NAME"] == display_name):
                    break
            result = [entry]
            result = self.update_dict(result)
            return result
        else:
            v = block_storage.list_volumes(self.config['compartment_id'])
            results = v.data
            results = self.update_dict(results)
            return results

    def mount(self, path=None, name=None):
        raise NotImplementedError

    def migrate(self,
                name=None,
                fvm=None,
                tvm=None,
                fregion=None,
                tregion=None,
                fservice=None,
                tservice=None,
                fcloud=None,
                tcloud=None,
                cloud=None,
                region=None,
                service=None):
        """
        Migrate volume from one vm to another vm.

        :param name: name of volume
        :param fvm: name of vm where volume will be moved from
        :param tvm: name of vm where volume will be moved to
        :param fregion: the region where the volume will be moved from
        :param tregion: region where the volume will be moved to
        :param fservice: the service where the volume will be moved from
        :param tservice: the service where the volume will be moved to
        :param fcloud: the provider where the volume will be moved from
        :param tcloud: the provider where the volume will be moved to
        :param cloud: the provider where the volume will be moved within
        :param region: the region where the volume will be moved within
        :param service: the service where the volume will be moved within
        :return: dict

        """

        raise NotImplementedError

    def sync(self,
             volume_id=None,
             zone=None,
             cloud=None):
        """
        sync contents of one volume to another volume

        :param volume_id: id of volume A
        :param zone: zone where new volume will be created
        :param cloud: the provider where volumes will be hosted
        :return: str
        """
        raise NotImplementedError

    def add_tag(self, NAME, **kwargs):
        raise NotImplemented



