import os
import json

from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from datetime import datetime
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
import boto3
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from time import sleep
from cloudmesh.common.parameter import Parameter

import collections

class Provider(VolumeABC):
    kind = "volume"

    sample = """
    cloudmesh:
      cloud:
        {name}:
          cm:
            active: true
            heading: AWS
            host: TBD
            label: {name}
            kind: aws
            version: TBD
            service: volume
          default:
            volume_type: "gp2"
            size: 2
            iops: 1000
            encrypted: False
            multi_attach_enabled: True
            region: 'us-east-2'
          credentials:
            EC2_SECURITY_GROUP: cloudmesh
            EC2_ACCESS_ID: {EC2_ACCESS_ID}
            EC2_SECRET_KEY: {EC2_SECRET_KEY}
            EC2_PRIVATE_KEY_FILE_PATH: 
            EC2_PRIVATE_KEY_FILE_NAME: 
    """

    volume_states = [
        'in-use',
        'available',
    ]

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "cm.region",
                      #"AvailabilityZone",
                      "CreateTime",
                      "Encrypted",
                      "Size",
                      #"SnapshotId",
                      "State",
                      #"VolumeId",
                      "Iops",
                      #"Tags",
                      "VolumeType",
                      #"created",
                      "AttachedToVm"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Region",
                       #"AvailabilityZone",
                       "CreateTime",
                       "Encrypted",
                       "Size",
                       #"SnapshotId",
                       "State",
                        #"VolumeId",
                       "Iops",
                       #"Tags",
                       "VolumeType",
                       #"Created",
                       "AttachedToVm"
                       ],
        }
    }

    def __init__(self, name=None):
        self.cloud = name
        self.client = boto3.client('ec2')

    def update_dict(self, results):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements. For aws, we make region = AvailabilityZone.

        :param results: the original dicts.
        :param kind: for volume special attributes are added. This includes
                     cloud, kind, name, region.
        :return: The list with the modified dicts
        """

        # {'Volumes':
        #     [
        #         {
        #         'Attachments':
        #             [
        #                 {
        #                 'AttachTime': datetime.datetime(2020, 3, 16, 20, 0, 35, tzinfo=tzutc()),
        #                  'Device': '/dev/sda1',
        #                  'InstanceId': 'i-0765529fec90ba56b',
        #                  'State': 'attached',
        #                  'VolumeId': 'vol-09db404935694e941',
        #                  'DeleteOnTermination': True
        #                  }
        #             ],
        #         'AvailabilityZone': 'us-east-2c',
        #         'CreateTime': datetime.datetime(2020, 3, 16, 20, 0, 35, 257000, tzinfo=tzutc()),
        #         'Encrypted': False,
        #         'Size': 8,
        #         'SnapshotId': 'snap-085c8383cc8833286',
        #         'State': 'in-use',
        #         'VolumeId': 'vol-09db404935694e941',
        #         'Iops': 100,
        #         'Tags':
        #             [{'Key': 'Name',
        #               'Value': 'xin-vol-3'}],
        #         'VolumeType': 'gp2'
        #         },
        #         {...}
        #     ]
        # }


        if results is None:
            return None

        d = []

        elements = results['Volumes']
        for entry in elements:
            try:
                for item in entry['Tags']:
                    if item['Key'] == 'Name':
                        if item['Value'] == "":
                            Console.error(f"Please name volume {entry['VolumeId']}")
                            volume_name = " "
                        elif item['Value'] == " ":
                            Console.error(f"Please name volume {entry['VolumeId']}")
                            volume_name = " "
                        else:
                            volume_name = item['Value']
                    else:
                        Console.error(f"Please name volume {entry['VolumeId']}")
                        volume_name = " "
            except:
                Console.error(f"Please name volume {entry['VolumeId']}")
                volume_name = " "

            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": volume_name,
                "region": entry["AvailabilityZone"],
            })

            d.append(entry)
        return d

    def find_vm_name(self, volume_name=None):
        """
            This function find attached vm_name from given volume_name. only implemented circumstance when a volume
            can only
            attach to one vm. (type iol volume could attach to multiple vms, not implemented)

            :param volume_name: the name of volume.
            :return: vm_name: the name of vm
        """
        volume = self.client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [volume_name, ]
                },
            ],
        )

        #vms = []
        elements = volume['Volumes']
        for i in range(len(elements)):
            try:
                for item in elements[i]['Attachments']:
                    vm_id = item['InstanceId']
                    instance = client.describe_instances(InstanceIds=[vm_id])
                    for tag in instance['Reservations'][0]['Instances'][0]['Tags']:
                        print(tag)
                        if tag['Key'] == 'Name':
                            vm_name = tag['Value']
                            print("vm_name: ", vm_name)
                        return vm_name
            except:
                Console.error(f"{volume_name} does not attach to any vm")

    def update_AttachedToVm(self, data):
        """
            This function update returned volume dict with result['Volumes'][i]['AttachedToVm'] = vm_name. "i" chould
            be more than 0 if volume could attach to multiple vm, but for now, one volume only attach to one vm.

            :param data: returned volume dict
            :return: data: updated volume dict
        """
        elements = data['Volumes']
        for i in range(len(elements)):
            elements[i]['AttachedToVm'] = []
            try:
                for item in elements[i]['Attachments']:
                    vm_id = item['InstanceId']
                    instance = self.client.describe_instances(InstanceIds=[vm_id])
                    for tag in instance['Reservations'][0]['Instances'][0]['Tags']:
                        if tag['Key'] == 'Name':
                            vm_name = tag['Value']
                            elements[i]['AttachedToVm'].append(vm_name)
            except:
                pass
        return data

    def find_volume_id(self, volume_name):
        """
            This function find volume_id through volume_name

            :param volume_name: the name of volume
            :return: volume_id
        """
        volume = self.client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [volume_name,]
                },
            ],
        )
        volume_id = volume['Volumes'][0]['VolumeId']
        return volume_id

    def find_vm_id(self, vm_name):
        """
            This function find vm_id through vm_name

            :param vm_name: the name of vom
            :return: vm_id
        """
        instance = self.client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [vm_name, ]
                },
            ],
        )
        vm_id = instance['Reservations'][0]['Instances'][0]['InstanceId']
        return vm_id

    def wait(self,
             time=None):
        """
            This function waiting for volume to be updated

            :param time: time to wait in seconds
            :return: False
        """
        Console.info("waiting for volume to be updated")
        sleep(time)
        return False

    def get_volume_state(self, volume_name):
        """
            This function get volume state, such as "in-use", "available"

            :param volume_name
            :return: volume_state
        """
        volume = self.client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [volume_name, ]
                },
            ],
        )
        volume_state = volume['Volumes'][0]['State']
        return volume_state


    def create(self, name=None, **kwargs):
        """
            This function create a new volume, with defalt parameters in cloudmesh.volume.{cloud}.default.

            :param name: the name of volume
            :return: volume dict
        """
        cloud = kwargs['cloud']
        config = Config()
        default = config[f"cloudmesh.volume.{cloud}.default"]
        for key in default.keys():
            if key not in kwargs.keys():
                kwargs[key] = default[key]
            elif kwargs[key] == None:
                kwargs[key] = default[key]

        #default.update(kwargs)
        #banner(f"print kwargs after update {kwargs}")
        result = self._create(name=name, **kwargs)

            #size: 2
            #iops: 1000
            #encrypted: False
            #multi_attach_enabled: True
        result = self.update_dict(result)
        return result[0]

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
        :param iops (integer): NOT IMPLEMENTED. The number of I/O operations per second (IOPS)
                               that the volume supports
                               (from 100 to 64,000 for io1 type volume). If iops
                               is specified, the volume_type must be io1.
        :param kms_key_id (string): NOT IMPLEMENTED. The identifier of the AWS Key Management
                                    Service (AWS KMS) customer master key (CMK)
                                    to use for Amazon EBS encryption. If
                                    KmsKeyId is specified, the encrypted state
                                    must be true.
        :param outpost_arn (string): The Amazon Resource Name (ARN) of the Outpost.
        :param snapshot (string): snapshot id
        :param source:
        :param description (string):
        :param tag_key (string): Tag keys are case-sensitive and accept a
                                 maximum of 127 Unicode characters.
                                 May not begin with aws.
        :param tag_value (string): Tag values are case-sensitive and accept a
                                   maximum of 255 Unicode characters.
        :param multi_attach_enabled (boolean): True by default
        :return: volume dict

        """

        if kwargs['volume_type']=='io1':

            raise NotImplementedError

        if kwargs['volume_type']=='sc1':
            if int(kwargs['size']) < 500:
                raise Exception("minimum volume size for sc1 is 500 GB")


        r = self.client.create_volume(
            AvailabilityZone=kwargs['region'],
            Encrypted=kwargs['encrypted'],
            #Iops=kwargs['iops'],
            #KmsKeyId=None,
            #OutpostArn=None,
            Size=int(kwargs['size']),
            #SnapshotId=None,
            VolumeType=kwargs['volume_type'],
            #DryRun=kwargs['dryrun'],
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
            #MultiAttachEnabled=kwargs['multi_attach_enabled']
        )
        r = [r]
        result = {}
        result['Volumes']= r
        result['Volumes'][0]['AttachedToVm'] = []

        return result


    def list(self,
             **kwargs
             ):

        """
        This function list all volumes as following:
        If NAME (volume_name) is specified, it will print out info of NAME
        If NAME (volume_name) is not specified, it will print out info of all volumes
        If vm is specified, it will print out all the volumes attached to vm
        If region(availability zone) is specified, it will print out all the volumes in that region

        :param NAME: name of volume
        :param vm: name of vm
        :param region: name of availability zone
        :return:
        """

        # if len(kwargs)==0:
        #     dryrun = False
        # else:
        #     dryrun = kwargs['--dryrun']
        if kwargs:
            result = self.client.describe_volumes()
            for key in kwargs:
                if key == 'NAME' and kwargs['NAME']:
                    result = self.client.describe_volumes(
                        #DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'tag:Name',
                                'Values': [kwargs['NAME'],]
                            },
                        ],
                    )

                elif key=='NAMES' and kwargs['NAMES']:
                    if type(kwargs['NAMES'])== str:
                        kwargs['NAMES'] = [kwargs['NAMES']]
                    result = self.client.describe_volumes(
                        #DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'tag:Name',
                                'Values': kwargs['NAMES'],
                            },
                        ],
                    )
                elif key =='vm' and kwargs['vm']:
                    vm_id =  self.find_vm_id(kwargs['vm'])
                    result = self.client.describe_volumes(
                        #DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'attachment.instance-id',
                                'Values': [vm_id,]
                            },
                        ],
                    )
                elif key =='region' and kwargs['region']:
                    result = self.client.describe_volumes(
                        #DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'availability-zone',
                                'Values': [kwargs['region'],]
                            },
                        ],
                    )

        else:
            result = self.client.describe_volumes()

        result = self.update_AttachedToVm(result)
        result = self.update_dict(result)
        return result

    def delete(self, NAME):
        """
        This function delete one volume. It will call self.list() to return a dict of all the volumes under the cloud.

        :param NAME (string): volume name
        :return: self.list()
        """

        banner(f"delete volume {NAME}")
        volume_id = self.find_volume_id(NAME)
        response = self.client.delete_volume(VolumeId=volume_id)
        return self.list()

    def attach(self,
               NAMES,
               vm,
               device=None,
               dryrun=False):

        """
        This function attach one or more volumes to vm. It returns self.list() to list the updated volume.
        The updated dict with
        "AttachedToVm" showing the name of vm where the volume attached to

        :param NAMES (string): names of volumes
        :param vm (string): name of vm
        :param device (string): The device name which is the attaching point to vm
        :param dryrun (boolean): True|False
        :return: self.list()
        """

        devices = [
                  "/dev/sdb",
                  "/dev/sdd",
                  "/dev/sde",
                  "/dev/sdf",
                  "/dev/sdg",
                  "/dev/sdh",]

        vm_id = self.find_vm_id(vm)
        for name in NAMES:
            volume_id = self.find_volume_id(name)
            for device in devices:
                try:
                    response = self.client.attach_volume(
                                        Device=device,
                                        InstanceId=vm_id,
                                        VolumeId=volume_id,
                                        DryRun=dryrun
                                    )
                except:
                    pass
        return self.list(NAMES=NAMES)

    def detach(self,
                NAME):

        """
        This function detach a volume from vm. It returns self.list() to list the updated volume. The vm under "AttachedToVm" will be
        removed if volume is successfully detached.

        :param NAME: name of volume to dettach
        :return: self.list()
        """

        volume_state = self.get_volume_state(volume_name=NAME)
        if volume_state == 'in-use':
            volume_id = self.find_volume_id(volume_name=NAME)
            rresponse = self.client.detach_volume(VolumeId=volume_id)
            self.wait(10)
        return self.list(NAME=NAME)[0]

    def add_tag(self, NAME, **kwargs):

        """
        This function add tag to a volume.
        In aws Boto3, key for volume name is "Name". For example, key="Name", value="user-volume-1".
        It could also be used to rename or name a volume.
        If NAME is not specified, then tag will be added to the last volume.

        :param NAME: name of volume
        :param kwargs:
                    key: name of tag
                    value: value of tag
        :return: self.list(NAME)
        """

        key = kwargs['key']
        value = kwargs['value']

        volume_id = self.find_volume_id(volume_name=NAME)
        result = self.client.create_tags(
            Resources=[
                volume_id,
            ],
            Tags=[
                {
                    'Key': key,
                    'Value': value
                },
            ],
        )
        if key == 'Name':
            result = self.list(NAME=value)[0]
        else:
            result = self.list(NAME=NAME)[0]
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

    def sync(self,
             volume_id,
             zone=None,
             cloud=None,
             dryrun=False
             ):
        """
        sync contents of one volume to another volume

        :param volume_id (string): list of id of volume
        :param zone (string): zone where new volume will be created
        :param cloud (string): the provider where volumes will be hosted
        :return: dict

        """
        banner(f"sync volume")
        volume = self.ec2.Volume(volume_id)
        snapshot = volume.create_snapshot()
        if zone is None:
            availability_zone = self.ec2.describe_volumes(
                VolumeIds=[volume_id])['Volumes'][0]['availability-zone']
        else:
            availability_zone = zone
        result = self.ec2.create_volume(SnapshotId=snapshot,
                                        AvailabilityZone=availability_zone,
                                        DryRun=dryrun)
        # This is wrong not updated
        raise NotImplementedError




    def set(self,
            volume_id,
            attribute=None,
            tag_key=None,
            tag_value=None,
            size=None,
            voltype=None,
            iops=None,
            dryrun=False):

        """
            modify-volume-attribute: resume I/O access to the volume, or add or
                                     overwrite the specified tags, \
                                     or modify volume size, volume type, iops value

            :param volume_id <(string): volume id
            :param attribute (sting): can be "auto_enable_io", "tag"
            :param tag_key (string): Tag keys are case-sensitive and accept a
                                     maximum of 127 Unicode characters.
                                     May not begin with aws.
            :param tag_value (string): Tag values are case-sensitive and accept
                                       a maximum of 255 Unicode characters.
            :param size (integer): The target size of the volume, in GiB.
            :param voltype (string): Type of volume. This can be 'gp2' for
                                     General Purpose SSD,
                                    'io1' for Provisioned IOPS SSD, 'st1'
                                    for Throughput Optimized HDD,
                                    'sc1' for Cold HDD, or 'standard' for
                                    Magnetic volumes.
            :param iops (integer): The number of I/O operations per second
                                   (IOPS) that the volume supports
                                   (from 100 to 64,000 for io1 type volume).
            :param dryrun (boolean): True | False
        """

        volume = self.ec2.Volume(volume_id)
        if attribute == "auto_enable_io":
            result = volume.modify_attribute(
                AutoEnableIO={
                    'Value': True
                },
                DryRun=dryrun
            )

        elif attribute == "tag":
            result = volume.create_tags(
                DryRun=dryrun,
                Tags=[
                    {
                        'Key': tag_key,
                        'Value': tag_value
                    },
                ]
            )

        else:
            result = volume.modify_volume(
                DryRun=dryrun,
                VolumeId=volume_id,
                Size=size,
                VolumeType=volume_type, # BUG
                Iops=iops
            )

        # This is wrong not updated
        return result

    def unset(self, volume_id, attribute=None, dryrun=False):

        """
        modify-volume-attribute: suspend I/O access to the volume, or
        overwrite tag by an empty string

        :param volume_id (string): volume id
        :param attribute (sting): "no_auto_enable_io" | "tag"
        :param dryrun (boolean): True | False
        """

        volume = self.ec2.Volume(volume_id)
        if attribute == "no_auto_enable_io":
            result = volume.modify_attribute(
                AutoEnableIO={
                    'Value': False
                },
                DryRun=dryrun
            )

        elif attribute == "tag":
            result = volume.create_tags(
                DryRun=dryrun,
                Tags=[
                    {
                        'Key': " ",
                        'Value': " "
                    },
                ]
            )
        # This is wrong not updated
        return result


if __name__ == "__main__":
    # region = 'us-east-2'
    p = Provider()

    p.list()
