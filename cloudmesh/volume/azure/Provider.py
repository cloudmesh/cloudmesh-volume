from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption
# from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.VolumeABC import VolumeABC
import json
import ast


# client = get_client_from_auth_file(ComputeManagementClient, auth_path=C:\Users\plj2861\Documents\AshleyPersonal\School\IndianaUniversity\CloudComputing\azure_credentials.json)


class Provider(VolumeABC):

    """The provider class is a category of objects, and in this case objects
    related to creating, deleting, and listing a volume, along with other
    volume related functions."""

    kind = "volume"

    sample = """
    cloudmesh:
      volume:
        azure:
          cm:
            active: true
            heading: Chameleon
            host: chameleoncloud.org
            label: chameleon
            kind: azure
            version: train
            service: compute
          credentials:
             AZURE_TENANT_ID: {tenantid}
             AZURE_SUBSCRIPTION_ID: {subscriptionid}
             AZURE_APPLICATION_ID: {applicationid}
             AZURE_SECRET_KEY: {secretkey}
             AZURE_REGION: eastus
          default:
            size: Basic_A0
            volume_type: __DEFAULT__

    """


    volume_states = [
        'ACTIVE',
        'BUILDING',
        'DELETED',
        'ERROR',
        'HARD_REBOOT',
        'PASSWORD',
        'PAUSED',
        'REBOOT',
        'REBUILD',
        'RESCUED',
        'RESIZED',
        'REVERT_RESIZE',
        'SHUTOFF',
        'SOFT_DELETED',
        'STOPPED',
        'SUSPENDED',
        'UNKNOWN',
        'VERIFY_RESIZE'
    ]

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "cm.location",
                      "cm.size",
                      "cm.group_name",
                      "id",
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Region",
                       "Size",
                       "Group_Name",
                       "Id",
                       ],
        }
    }
