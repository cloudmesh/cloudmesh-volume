from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.mongo.CmDatabase import CmDatabase


# class Provider(VolumeABC): # correct
class Provider(object):  # broken
    kind = "volume"

    @staticmethod
    def get_kind():
        """
        Get the kind of provider

        :return: string
        """
        kind = ["multipass",
                "aws",
                "azure",
                "google",
                "openstack",
                "oracle"]
        return kind

    @staticmethod
    def get_provider(kind):
        """
        Get the provider with specific provider (kind)

        :param kind:
        :return:
        """

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
        """
        Print out the result dictionary as table(by default) or json.

        :param data: dic returned from volume functions
        :param kind: kind of provider
        :param output: "table" or "json"
        :return:
        """

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
        """
        Create a volume.

           :param name (string): name of volume
           :param region (string): availability-zone
           :param size (integer): size of volume
           :param volume_type (string): type of volume.
           :param description (string)
           :return: dict
        """

        try:
            data = self.provider.create(**kwargs)
            variables = Variables()
            variables["volume"] = data[0]["cm"]["name"]
        except:
            raise ValueError("Volume could not be created")
        return data

    @DatabaseUpdate()
    def delete(self, name=None):
        """
        Delete volumes.
        If name is not given, delete the most recent volume.

        :param name: List of volume name
        :return:
        """
        d = self.provider.delete(name)
        return d

    @DatabaseUpdate()
    def list(self, **kwargs):
        """
        This command list all volumes as follows:

        If names are given, search through all the active clouds and list all
        the volumes. If names and cloud are given, list all volumes under the
        cloud. If cloud is given, list all the volumes under the cloud.
        If cloud is not given, list all the volumes under current cloud.
        If vm is given, under the current cloud, list all the volumes
        attaching to the vm. If region is given, under the current cloud,
        list all volumes in that region.

        :param names: List of volume names
        :param vm: The name of the virtual machine
        :param region:  The name of the region
        :param cloud: The name of the cloud
        :param refresh: If refresh the information is taken from the cloud
        :return: dict
        """
        data = self.provider.list(**kwargs)
        return data

    def info(self, name=None):
        """
        Search through the list of volumes, find the matching volume with name,
        return the dict of matched volume

        :param name: volume name to match
        :return: dict
        """
        volumes = self.provider.list()
        for volume in volumes:
            if volume["cm"]["name"] == name:
                return volume
        return None

    def search(self, name=None):
        """
        Calls info(self, name=None)

        :param name: volume name to match
        :return: dict
        """
        return self.info(name=name)

    @DatabaseUpdate()
    def status(self, name=None):
        """
        This function returns status of volume, such as "available", "in-use"
        and etc..

        :param name: name of volume
        :return: string
        """
        volume_status = self.provider.status(name)
        return volume_status

    @DatabaseUpdate()
    def attach(self, names=None, vm=None):
        """
        Attach volume to a vm.
        If names is not specified, attach the most recent volume to vm.

        :param name: volume name
        :param vm: vm name which the volume will be attached to
        :return: dict
        """
        result = self.provider.attach(names, vm)
        return result

    @DatabaseUpdate()
    def detach(self, name=None):
        """
        Detach volumes from vm.
        If success, the last volume will be saved as the most recent volume.

        :param names: names of volumes to detach
        :return: dict
        """
        try:
            result = self.provider.detach(name)
            variables = Variables()
            variables["volume"] = result["cm"]["name"]
        except:
            raise ValueError("Volume could not be detached")
        return result

    @DatabaseUpdate()
    def add_tag(self, **kwargs):
        """
        This function add tag to a volume.
        If name is not specified, then tag will be added to the last volume.
        If success, the volume will be saved as the most recent volume.

        :param name: name of volume
        :param kwargs:
                     key: name of tag
                     value: value of tag
        :return: self.list()
        """
        try:
            result = self.provider.add_tag(**kwargs)
            variables = Variables()
            variables["volume"] = result["cm"]["name"]
        except:
            raise ValueError("Tag could not be added")
        return result

    @DatabaseUpdate()
    def migrate(self, **kwargs):
        """
        Migrate volume from one vm to another vm.

        :param name (string): the volume name
        :param vm (string): the vm name
        :return: dict
        """
        try:
            result = self.provider.migrate(**kwargs)
        except:
            raise ValueError("Volume could not be migrate")
        return result

    @DatabaseUpdate()
    def sync(self, **kwargs):
        """
        synchronize one volume with another volume

        :param names (list): list of volume names
        :return: dict
        """
        #try:
        result = self.provider.sync(**kwargs)
        #except:
            #raise ValueError("Volume could not be synchronized")
        return result

    @DatabaseUpdate()
    def purge(self, **kwargs):
        """
        purge deleted volumes in MongoDB database

        :return: dict
        """
        collection = f"{self.cloud}-volume"
        self.cm = CmDatabase()
        if self.cloud == 'aws' or self.cloud == 'multipass':
            self.cm.collection(collection).delete_many({"State": "deleted"})
        elif self.cloud == 'oracle':
            self.cm.collection(collection).delete_many(
                {"lifecycle_state": "deleted"})
        elif self.cloud == 'azure':
            self.cm.collection(collection).delete_many(
                {"disk_state": "deleted"})
        elif self.cm.cloud == 'google' or self.cloud == 'openstack':
            self.cm.collection(collection).delete_many({"status": "deleted"})
        return self.provider.list()
