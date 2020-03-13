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
import datatime

class Provider(VolumeABC):
    #kind = "multipass"


    def __init__(self,
                 name=None,
                 configuration="~/.cloudmesh/cloudmesh.yaml"):
        try:
            super().__init__(name, configuration)
            self.kind = Config(configuration)[f"cloudmesh.cloud.{name}.cm.kind"]
            self.credentials = Config(configuration)[
                f"cloudmesh.cloud.{name}.credentials"]
            self.name = name
        except:
            Console.error(f"provider {name} not found in {configuration}")
            raise ValueError(f"provider {name} not found in {configuration}")

        provider = None

        providers = ProviderList()

        if self.kind in ['openstack']:
            from cloudmesh.openstack.compute.Provider import \
                Provider as OpenStackComputeProvider
            provider = OpenStackComputeProvider

        elif self.kind in ['google']:
            from cloudmesh.google.compute.Provider import \
                Provider as GoogleComputeProvider
            provider = GoogleComputeProvider

        elif self.kind in ['azure']:
            from cloudmesh.azure.compute.Provider import \
                Provider as AzureComputeProvider
            provider = AzureComputeProvider

        elif self.kind in ['aws']:
            from cloudmesh.aws.compute.Provider import \
                Provider as AWSComputeProvider
            provider = AWSComputeProvider

        if provider is None:
            Console.error(f"provider {name} not supported")
            raise ValueError(f"provider {name} not supported")

        self.p = provider(name=name, configuration=configuration)

    @DatabaseUpdate()
    def list(self, **kwargs):
        return self.p.list(**kwargs)

    def create(self, name=None):
        banner(f"mount {name}")
        os.system(f"multipass mount /Users/ashok/multipass-mount  {name}")

    def mount(self, path=None,name=None):
        self.provider.mount(path,name)

    # @DatabaseUpdate
    # def list(self, name=None):
    #    #(...)
    #    # list of dicts