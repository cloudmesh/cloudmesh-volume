from abc import ABCMeta, abstractmethod
from cloudmesh.configuration.Config import Config

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

    @abstractmethod
    def list(self,
             vm=None,
             region=None,
             cloud=None,
             refresh=False):
        """
        List of volume.
        
        :param vm: name of vm
        :param region: name of region
        :param cloud: name of cloud
        :param refresh: refresh
        :return: dict
        """
        raise NotImplementedError
     
    @abstractmethod   
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
    
    @abstractmethod
    def sync(self,
                vola=None,
                volb=None,
                region=None,
                cloud=None):
        """
        sync contents of one volume to another volume
        
        :param vola: name of volume A
        :param volb: name of volume B
        :param region: region where volumes will be stored
        :param cloud: the provider where volumes will be hosted
        :return: str
        """
        raise NotImplementedError
    
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
    
