from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict

import ctypes
import os
import subprocess
from datetime import datetime
from pprint import pprint
from sys import platform

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2018_12_01.models import SecurityRule
from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.abstract.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING, banner
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.provider import ComputeProviderPlugin
from msrestazure.azure_exceptions import CloudError




# from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient

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
             AZURE_REGION: westus
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
                      "availability_zone",
                      "created_at",
                      "size",
                      "status",
                      "id",
                      "volume_type"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Availability Zone",
                       "Created At",
                       "Size",
                       "Status",
                       "Id",
                       "Volume Type"
                       ],
        }
    }


    def __init__(self, name="azure", configuration=None, credentials=None):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
        configuration = configuration if configuration is not None \
            else CLOUDMESH_YAML_PATH

        conf = Config(configuration)["cloudmesh"]

        self.user = Config()["cloudmesh"]["profile"]["user"]

        self.spec = conf["cloud"][name]
        self.cloud = name

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


    def Print(self, data, output=None, kind=None):
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
            })
            d.append(entry)
        return d


    # def _get_resource_group(self):
    #     groups = self.resource_client.resource_groups
    #     if groups.check_existence(self.GROUP_NAME):
    #         return groups.get(self.GROUP_NAME)
    #     else:
    #         # Create or Update Resource groupCreating new public IP
    #         Console.info('Creating Azure Resource Group')
    #         res = groups.create_or_update(self.GROUP_NAME,
    #                                       {'location': self.LOCATION})
    #         Console.info('Azure Resource Group created: ' + res.name)
    #         return res
    #
    #
    # # Azure Resource Group
    # self.GROUP_NAME = self.default["resource_group"]


    def create(self, **kwargs):
        GROUP_NAME = 'cloudmesh'
        # self.vms = self.compute_client.virtual_machines
        LOCATION = 'eastus'
        disk_creation = self.compute_client.disks.create_or_update(
            GROUP_NAME,
            "cloudmesh-os-disk",
            {
                'location': LOCATION,
                'disk_size_gb': 1,
                'creation_data': {
                    'create_option': 'Empty'
                }
            }
        )
        # print list after create
        results = disk_creation.result().as_dict()
        result = self.update_dict([results])
        return result


    def delete (self, NAMES=None):
        GROUP_NAME = 'cloudmesh'
        LOCATION = 'eastus'
        disk_deletion = self.compute_client.disks.delete(
            GROUP_NAME,
            "cloudmesh-os-disk",
            {
                'location': LOCATION
            }
        )
        # print list after deleting
        results = disk_deletion.result()
        result = self.update_dict(results)
        return result


    def list(self,
             NAMES=None,
             vm=None,
             region=None,
             cloud=None,
             refresh=None,
             dryrun=None):
        disk_list = self.compute_client.disks.list()
        return disk_list


    def attach(self, NAME=None, vm=None):
        LOCATION = 'eastus'
        GROUP_NAME = 'cloudmesh'
        VM_NAME = 'ashthorn-vm-3'
        disk_creation = self.compute_client.disks.create_or_update(
            GROUP_NAME,
            "test",
            {
                'location': LOCATION,
                'disk_size_gb': 1,
                'creation_data': {
                    'create_option': 'Empty'
                }
            }
        )
        data_disk = disk_creation.result()
        self.vms = self.compute_client.virtual_machines
        virtual_machine = self.vms.get(GROUP_NAME, VM_NAME)
        disk_attach = virtual_machine.storage_profile.data_disks.append({
            'lun': 0,
            'name': data_disk.name,
            'create_option': 'Attach',
            'managed_disk': {
                'id': data_disk.id
            }
        })
        updated_vm = self.vms.create_or_update(
            GROUP_NAME,
            VM_NAME,
            virtual_machine
        )
        results = updated_vm.result().as_dict()
        result = self.update_dict([results])
        return result



#might need to access azure compute provider vm name
#create vm first then attach disk to new vm
#if vm unavailable, give an error
#if missing (Such as delete), give an error

    def detach(self,
              NAME=None):
        print("update me")


    def add_tag(self,**kwargs):
        print("update me")


    def migrate(self,
                name=None,
                from_vm=None,
                to_vm=None):
        print("update me")


    def sync(self,
             from_volume=None,
             to_volume=None):
        print("update me")


    def status(self, NAME=None):
        print("update me")


#every cloud needs a function called search (per Xin) such as describe or
# list volume