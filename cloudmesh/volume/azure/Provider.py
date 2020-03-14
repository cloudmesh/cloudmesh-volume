from abc import ABCMeta, abstractmethod
from cloudmesh.configuration.Config import Config


class VolumeABC(metaclass=ABCMeta):

    # def __init__(self, cloud):
    #    raise NotImplementedError

    def __init__(self, cloud, path):
        try:
            config = Config(config_path=path)["cloudmesh"]
            self.cm = config["cloud"][cloud]["cm"]
            self.default = config["cloud"][cloud]["default"]
            self.credentials = config["cloud"][cloud]["credentials"]
            self.group = config["default"]["group"]
            self.experiment = config["default"]["experiment"]

        except Exception as e:
            # raise ValueError(f"storage service {service} not specified")
            print(e)

    def list(self,
             vm=None,
             region=None,
             cloud=None,
             filter=None,
             dryrun=None,
             refresh=False):
        """
        This command list all volumes as follows

        If vm is defined, all vloumes of teh vm are returned.
        If region is defined all volumes of the vms in that region are returned.
        ....

        The filter allows us to specify cloud specific filter option
        a filter for this cloud looks like ....????

        :param vm:
        :param region:
        :param cloud:
        :param filter:
        :param refresh:
        :return:
        """
        raise NotImplementedError

    def create(self, name=None, **kwargs):
        """
        Create a volume.

        TODO: describe all the parameters

        :param name:
        :param zone: name of availability-zone
        :param size:
        :param voltype:
        :param iops: The number of I/O operations per second (IOPS) that the volume supports (from 100 to 64,000 for\
         io1 type volume).
        :param image:
        :param snapshot:
        :param source:
        :param description:
        :return:
        """
        raise NotImplementedError

    def delete(self, name=None):
        """
        Delete volume
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

    def mount(self, path=None, name=None, volume_id=None, vm_id=None):
        """
        mounts volume
        :param path: path of the mount
        :param name: the name of the instance
        :param volume_id: volume id
        :param vm_id: instance id
        :return: dict
        """
        raise NotImplementedError
