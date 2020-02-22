from abc import ABCMeta, abstractmethod
from cloudmesh.configuration.Config import Config

'''
# noinspection PyUnusedLocal
class VolumeABC(metaclass=ABCMeta):

    def __init__(self, cloud, path):
        config = Config(config_path=path)["cloudmesh"]
        self.cm = config["cloud"][cloud]["cm"]
        self.default = config["cloud"][cloud]["default"]
        self.credentials = config["cloud"][cloud]["credentials"]
        self.group = config["default"]["group"]
        self.experiment = config["default"]["experiment"]

    @abstractmethod
    def create(self,
               name=None,
               size=None,
               voltype=None,
               image=None,
               snapshot=None,
               source=None,
               description=None):
        """
        Create a volume.

        TODO: describe all the parameters

        :param name:
        :param size:
        :param voltype:
        :param image:
        :param snapshot:
        :param source:
        :param description:
        :return:
        """
        raise NotImplementedError

    # TODO: add your methods
'''