# need to update output

    def __init__(self, name="azure", configuration=None, credentials=None):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
        # configuration = configuration if configuration is not None \
            # else CLOUDMESH_YAML_PATH

        conf = Config(configuration)["cloudmesh"]

        self.user = Config()["cloudmesh"]["profile"]["user"]

        self.spec = conf["volume"][name]
        self.cloud = name
        self.location = 'eastus'
        self.size = 1
        self.group_name = 'cloudmesh'

        cred = self.spec["credentials"]
        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, configuration)

        # update credentials with the passed dict
        if credentials is not None:
            cred.update(credentials)

        VERBOSE(cred, verbose=10)

        if self.cloudtype != 'azure':
            Console.error("This class is meant for azure cloud")

        # ServicePrincipalCredentials related Variables to configure in
        # cloudmesh.yaml file

        # AZURE_APPLICATION_ID = '<Application ID from Azure Active Directory
        # App Registration Process>'

        # AZURE_SECRET_KEY = '<Secret Key from Application configured in
        # Azure>'

        # AZURE_TENANT_ID = '<Directory ID from Azure Active Directory
        # section>'

        credentials = ServicePrincipalCredentials(
            client_id=cred['AZURE_APPLICATION_ID'],
            #application and client id are same thing
            secret=cred['AZURE_SECRET_KEY'],
            tenant=cred['AZURE_TENANT_ID']
        )

        subscription = cred['AZURE_SUBSCRIPTION_ID']

        # Management Clients
        self.compute_client = ComputeManagementClient(
            credentials, subscription)


    def Print(self, data, kind=None, output="table"):
        """
        Print out the result dictionary as table(by default) or json.

        :param data: dic returned from volume functions
        :param kind: kind of provider
        :param output: "table" or "json"
        :return:
        """
        order = self.output["volume"]['order']
        header = self.output["volume"]['header']
        print(Printer.flatwrite(data,
                                sort_keys=["name"],
                                order=order,
                                header=header,
                                output=output,
                                )
              )


    def update_dict(self, results):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements. Libcloud returns an object or list of objects with the dict
        method. This object is converted to a dict. Typically this method is used
        internally.

        :param results: the original dicts.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """

        if results is None:
            return None

        d = []

        for entry in results:
            print("entry", entry)
            volume_name = entry['name']
            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": volume_name,
                "location": self.location,
                "size": self.size,
                "group_name": self.group_name,
            })
            d.append(entry)
        return d


    def create(self, **kwargs):
        """
        Create a volume.

           :param NAME (string): name of volume
           :param region (string): availability-zone
           :param size (integer): size of volume
           :param volume_type (string): type of volume.
           :param description (string)
           :return: dict
        """
        disk_creation = self.compute_client.disks.create_or_update(
            self.group_name,
            kwargs['NAME'],
            {
                'location': self.location,
                'disk_size_gb': self.size,
                'creation_data': {
                    'create_option': 'Empty'
                }
            }
        )
        # return after create
        results = disk_creation.result().as_dict()
        result = self.update_dict([results])
        return result


    def delete (self, name=None):
        """
        Delete volumes.
        If NAMES is not given, delete the most recent volume.

        :param NAMES: List of volume names
        :return:
        """
        disk_deletion = self.compute_client.disks.delete(
            self.group_name,
            name,
            {
                'location': self.location
            }
        )
        # return after deleting
        results = disk_deletion.result()
        result = self.update_dict(results)
        return result


    def list(self, **kwargs):
        """
        This command list all volumes as follows:

        If NAMES are given, search through all the active clouds and list all
        the volumes.
        If NAMES and cloud are given, list all volumes under the cloud.
        If cloud is given, list all the volumes under the cloud.
        If cloud is not given, list all the volumes under current cloud.
        If vm is given, under the current cloud, list all the volumes attaching
        to the vm.
        If region is given, under the current cloud, list all volumes in that
        region.

        :param NAMES: List of volume names
        :param vm: The name of the virtual machine
        :param region:  The name of the region
        :param cloud: The name of the cloud
        :param refresh: If refresh the information is taken from the cloud
        :return: dict
        """
        disk_list = \
            self.compute_client.disks.list_by_resource_group(self.group_name)
        # return disk_list
        found = []
        for disk in disk_list:
            results = disk.as_dict()
            result = self.update_dict([results])
            found.append(result)
        return found


    def attach(self, NAMES=None, vm=None):
        """
        This function attaches a given volume to a given instance

        :param NAMES: Names of Volumes
        :param vm: Instance name
        :return: Dictionary of volumes
        """
        # VM_NAME = 'ashthorn-vm-3'
        self.vms = self.compute_client.virtual_machines
        disk_creation = self.compute_client.disks.create_or_update(
            self.group_name,
            NAMES,
            {
                'location': self.location,
                'disk_size_gb': self.size,
                'creation_data': {
                    'create_option': 'Empty'
                }
            }
        )
        data_disk = disk_creation.result()
        virtual_machine = self.vms.get(self.group_name, vm)
        disk_attach = virtual_machine.storage_profile.data_disks.append({
            'lun': 0,
            'name': data_disk.name,
            'create_option': 'Attach',
            'managed_disk': {
                'id': data_disk.id
            }
        })
        updated_vm = self.vms.create_or_update(
            self.group_name,
            vm,
            virtual_machine
        )
        # return after attaching
        results = updated_vm.result().as_dict()
        result = self.update_dict([results])
        return result


    def detach(self, NAME=None, vm=None):
        """
        Detach volumes from vm.
        If success, the last volume will be saved as the most recent volume.

        :param NAMES: names of volumes to detach
        :return: dict
        """
        self.vms = self.compute_client.virtual_machines
        virtual_machine = self.vms.get(self.group_name, vm)
        data_disks = virtual_machine.storage_profile.data_disks
        data_disks[:] = [
            disk for disk in data_disks if disk.name != NAME]
        async_vm_update = self.compute_client.virtual_machines.create_or_update(
            self.group_name,
            vm,
            virtual_machine
        )
        # return after detaching
        results = async_vm_update.result().as_dict()
        result = self.update_dict([results])
        return result


    def status(self, NAME=None):
        """
        This function returns status of volume, such as "available", "in-use"
        and etc..

        :param NAME: name of volume
        :return: string
        """
        disk_status = self.compute_client.disks.get(
            self.group_name,
            NAME
        )
        # return after getting status
        results = disk_status.as_dict()
        res = dict((k, results[k]) for k in ['disk_state']
                   if k in results)
        return res


    def info(self, NAME=None):
        """
        Search through the list of volumes, find the matching volume with name,
        return the dict of matched volume

        :param name: volume name to match
        :return: dict
        """
        disk_status = self.compute_client.disks.get(
            self.group_name,
            NAME
        )
        # return after getting info
        results = disk_status.as_dict()
        result = self.update_dict([results])
        return result


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
        async_vm_update = self.compute_client.disks.create_or_update(
            self.group_name,
            kwargs['NAME'],
            {
                'location': self.location,
                'disk_size_gb': self.size,
                'creation_data': {
                    'create_option': 'Empty',
                },
                'tags': {
                    'volumeproject': 'test',
                    'tag2': 'test2'
                }
            }
        )
        async_vm_update.wait()
        # return after adding tags
        results = async_vm_update.result().as_dict()
        result = self.update_dict([results])
        return result


    def migrate(self,**kwargs):
        """
        Migrate volume from one vm to another vm.

        :param NAME (string): the volume name
        :param vm (string): the vm name
        :param region (string): the availability zone
        :return: dict
        """
        raise NotImplementedError


    def sync(self,NAMES):
        """
        synchronize one volume with another volume

        :param NAMES (list): list of volume names
        :return: dict
        """
        raise NotImplementedError
