import pprint
import openstack
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.Printer import Printer

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
        print("results", results)

        for entry in results:
            print("entry",entry)
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

    def __init__(self,name):
        self.cloud = name
        self.config = Config()["cloudmesh.volume.openstack.credentials"]
        self.defaults = Config()["cloudmesh.volume.openstack.default"]

    def create(self, **kwargs):
        con = openstack.connect(**self.config)
        arguments = dotdict(kwargs)
        if arguments.volume_type == None:
            arguments.volume_type=self.defaults["volume_type"]
        if arguments.size == None:
            arguments.size=self.defaults["size"]
        print(arguments.NAME)
        con.create_volume(name=arguments.NAME,size=arguments.size,volume_type=arguments.volume_type)
        #print list after create
        results = con.list_volumes()
        result = self.update_dict(results)
        print(self.Print(result, kind='volume', output=kwargs['output']))

    def delete(self, name=None):
        config = self.credentials()
        con = openstack.connect(**config)
        con.delete_volume(name_or_id=name)
        
    def list(self,**kwargs):
        if kwargs["--refresh"]:
            con = openstack.connect(**self.config)
            results = con.list_volumes()
            result = self.update_dict(results)
            print(self.Print(result, kind='volume', output=kwargs['output']))
        else:
            # read record from mongoDB
            refresh = False

    def attach(self, NAME=None, vm=None):
        con = openstack.connect(**self.config)
        server = con.get_server(vm)
        volume = con.list_volumes(NAME)[0]
        results = con.attach_volume(server, volume, device=None, wait=True, timeout=None)
        result = self.update_dict(results)
        return ''

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

    #
    # BUG NO DEFINITION OF WAHT UNSET IS. ARCHITECTURE DOCUMENT IS MISSING
    #
    def unset(self,
              name=None,
              property=None,
              image_property=None):
        """
        Separate a volume from a group of joined volumes

        :param name: name of volume to separate
        :param property: key to volume being separated
        :param image_property: image stored in separated volume
        :return: str
        """
        raise NotImplementedError

