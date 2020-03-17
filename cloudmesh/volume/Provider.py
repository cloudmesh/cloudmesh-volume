# Gregor will help us, can only do this after the abstract base class is defined
# Example can find under
#
# cloudmesh-cloud/cloudmesh/compute/*,
# cloudmesh-cloud/cloudmesh/vm/command,
# cloudmesh-storage/cloudmesh/storage/*
import os
import json

from cloudmesh.common.Printer import Printer
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.management.configuration.arguments import Arguments

# class Provider(VolumeABC): # correct
class Provider(object):  # broken
    # kind = "multipass"

    @staticmethod
    def get_kind():
        banner("get in def get_kind()")
        kind = ["multipass",
                "aws",
                "azure",
                "google",
                "openstack",
                "oracle"]
        return kind

    @staticmethod
    def get_provider(kind):
        banner("get in def get_provider(kind)")

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

        else:
            Console.error(f"Compute provider {kind} not supported")

            raise ValueError(f"Compute provider {kind} not supported")

        return P

        # noinspection PyPep8Naming

    def Print(self, data, output='table', kind=None):

        if kind is None and len(data) > 0:
            kind = data[0]["cm"]["kind"]

        if output == "table":

            order = self.provider.output[kind]['order']  # not pretty
            header = self.provider.output[kind]['header']  # not pretty

            if 'humanize' in self.provider.output[kind]:
                humanize = self.provider.output[kind]['humanize']
            else:
                humanize = None

            print(Printer.flatwrite(data,
                                    sort_keys=["name"],
                                    order=order,
                                    header=header,
                                    output=output,
                                    humanize=humanize)
                  )
        else:
            print(Printer.write(data, output=output))

    def __init__(self,
                 name=None,
                 configuration="~/.cloudmesh/cloudmesh.yaml"):
        try:
            banner("initializing")
            conf = Config(configuration)["cloudmesh"]
            self.spec = conf["volume"][name]
            self.cloud = name
    #        print('self.cloud = ', self.cloud)
            self.kind = self.spec["cm"]["kind"]
            super().__init__()

        except:
            Console.error(f"provider {name} not found in {configuration}")
            raise ValueError(f"provider {name} not found in {configuration}")

        P = None

        if self.kind in ["multipass",
                "aws",
                "azure",
                "google",
                "openstack",
                "oracle"]:

            P = Provider.get_provider(self.kind)

        if P is None:
            Console.error(f"provider {name} not supported")
            raise ValueError(f"provider {name} not supported")

        self.provider = P(self.cloud)

    @DatabaseUpdate()
    def create(self, **kwargs):
        d = self.provider.create(**kwargs)
        return d

    @DatabaseUpdate()
    def delete(self, name=None):
        d = self.provider.delete(name)
        return d

    @DatabaseUpdate()
    def list(self, **kwargs):
        banner('goes in def list(self, **kwargs):')
        data = self.provider.list(**kwargs)
        return data

    #
    # BUG: two different definitiosn of mount
    #
    # def mount(self, path=None, name=None):
    #    self.provider.mount(path, name)

    def mount(self, path=None, name=None, volume_id=None, vm_id=None):
        """
        mounts volume
        :param path: path of the mount
        :param name: the name of the instance
        :param volume_id: volume id
        :param vm_id: instance id
        :return: dict
        """
        raise NotImplementedError

    #
    # BUG NO GENERAL DEFINITIONS OF MIGRATE
    # BUG THE PARAMETER NAMES ARE REALY NOT GOOD
    #
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

    #
    # BUG NO GENERAL DEFINITION OF WHAT SYNC IS DOING
    # DEFINITION OF SYNC MAY BE WRONG
    # ARCHITECTURE DOCUMENT IS MISSING
    #
    def sync(self,
             volume_id=None,
             zone=None,
             cloud=None):
        """
        sync contents of one volume to another volume

        :param volume_id: id of volume A
        :param zone: zone where new volume will be created
        :param cloud: the provider where volumes will be hosted
        :return: str
        """
        raise NotImplementedError

    #
    # BUG NO DEFINITION OF WAHT UNSET IS. ARCHITECTURE DOCUMENT IS MISSING
    #
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
