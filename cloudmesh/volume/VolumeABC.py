from abc import ABCMeta, abstractmethod

from cloudmesh.configuration.Config import Config


class VolumeABC(metaclass=ABCMeta):

    def __init__(self, cloud, path):
        # noinspection SpellCheckingInspection
        """
                Initialize self.cm, self.default, self.credentials, self.group,
                self.experiment

                :param cloud: name of provider
                :param path: "~/.cloudmesh/cloudmesh.yaml"
                """

        try:
            # noinspection SpellCheckingInspection
            config = Config(config_path=path)["cloudmesh"]
            self.cm = config["cloud"][cloud]["cm"]
            self.default = config["cloud"][cloud]["default"]
            self.credentials = config["cloud"][cloud]["credentials"]
            self.group = config["default"]["group"]
            self.experiment = config["default"]["experiment"]

        except Exception as e:
            print(e)

    @abstractmethod
    def list(self):
        """
        This command list all volumes as follows:

        If NAMES are given, search through all the active clouds and list all
        the volumes. If NAMES and cloud are given, list all volumes under the
        cloud. If cloud is given, list all the volumes under the cloud.
        If cloud is not given, list all the volumes under current cloud.
        If vm is given, under the current cloud, list all the volumes attaching
        to the vm. If region is given, under the current cloud, list all
        volumes in that region.

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
    def create(self, **kwargs):
        """
        Create a volume.
        For multipass, creates a directory, volume region means path of the directory, i.e.
            "/Users/username/multipass"
        For aws, creates EBS volume in EC2 service, volume region means availability zone.
        For azure, creates disk, volume region means location.
        For google, creates zonal disks, volume region means zone of volume.
        For oracle, creates volume in block-storage service, volume region means availability_domain.
        For openstack, creates volume, volume region means zone.

        :param NAME (string): name of volume
        :param region (string): region
        :param size (integer): size of volume
        :param volume_type (string): type of volume.
        :param description (string)
        :return: dict of the created volume
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, names=None):
        """
        Delete volumes.
        If volume names are not given, delete the most recent volume.

        :param NAMES: List of volume names
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def attach(self, name=None, vm=None):
        """
        Attach volume to a vm.
        If volume names are not specified, attach the most recent volume to vm.

        :param NAME: volume name
        :param vm: vm name which the volume will be attached to
        :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def detach(self, names=None):
        """
        Detach volumes from vm.
        If success, the last volume will be saved as the most recent volume.

        :param NAMES: names of volumes to detach
        :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def add_tag(self, **kwargs):
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
    def status(self, name=None):
        """
        This function returns status of volume, such as "available", "in-use"
        and etc.

        :param NAME: name of volume
        :return: string
        """
        raise NotImplementedError

    @abstractmethod
    def migrate(self, **kwargs):
        """
        This function migrate volume from one vm to another vm in the same cloud service.

        :param NAME (string): the volume name
        :param vm (string): the vm name
        :param region (string): region
        :return: dict
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self, **kwargs):
        """
        This function synchronize one volume with another volume in the same cloud service.

        :param NAMES (list): list of volume names
        :return: dict
        """
        raise NotImplementedError

    def purge(self, **kwargs):
        """
        This function purge all the deleted volume in MongoDB database

        :return:
        """
        raise NotImplementedError
