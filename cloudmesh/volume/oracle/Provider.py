import oci
from cloudmesh.common.dotdict import dotdict
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.VolumeABC import VolumeABC


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

    def update_dict(self, results):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements.
        Libcloud
        returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used
        internally.

        :param results: the original dicts.
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
            attribute_id = entry.__getattribute__("id")

            entry = {
                "availability_domain": availability_domain,
                "time_created": time_created,
                "size_in_gbs": size_in_gbs,
                "id": attribute_id,
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
        """
        Initialize provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: name of cloud
        """
        self.cloud = name
        self.config = Config()["cloudmesh.volume.oracle.credentials"]
        self.defaults = Config()["cloudmesh.volume.oracle.default"]

    def get_volume_id_from_name(self, block_storage, name):
        """
        This function get volume id from volume name

        :param block_storage: Block storage client object
        :param name: volume name
        :return: volume id
        """
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        volume_id = None
        for entry in results:
            display_name = entry.__getattribute__("display_name")
            if name == display_name:
                volume_id = entry.__getattribute__("id")
                break
        return volume_id

    def get_attachment_id_from_name(self, block_storage, name):
        """
        This function get attachment id from volume name

        :param block_storage: Block storage client object
        :param name: Name of the volume
        :return: Volume attachment id
        """
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        attachment_id = None
        for entry in results:
            display_name = entry.__getattribute__("display_name")
            if name == display_name:
                tags = entry.__getattribute__("freeform_tags")
                attachment_id = tags['attachment_id']
                break
        return attachment_id

    def status(self, name):
        """
        This function get volume status, such as "in-use", "available"

        :param name: Volume name
        :return: Volume_status
        """
        block_storage = oci.core.BlockstorageClient(self.config)
        v = block_storage.list_volumes(self.config['compartment_id'])
        volumes = v.data
        result = []
        entry = None
        for entry in volumes:
            display_name = entry.__getattribute__("display_name")
            if name == display_name:
                break
        result.append(entry)
        result = self.update_dict(result)
        return result

    def create(self, **kwargs):
        """
        This function creates a new volume with default size of 50gb.
        Default parameters are read from self.config.

        :param kwargs: Contains Volume name
        :return: Volume dictionary
        """
        arguments = dotdict(kwargs)
        block_storage = oci.core.BlockstorageClient(self.config)
        result = block_storage.create_volume(
            oci.core.models.CreateVolumeDetails(
                compartment_id=self.config['compartment_id'],
                availability_domain=self.config['availability_domain'],
                display_name=arguments.NAME
            ))
        # wait for availability of volume
        oci.wait_until(
            block_storage,
            block_storage.get_volume(result.data.id),
            'lifecycle_state',
            'AVAILABLE'
        ).data

        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        result = self.update_dict(results)
        return result

    def delete(self, name=None):
        """
        This function delete one volume.

        :param name: Volume name
        :return: Dictionary of volumes
        """
        block_storage = oci.core.BlockstorageClient(self.config)
        volume_id = self.get_volume_id_from_name(block_storage, name)
        if volume_id is not None:
            block_storage.delete_volume(volume_id=volume_id)
            # wait for termination
            oci.wait_until(
                block_storage,
                block_storage.get_volume(volume_id),
                'lifecycle_state',
                'TERMINATED'
            ).data
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        result = self.update_dict(results)
        return result

    def attach(self, NAMES=None, vm=None):
        """
        This function attaches a given volume to a given instance

        :param NAMES: Names of Volumes
        :param vm: Instance name
        :return: Dictionary of volumes
        """
        compute_client = oci.core.ComputeClient(self.config)
        # get instance id from VM name
        i = compute_client.list_instances(self.config['compartment_id'])
        instances = i.data
        instance_id = None
        for entry in instances:
            display_name = entry.__getattribute__("display_name")
            if vm == display_name:
                instance_id = entry.__getattribute__("id")
                break

        # get volumeId from Volume name
        block_storage = oci.core.BlockstorageClient(self.config)
        volume_id = self.get_volume_id_from_name(block_storage, NAMES[0])
        # attach volume to vm
        a = compute_client.attach_volume(
            oci.core.models.AttachIScsiVolumeDetails(
                display_name='IscsiVolAttachment',
                instance_id=instance_id,
                volume_id=volume_id
            )
        )

        # tag volume with attachment id. This needed during detach.
        block_storage.update_volume(
            volume_id,
            oci.core.models.UpdateVolumeDetails(
                freeform_tags={'attachment_id': a.data.id},
            ))

        # wait until attached
        oci.wait_until(
            compute_client,
            compute_client.get_volume_attachment(
                a.data.id),
            'lifecycle_state',
            'ATTACHED'
        )
        # return result after attach
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        results = self.update_dict(results)
        return results

    def detach(self, NAME=None):
        """
        This function detaches a given volume from an instance

        :param NAME: Volume name
        :return: Dictionary of volumes
        """
        compute_client = oci.core.ComputeClient(self.config)
        block_storage = oci.core.BlockstorageClient(self.config)
        attachment_id = self.get_attachment_id_from_name(block_storage, NAME)
        compute_client.detach_volume(attachment_id)
        # wait for detachment
        oci.wait_until(
            compute_client,
            compute_client.get_volume_attachment(attachment_id),
            'lifecycle_state',
            'DETACHED'
        )
        # return result after detach
        v = block_storage.list_volumes(self.config['compartment_id'])
        results = v.data
        results = self.update_dict(results)
        return results[0]

    def list(self, **kwargs):
        """
        This function list all volumes as following:
        If NAME (volume_name) is specified, it will print out info of NAME
        If NAME (volume_name) is not specified, it will print out info of all
          volumes

        :param kwargs: contains name of volume
        :return: Dictionary of volumes
        """
        block_storage = oci.core.BlockstorageClient(self.config)
        if kwargs and kwargs['NAME']:
            v = block_storage.list_volumes(self.config['compartment_id'])
            results = v.data
            entry = None
            for entry in results:
                display_name = entry.__getattribute__("display_name")
                if kwargs["NAME"] == display_name:
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
        """
        This method is not applicable to Oracle

        :param path:
        :param name:
        :return:
        """
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
        """
        This function add tag to a volume.

        :param NAME: name of volume
        :param kwargs:
                    key: name of tag
                    value: value of tag
        :return: Dictionary of volume
        """
        key = kwargs['key']
        value = kwargs['value']
        block_storage = oci.core.BlockstorageClient(self.config)
        volume_id = self.get_volume_id_from_name(block_storage, NAME)
        block_storage.update_volume(
            volume_id,
            oci.core.models.UpdateVolumeDetails(
                freeform_tags={key: value},
            )
        )
        result = self.list(NAME=NAME)[0]
        return result
