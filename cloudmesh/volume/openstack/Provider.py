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
        {name}:
          cm:
            active: true
            heading: {name}
            host: TBD
            label: {name}
            kind: openstack
            version: TBD
            service: volume
          credentials:
            auth:
              username: $USER
            key_path: ~/.ssh/id_rsa.pub
          default:
            size: m1.medium
            image: lts
    """

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "availability_zone",
                      "created_at",
                      "size",
                      "id",
                      "volume_type"

                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "availability_zone",
                       "created_at",
                       "size",
                       "id",
                       "volume_type"
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

    def credentials(self):
        config = Config()["cloudmesh.volume.openstack.credentials"]
        return config

    def create(self, **kwargs):
        config = self.credentials()
        con = openstack.connect(**config)
        arguments = dotdict(kwargs)
        con.create_volume(name=arguments.name,size=arguments.size,volume_type=arguments.voltype)

    def delete(self, name=None):
        config = self.credentials()
        con = openstack.connect(**config)
        con.delete_volume(name_or_id=name)
        
    def list(self,**kwargs):
        config = self.credentials()
        if kwargs["--refresh"]:
            con = openstack.connect(**config)
            results = con.list_volumes()
            result = self.update_dict(results)
            print(self.Print(result, kind='volume', output=kwargs['output']))
        else:
            # read record from mongoDB
            refresh = False

    def mount(self,path=None,name=None):
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

