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
from cloudmesh.common.console import Console
from cloudmesh.common.variables import Variables

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

    def Print(self, data, kind=None, output="table"):

        if kind is None and len(data) > 0:
            kind = data[0]["cm"]["kind"]

        if output == "table":

            order = self.provider.output[kind]['order']
            header = self.provider.output[kind]['header']

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
            conf = Config(configuration)["cloudmesh"]
            self.spec = conf["volume"][name]
            self.cloud = name
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
        try:
            data = self.provider.create(**kwargs)
            variables = Variables()
            variables["volume"] = data["cm"]["name"]
        except:
            raise ValueError("Volume could not be created")
        return data

    @DatabaseUpdate()
    def delete(self, name=None):
        d = self.provider.delete(name)
        return d

    @DatabaseUpdate()
    def list(self, **kwargs):
        data = self.provider.list(**kwargs)
        return data

    def info(self, name=None):
        volumes = self.provider.list()
        for volume in volumes:
            if volume["cm"]["name"] == name:
                return volume
        return None

    def search(self, name=None):
        return self.info(name=name)

    @DatabaseUpdate()
    def attach(self, NAMES=None, vm=None):

        """
        Attatch volume to a vm

        :param NAME: volume name
        :param vm: vm name which the volume will be attached to
        :return: dict
        """
        result = self.provider.attach(NAMES, vm)
        return result

    @DatabaseUpdate()
    def detach(self, NAME=None):

        """
        Detach a volume from vm

        :param NAME: name of volume to detach
        :return: dict
        """
        result = self.provider.detach(NAME)
        return result

    @DatabaseUpdate()
    def add_tag(self, **kwargs):

        """
        Add tag for a volume. For example: key="Name", value="user-volume-1".

        :param NAME: name of volume
        :param key: tag key
        :param value: tag value
        :return: dict
        """
        try:
            result = self.provider.add_tag(**kwargs)
            variables = Variables()
            variables["volume"] = result["cm"]["name"]
        except:
            raise ValueError("Tag could not be added")
        return result


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


