from abc import ABCMeta, abstractmethod

from cloudmesh.configuration.Config import Config


class VolumeABC(metaclass=ABCMeta):

    def __init__(self, cloud, path):
        """
        Initialize self.cm, self.default, self.credentials, self.group, self.experiment

        :param cloud: name of provider
        :param path: "~/.cloudmesh/cloudmesh.yaml"
        """

        try:
            config = Config(config_path=path)["cloudmesh"]
            self.cm = config["cloud"][cloud]["cm"]
            self.default = config["cloud"][cloud]["default"]
            self.credentials = config["cloud"][cloud]["credentials"]
            self.group = config["default"]["group"]
            self.experiment = config["default"]["experiment"]

        except Exception as e:
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
        This command list all volumes as follows:

        If NAMES are given, search through all the active clouds and list all the volumes.
        If NAMES and cloud are given, list all volumes under the cloud.
        If cloud is given, list all the volumes under the cloud.
        If cloud is not given, list all the volumes under current cloud.
        If vm is given, under the current cloud, list all the volumes attaching to the vm.
        If region is given, under the current cloud, list all volumes in that region.

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
        """
        Create a volume.

           :param NAME (string): name of volume
           :param region (string): availability-zone
           :param size (integer): size of volume
           :param volume_type (string): type of volume.
           :param description (string)
           :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, NAMES=None):
        """
        Delete volumes.
        If NAMES is not given, delete the most recent volume.

        :param NAMES: List of volume names
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def attach(self, NAME=None, vm=None):
        """
        Attatch volume to a vm.
        If NAMES is not specified, attach the most recent volume to vm.

        :param NAME: volume name
        :param vm: vm name which the volume will be attached to
        :return: dict
        """

        raise NotImplementedError

    @abstractmethod
    def detach(self,NAMES=None):
        """
        Dettach volumes from vm.
        If success, the last volume will be saved as the most recent volume.

        :param NAMES: names of volumes to dettach
        :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def add_tag(self,**kwargs):
        """
        This function add tag to a volume.
        If NAME is not specified, then tag will be added to the last volume.
        If success, the volume will be saved as the most recent volume.

        :param NAME: name of volume
        :param kwargs:
                    key: name of tag
                    value: value of tag
        :return: self.list()
        """
        raise NotImplementedError

    @abstractmethod
    def status(self, NAME=None):
        """
        This function returns status of volume, such as "available", "in-use" and etc..

        :param NAME: name of volume
        :return: string
        """
        raise NotImplementedError

    @abstractmethod
    def migrate(self,**kwargs):
        """
        Migrate volume from one vm to another vm.

        :param name: name of volume
        :param from_vm: name of vm where volume will be moved from
        :param to_vm: name of vm where volume will be moved to
        :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self,NAMES):
        """
        synchronize one volume with another volume

        :param NAMES (list): list of volume names
        :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def purge(self,**kwargs):
        """
        purge all the deleted volume in MongoDB database

        :return: dict
        """
        raise NotImplementedError