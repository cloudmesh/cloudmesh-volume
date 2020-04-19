import openstack
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.VolumeABC import VolumeABC


class Provider(VolumeABC):
    kind = "opensatck"

    sample = """
    cloudmesh:
      volume:
        openstack:
          cm:
            active: true
            heading: Chameleon
            host: chameleoncloud.org
            label: chameleon
            kind: openstack
            version: train
            service: compute
          credentials:
            auth:
              username: TBD
              password: TBD
              auth_url: https://kvm.tacc.chameleoncloud.org:5000/v3
              project_id: TBD
              project_name: cloudmesh
              user_domain_name: Default
            region_name: KVM@TACC
            interface: public
            identity_api_version: '3'
            key_path: TBD/id_rsa.pub
          default:
            size: 1
            volume_type: __DEFAULT__
            
    """
    vm_state = [
        'ACTIVE',
        'BUILDING',
        'DELETED',
        'ERROR',
        'HARD_REBOOT',
        'PASSWORD',
        'PAUSED',
        'REBOOT',
        'REBUILD',
        'RESCUED',
        'RESIZED',
        'REVERT_RESIZE',
        'SHUTOFF',
        'SOFT_DELETED',
        'STOPPED',
        'SUSPENDED',
        'UNKNOWN',
        'VERIFY_RESIZE'
    ]

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "availability_zone",
                      "created_at",
                      "size",
                      "status",
                      "id",
                      "volume_type"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Availability Zone",
                       "Created At",
                       "Size",
                       "Status",
                       "Id",
                       "Volume Type"
                       ],
        }
    }

    def update_dict(self, results):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements. Typically this method is used
        internally.

        :param results: the original dicts.
        :return: The list with the modified dicts
        """

        if results is None:
            return None

        d = []

        for entry in results:
            volume_name = entry['name']
            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": volume_name,
            })
            d.append(entry)
        return d

    def status(self, volume_name):
        """
        This function get volume status, such as "in-use", "available"

        :param volume_name: Volume name
        :return: Volume_status
        """
        con = openstack.connect(**self.config)
        result = con.get_volume(name_or_id=volume_name)
        result = [result]
        result = self.update_dict(result)
        return result

    def __init__(self, name):
        """
        Initialize provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: name of cloud
        """
        self.cloud = name
        self.config = Config()["cloudmesh.volume.openstack.credentials"]
        self.defaults = Config()["cloudmesh.volume.openstack.default"]

    def create(self, **kwargs):
        """
        This function creates a new volume with default volume type __DEFAULT__.
        Default parameters are read from self.config.

        :param kwargs: Contains Volume name,size
        :return: Volume dictionary
        """
        try:
            con = openstack.connect(**self.config)
            arguments = dotdict(kwargs)
            if arguments.volume_type is None:
                arguments.volume_type = self.defaults["volume_type"]
            if arguments.size is None:
                arguments.size = self.defaults["size"]
            r = con.create_volume(name=arguments.NAME,
                                  size=arguments.size,
                                  volume_type=arguments.volume_type
                                  )
            r = [r]
            result = self.update_dict(r)
        except Exception as e:
            Console.error("Problem creating volume", traceflag=True)
            print(e)
            raise RuntimeError
        return result

    def delete(self, name=None):
        """
        This function delete one volume.

        :param name: Volume name
        :return: Dictionary of volumes
        """
        try:
            con = openstack.connect(**self.config)
            con.delete_volume(name_or_id=name)
            results = con.list_volumes()
            result = self.update_dict(results)
        except Exception as e:
            Console.error("Problem deleting volume", traceflag=True)
            print(e)
            raise RuntimeError
        return result

    def list(self, **kwargs):
        """
        This function list all volumes as following:
        If NAME (volume_name) is specified, it will print out info of NAME
        If NAME (volume_name) is not specified, it will print out info of all
          volumes

        :param kwargs: contains name of volume
        :return: Dictionary of volumes
        """
        try:
            con = openstack.connect(**self.config)
            results = con.list_volumes()
            if kwargs and kwargs['NAME']:
                result = con.get_volume(name_or_id=kwargs["NAME"])
                result = [result]
                result = self.update_dict(result)
            else:
                result = self.update_dict(results)
        except Exception as e:
            Console.error("Problem listing volumes", traceflag=True)
            print(e)
            raise RuntimeError
        return result

    def attach(self, NAMES=None, vm=None):
        """
        This function attaches a given volume to a given instance

        :param NAMES: Names of Volumes
        :param vm: Instance name
        :return: Dictionary of volumes
        """
        try:
            con = openstack.connect(**self.config)
            server = con.get_server(vm)
            volume = con.get_volume(name_or_id=NAMES[0])
            con.attach_volume(server, volume, device=None, wait=True,
                              timeout=None)
        except Exception as e:
            Console.error("Problem attaching volume", traceflag=True)
            print(e)
            raise RuntimeError
        return self.list(NAME=NAMES[0])

    def detach(self, NAME=None):
        """
        This function detaches a given volume from an instance

        :param NAME: Volume name
        :return: Dictionary of volumes
        """
        try:
            con = openstack.connect(**self.config)
            volume = con.get_volume(name_or_id=NAME)
            attachments = volume['attachments']
            server = con.get_server(attachments[0]['server_id'])
            con.detach_volume(server, volume, wait=True,
                              timeout=None)
        except Exception as e:
            Console.error("Problem detaching volume", traceflag=True)
            print(e)
            raise RuntimeError
        return self.list(NAME=NAME)[0]

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
        raise NotImplemented
