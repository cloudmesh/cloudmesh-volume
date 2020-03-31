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

    @abstractmethod
    def list(self,
             NAMES=None,
             vm=None,
             region=None,
             cloud=None,
             refresh=None,
             dryrun=None):
        """
        This command list all volumes as follows

        If vm is defined, all vloumes of teh vm are returned.
        If region is defined all volumes of the vms in that region are returned.
        ....

        The filter allows us to specify cloud specific filter option
        a filter for this cloud looks like ....????

        :param NAMES: List of volume names
        :param vm: The name of the virtual machine
        :param region:  The name of the region
        :param cloud: The name of the cloud
        :param refresh: If refresh the information is taken from the cloud
        :return: dict
        """
        raise NotImplementedError

    #
    # BUG ARCHOTECTURE DOCUMENT MISSING. EG what is create in each provider
    #
    @abstractmethod
    def create(self, NAME=None, **kwargs):
    # def create(self,
    #            NAME=None,
    #            size=None,
    #            volume_type=None,
    #            description=None,
    #            dryrun=None
    #            ):
        """
        Create a volume.
        :param NAME: Volume name
        :return: dict
        """

        raise NotImplementedError

    @abstractmethod
    def delete(self, NAMES=None):
        """
        Delete volume
        :param NAMES: List of volume names
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def attach(self, NAME=None, vm=None):

        """
        attatch volume to a vm

        :param NAME: volume name
        :param vm: vm name which the volume will be attached to
        :return: dict
        """

        raise NotImplementedError

    @abstractmethod
    def detach(self,
              NAMES=None):

        """
        Dettach a volume from vm

        :param NAMES: names of volumes to dettach
        :return: str
        """
        raise NotImplementedError

    @abstractmethod
    def migrate(self,
                name=None,
                from_vm=None,
                to_vm=None):

        """
        Migrate volume from one vm to another vm.

        :param name: name of volume
        :param from_vm: name of vm where volume will be moved from
        :param to_vm: name of vm where volume will be moved to
        :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self,
             from_volume=None,
             to_volume=None):
        """
        Sync contents of one volume to another volume. It is  a copy of all
        changed content from one volume to the other.

        :param from_volume: name of the from volume
        :param to_volume: name of the to volume

        :return: str
        """
        raise NotImplementedError