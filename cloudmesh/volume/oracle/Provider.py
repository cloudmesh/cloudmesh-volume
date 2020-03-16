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
                      "availability_domain",
                      "time_created",
                      "size_in_gbs",
                      "id"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "availability_domain",
                       "time_created",
                       "size_in_gbs",
                       "id"
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
            id = entry.__getattribute__("id")

            entry = {
                "availability_domain": availability_domain,
                "time_created": time_created,
                "size_in_gbs": size_in_gbs,
                "id": id
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

    def credentials(self):
        config = Config()
        credential =  config["cloudmesh.volume.oracle.credentials"]
        return credential

    def create(self, **kwargs):
        raise NotImplementedError

    def delete(self, name=None):
        raise NotImplementedError

    def list(self, **kwargs):
        if kwargs["--refresh"]:
            credentials = self.credentials()
            block_storage = oci.core.BlockstorageClient(credentials)
            v = block_storage.list_volumes(credentials['compartment_id'])
            results = v.data
            result = self.update_dict(results)
            print(self.Print(result, kind='volume', output=kwargs['output']))
        else:
            # read record from mongoDB
            refresh = False

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

