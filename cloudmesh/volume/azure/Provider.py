import ctypes
import os
import subprocess
from datetime import datetime
from pprint import pprint
from sys import platform

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2018_12_01.models import SecurityRule
from azure.mgmt.resource import ResourceManagementClient
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING, banner
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.provider import ComputeProviderPlugin
from msrestazure.azure_exceptions import CloudError

CLOUDMESH_YAML_PATH = "~/.cloudmesh/cloudmesh.yaml"

class Provider(VolumeABC):

    kind = 'volume'

    sample = """
        cloudmesh:
          cloud:
            {name}:
              cm:
                active: true
                heading: {name}
                host: TBD
                label: {name}
                kind: azure
                version: latest
                service: compute
              default:
                size: Basic_A0
                resource_group: cloudmesh
                storage_account: cmdrive
                network: cmnetwork
                subnet: cmsubnet
                blob_container: vhds
                AZURE_VM_IP_CONFIG: cloudmesh-ip-config
                AZURE_VM_NIC: cloudmesh-nic
                AZURE_VM_DISK_NAME: cloudmesh-os-disk
                AZURE_VM_USER: TBD
                AZURE_VM_PASSWORD: TBD
                AZURE_VM_NAME: cloudmeshVM
              credentials:
                AZURE_TENANT_ID: {tenantid}
                AZURE_SUBSCRIPTION_ID: {subscriptionid}
                AZURE_APPLICATION_ID: {applicationid}
                AZURE_SECRET_KEY: {secretkey}
                AZURE_REGION: eastus
        """

    volume_state = [

    ]

    output = {
        }


    credentials = ServicePrincipalCredentials(
        client_id=cred['AZURE_APPLICATION_ID'],
        secret=cred['AZURE_SECRET_KEY'],
        tenant=cred['AZURE_TENANT_ID']
    )

    subscription = cred['AZURE_SUBSCRIPTION_ID']

    # Management Clients
    self.resource_client = ResourceManagementClient(
        credentials, subscription)
    self.compute_client = ComputeManagementClient(
        credentials, subscription)
    self.network_client = NetworkManagementClient(
        credentials, subscription)

    # VMs abbreviation
    self.vms = self.compute_client.virtual_machines
    self.imgs = self.compute_client.virtual_machine_images

    # Azure Resource Group
    self.GROUP_NAME = self.default["resource_group"]

    # Azure Datacenter Region
    self.LOCATION = cred["AZURE_REGION"]

    # NetworkManagementClient related Variables
    self.VNET_NAME = self.default["network"]
    self.SUBNET_NAME = self.default["subnet"]
    self.IP_CONFIG_NAME = self.default["AZURE_VM_IP_CONFIG"]

    # Azure VM Storage details
    self.OS_DISK_NAME = self.default["AZURE_VM_DISK_NAME"]
    self.USERNAME = self.default["AZURE_VM_USER"]
    self.PASSWORD = self.default["AZURE_VM_PASSWORD"]
    self.VM_NAME = self.default["AZURE_VM_NAME"]
    self.NIC_NAME = self.default["AZURE_VM_NIC"]

    # public IPs
    self.PUBLIC_IP__NAME = self.VM_NAME + '-pub-ip'

    # Create or Update Resource group
    self._get_resource_group()

    self.cmDatabase = CmDatabase()

    self.protocol_str_map = {
        'tcp': 'Tcp',
        'udp': 'Udp',
        'icmp': 'Icmp',
        'esp': 'Esp',
        'ah': 'Ah',
        '*': '*'
    }

    def update_dict(self, results):
        if results is None:
            return None
        # elif type(elements) == list:
        #     _elements = elements
        # else:
        #     _elements = [elements]
        d = []

        elements = results['Volumes']
        # print(type(elements))
        for entry in elements:
            # print("entry", entry)
            # print(type(entry))
            try:
                for item in entry['Tags']:
                    if item['Key'] == 'Name':
                        volume_name = item['Value']
                    else:
                        volume_name = " "
            except:
                pass
            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": volume_name,
                "region": entry["AvailabilityZone"],  # for aws region = AvailabilityZone
                "vms": None
            })

            #            entry["cm"]["created"] = str(DateTime.now())

            d.append(entry)
        return d

        def create(self, name=None, **kwargs):  # name is volume name
            cloud = kwargs['cloud']
            config = Config()
            default = config[f"cloudmesh.volume.{cloud}.default"]
            # banner(f"print default {default}")
            # banner(f"print kwargs {kwargs}")
            for key in default.keys():
                if key not in kwargs.keys():
                    kwargs[key] = default[key]
                elif kwargs[key] == None:
                    kwargs[key] = default[key]

            # default.update(kwargs)
            # banner(f"print kwargs after update {kwargs}")
            result = self._create(name=name, **kwargs)

            # size: 2
            # iops: 1000
            # encrypted: False
            # multi_attach_enabled: True
            result = self.update_dict(result)
            return result

        def _create(self,
                    **kwargs):
            """
            Create a volume.

            :param name (string): name of volume
            :param zone (string): availability-zone
            :param encrypted (boolean): True|False
            :param size (integer): size of volume

            :param volume_type (string): type of volume. This can be gp2 for General
                                         Purpose SSD, io1 for Provisioned IOPS SSD,
                                        st1 for Throughput Optimized HDD, sc1 for
                                        Cold HDD, or standard for Magnetic volumes.
            :param iops (integer): The number of I/O operations per second (IOPS)
                                   that the volume supports
                                   (from 100 to 64,000 for io1 type volume). If iops
                                   is specified, the volume_type must be io1.
            :param kms_key_id (string): The identifier of the AWS Key Management
                                        Service (AWS KMS) customer master key (CMK)
                                        to use for Amazon EBS encryption. If
                                        KmsKeyId is specified, the encrypted state
                                        must be true.
            :param outpost_arn (string): The Amazon Resource Name (ARN) of the Outpost.
            :param image:
            :param snapshot (string): snapshot id
            :param source:
            :param description (string):
            :param tag_key (string): Tag keys are case-sensitive and accept a
                                     maximum of 127 Unicode characters.
                                     May not begin with aws.
            :param tag_value (string): Tag values are case-sensitive and accept a
                                       maximum of 255 Unicode characters.
            :param multi_attach_enabled (boolean):
            :return:

            """

            # banner(f"create volume {kwargs}")
            client = boto3.client('ec2')

            if kwargs['volume_type'] == 'io1':
                raise NotImplementedError

            r = client.create_volume(
                AvailabilityZone=kwargs['region'],
                Encrypted=kwargs['encrypted'],
                # Iops=kwargs['iops'],
                # KmsKeyId=None,
                # OutpostArn=None,
                Size=kwargs['size'],
                # SnapshotId=None,
                VolumeType=kwargs['volume_type'],
                DryRun=kwargs['dryrun'],
                TagSpecifications=[
                    {
                        'ResourceType': 'volume',
                        'Tags': [
                            {
                                'Key': "Name",
                                'Value': kwargs['NAME']
                            },
                        ]
                    },
                ],
                # MultiAttachEnabled=kwargs['multi_attach_enabled']
            )
            r = [r]
            result = {}
            result['Volumes'] = r

            # banner("raw results")
            # print(result)
            # banner("raw results end")

            return result

        # PROPOSAL 2
        def list(self,
                 **kwargs
                 ):

            """
            THis command list all volumes as follows

            If vm is defined, all vloumes of teh vm are returned.
            If region is defined all volumes of the vms in that region are returned.
            ....

            #The filter allows us to specify cloud specific filter option
            #a filter for this cloud looks like ....????

            :param dryrun:
            :param refresh:
            :return:
            """

            # dont    filter_name=None,
            # dont    filter_value=None,
            #     dryrun=False):

            #:param filter_name (string)
            #:param filter_value (string)
            #:param volume_ids (list): The volume IDs

            # filter = "[[
            #                 {
            #                     'Name': 'xyz',
            #                     'Values': [
            #                         'abc',
            #                     ]
            #                 },
            #             ]"

            # filter = eval(filter)

            #        banner('print kwargs')
            #        print(kwargs)
            #        print(kwargs['output'])

            client = boto3.client('ec2')
            dryrun = kwargs['--dryrun']
            #        region = kwargs['--region']
            #        vm = kwargs['--vm']# will need vm id from mongo records
            result = client.describe_volumes(
                DryRun=dryrun,
                # Filters=[
                #     {
                #         'Name': {},
                #         'Values': [
                #             filter_value,
                #         ]
                #     },
                # ],
            )
            banner("raw results")
            print(result)
            banner("raw results end")
            result = self.update_dict(result)

            #        print(self.Print(result, kind='volume', output=kwargs['output']))

            return result