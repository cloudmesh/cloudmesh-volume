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
#             NAMES=[],
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
        :return:
        """
        raise NotImplementedError

    #
    # BUG ARCHOTECTURE DOCUMENT MISSING. EG what is create in each provider
    #
    @abstractmethod
    def create(self, name=None, **kwargs):
        """
        Create a volume.
        """

        raise NotImplementedError

    @abstractmethod
    def delete(self, name=None):
        """
        Delete volume
        :param name:
        :return:
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

    #
    # BUG NO PROPER DEFINITION OF WAHT UNSET IS.
    # ARCHITECTURE DOCUMENT IS MISSING
    #
    @abstractmethod
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

    #
    # BUG NO PROPER DEFINITION OF WHAT A MONUT IS. ARCHOTECTURE DOCUMENT MISSING
    #
    #
    # BUG: two different definitiosn of mount IN DIFFERENT PROVIDERS
    #
    # def mount(self, path=None, name=None):
    #    self.provider.mount(path, name)
    #
    # path will be in yaml
    #
    @abstractmethod
    def mount(self, volume=None, vm=None):
        """
        mounts volume
        :param name: the name of the volume
        :param volume: volume id
        :return: dict
        """
        raise NotImplementedError
