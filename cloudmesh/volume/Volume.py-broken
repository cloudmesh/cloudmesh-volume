# Gregor will help us, can only do this after the abstract base class is defined
# Example can find under
#
# cloudmesh-cloud/cloudmesh/compute/*,
# cloudmesh-cloud/cloudmesh/vm/command,
# cloudmesh-storage/cloudmesh/storage/*
import os
import json

from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config

class Provider(VolumeABC):
    #kind = "multipass"

    @staticmethod
    def get_kind():
        kind = ["multipass",
                "aws",
                "azure",
                "google",
                "openstack",
                "oracle"]
        return kind

    @staticmethod
    def get_provider(kind):

        if kind == "multipass":
            from cloudmesh.volume.multipass.Provider import Provider as P

        elif kind == "aws":
            from cloudmesh.volume.aws.Provider import Provider as P

        elif kind == "azure":
            from cloudmesh.volume.azure.Provider import Provider as P

        elif kind == "google":
            from cloudmesh.volume.google.Provider import Provider as P

        elif kind == "openstack":
            from cloudmesh.volume.openstack.Provider import Provider as P

        elif kind == "oracle":
            from cloudmesh.volume.oracle.Provider import Provider as P

        return P


    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh.yaml"):
        conf = Config(configuration)["cloudmesh"]
        self.spec = conf["volume"][name]
        self.cloud = name
        self.kind = self.spec["cm"]["kind"]
        super().__init__(name, conf)

        P = Provider.get_provider(self.kind)
        self.provider = P(self.cloud)

    def create(self, **kwargs):  #, **args):
        #banner(f"mount {name}")
        # #os.system(f"multipass mount /Users/ashok/multipass-mount  {name}")

        self.provider.create(**kwargs)
        """
        name = args["name"]
        def create(self,
                   name=None,
                   zone=None,
                   size=None,
                   voltype="gp2",
                   iops=1000,
                   kms_key_id=None,
                   outpost_arn=None,
                   image=None,
                   snapshot=None,
                   encrypted=False,
                   source=None,
                   description=None,
                   tag_key=None,
                   tag_value=None,
                   multi_attach_enabled=True,
                   dryrun=False):
        """
        
    def delete(self,name=None):
        self.provider.delete(name)

    def mount(self, path=None,name=None):
        self.provider.mount(path,name)

    # @DatabaseUpdate
    # def list(self, name=None):
    #    #(...)
    #    # list of dicts
