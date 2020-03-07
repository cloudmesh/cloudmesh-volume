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

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh.yaml"):
        conf = Config(configuration)["cloudmesh"]
        # self.user = conf["profile"]
        #self.spec = conf["cloud"][name]
        self.cloud = name
        #cred = self.spec["credentials"]
        #deft = self.spec["default"]
        #self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, conf)
        print(self.cloud)
        #print(self.cloudtype)
        if self.cloud == "multipass":
            from cloudmesh.volume.multipass.Provider import \
                Provider as MulitpassProvider
            self.provider = MulitpassProvider(self.cloud)

    def create(self, name=None):
        banner(f"mount {name}")
        os.system(f"multipass mount /Users/ashok/multipass-mount  {name}")

    def mount(self, path=None,name=None):
        self.provider.mount(path,name)



