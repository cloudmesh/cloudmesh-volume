# Gregor will help us, can only do this after the abstract base class is defined
# Example can find under
#
# cloudmesh-cloud/cloudmesh/compute/*,
# cloudmesh-cloud/cloudmesh/vm/command,
# cloudmesh-storage/cloudmesh/storage/*

from abc import ABCMeta, abstractmethod
from cloudmesh.configuration.Config import Config

'''
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.provider import ComputeProviderPlugin


class Provider(VolumeABC, ComputeProviderPlugin):
    kind = 'google'

    def __init__(self, cloud, path):
        config = Config(config_path=path)["cloudmesh"]
        self.cm = config["cloud"][cloud]["cm"]
        self.default = config["cloud"][cloud]["default"]
        self.credentials = config["cloud"][cloud]["credentials"]
        self.group = config["default"]["group"]
        self.experiment = config["default"]["experiment"]

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