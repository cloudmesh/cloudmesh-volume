from time import sleep

import boto3
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.mongo.CmDatabase import CmDatabase
import datetime


class Provider(VolumeABC):
    kind = "volume"

    sample = """
    cloudmesh:
      cloud:
        aws:
          cm:
            active: true
            heading: AWS
            host: TBD
            label: VAWAS1
            kind: aws
            version: TBD
            service: volume
          default:
            volume_type: gp2
            size: 2
            iops: 1000
            encrypted: False
            region: us-east-2a
            multi_attach_enabled: True
            snapshot: "None"
          credentials:
            EC2_SECURITY_GROUP: default
            EC2_ACCESS_ID: XXXXX
            EC2_SECRET_KEY: XXXXX
            EC2_PRIVATE_KEY_FILE_PATH: ~/.ssh/id_rsa
            EC2_PRIVATE_KEY_FILE_NAME: key_name
    """

    volume_status = [
        'in-use',
        'available',
        'creating',
        'deleting'
    ]

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "cm.region",
                      # "AvailabilityZone",
                      # "CreateTime",
                      # "Encrypted",
                      "Size",
                      # "SnapshotId",
                      "State",
                      # "VolumeId",
                      # "Iops",
                      "cm.tags",
                      "VolumeType",
                      # "created",
                      "AttachedToVm",
                      # "UpdateTime"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Region",
                       # "AvailabilityZone",
                       # "Create Time",
                       # "Encrypted",
                       "Size(GB)",
                       # "SnapshotId",
                       "Status",
                       # "VolumeId",
                       # "Iops",
                       "Tags",
                       "Volume Type",
                       # "Created",
                       "Attached To Vm",
                       # "Update Time"
                       ],
        }
    }

    def __init__(self, name=None):
        """
        Initialize provider, create boto3 ec2 client, get the default dict.

        :param name: name of cloud
        """
        self.cloud = name
        config = Config()
        self.default = config[f"cloudmesh.volume.{self.cloud}.default"]
        self.cred = config[f'cloudmesh.volume.{self.cloud}.credentials']
        self.client = boto3.client('ec2',
                                   region_name=self.default['region_name'],
                                   aws_access_key_id=self.cred['EC2_ACCESS_ID'],
                                   aws_secret_access_key=self.cred[
                                       'EC2_SECRET_KEY']
                                   )
        self.cm = CmDatabase()

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
        #                 'AttachTime': datetime.datetime(2020, 3, 16, 20, 0,
        #                  35, tzinfo=tzutc()),
        #                  'Device': '/dev/sda1',
        #                  'InstanceId': 'i-0765529fec90ba56b',
        #                  'State': 'attached',
        #                  'VolumeId': 'vol-09db404935694e941',
        #                  'DeleteOnTermination': True
        #                  }
        #             ],
        #         'AvailabilityZone': 'us-east-2c',
        #         'CreateTime': datetime.datetime(2020, 3, 16, 20, 0, 35,
        #          257000, tzinfo=tzutc()),
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
            tags = ""
            try:
                tags = entry['Tags'].copy()
                for item in entry['Tags']:
                    if item['Key'] == 'Name':
                        if item['Value'] == "":
                            # Console.error(f"Please name volume
                            #       {entry['VolumeId']}")
                            volume_name = " "
                        elif item['Value'] == " ":
                            # Console.error(f"Please name volume
                            #       {entry['VolumeId']}")
                            volume_name = " "
                        else:
                            volume_name = item['Value']
                            tags.remove(item)
                    else:
                        # Console.error(f"Please name volume
                        #       {entry['VolumeId']}")
                        volume_name = " "
            except:
                # Console.error(f"Please name volume {entry['VolumeId']}")
                volume_name = " "

            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": volume_name,
                "region": entry["AvailabilityZone"],
                "tags": tags
            })

            d.append(entry)
        return d

    def vm_info(self, vm):
        """
        This function find vm info through given vm name.

        :param vm: the name of vm.
        :return: dict
        """

        vm_info = self.client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [vm, ]
                },
            ]
        )
        return vm_info

    def find_vm_info_from_volume_name(self, volume_name=None):
        """
        This function find vm info which the volume attached to through given
        volume name. Only implemented circumstance when a volume can only
        attach to one vm. (type iol volume could attach to multiple vms,
        not implemented)

        :param volume_name: the name of volume.
        :return: string
        """
        volume = self.client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [volume_name, ]
                },
            ],
        )

        # vms = []
        elements = volume['Volumes']
        for i in range(len(elements)):
            try:
                for item in elements[i]['Attachments']:
                    vm_id = item['InstanceId']
                    instance = client.describe_instances(InstanceIds=[vm_id])
                    for tag in instance['Reservations'][0]['Instances'][0][
                        'Tags']:
                        if tag['Key'] == 'Name':
                            vm_name = tag['Value']
                            # print("vm_name: ", vm_name)
                        return vm_name
            except:
                Console.error(f"{volume_name} does not attach to any vm")

    def update_AttachedToVm(self, data):
        """
        This function update returned volume dict with
        result['Volumes'][i]['AttachedToVm'] = vm_name. "i" chould be more than
        0 if volume could attach to multiple vm, but for now, one volume only
        attach to one vm.
        Only IOPS io1 volumes can attach to multiple vms (creating of io1 volume
        is not implemented)

        :param data: volume dict
        :return: dict
        """
        elements = data['Volumes']
        for i in range(len(elements)):
            elements[i]['AttachedToVm'] = []
            try:
                for item in elements[i]['Attachments']:
                    vm_id = item['InstanceId']
                    instance = self.client.describe_instances(
                        InstanceIds=[vm_id])
                    for tag in instance['Reservations'][0]['Instances'][0][
                        'Tags']:
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
        :return: string
        """
        volume = self.client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [volume_name, ]
                },
            ],
        )
        volume_id = volume['Volumes'][0]['VolumeId']
        return volume_id

    def find_vm_id(self, vm_name):
        """
        This function find vm_id through vm_name

        :param vm_name: the name of vom
        :return: string
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

    def status(self, name):
        """
        This function get volume status, such as "in-use", "available",
        "deleting"

        :param name
        :return: dict
        """
        result = self.client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [name, ]
                },
            ],
        )
        result = self.update_dict(result)
        # volume_status = volume['Volumes'][0]['State']
        return result

    def create(self, **kwargs):
        """
        This function create a new volume, with defalt parameters in
        self.default.
        default:
            {volume_type: gp2
            size: 2
            iops: 1000
            encrypted: False
            region: us-east-2a
            multi_attach_enabled: True
            snapshot: "None"}

        :param NAME (string): the name of volume
        :param size (int): the size of volume (GB)
        :param volume_type: volume type
        :param region (string): availability zone of volume
        :return: dict
        """

        for key in self.default.keys():
            if key not in kwargs.keys():
                kwargs[key] = self.default[key]
            elif kwargs[key] == None:
                kwargs[key] = self.default[key]

        result = self._create(**kwargs)
        result = self.update_dict(result)
        return result

    def _create(self,
                **kwargs):
        """
        Create a volume.

        :param name (string): name of volume
        :param region (string): availability-zone
        :param encrypted (boolean): True|False
        :param size (integer): size of volume
        :param volume_type (string): type of volume. This can be gp2 for General
                                     Purpose SSD, io1 for Provisioned IOPS SSD
                                     (not implemented), st1 for Throughput
                                     Optimized HDD, sc1 for Cold HDD,
                                     or standard for Magnetic volumes.
        :param snapshot (string): snapshot id
        :return: dict
        """

        if kwargs['volume_type'] == 'io1':
            raise NotImplementedError

        if kwargs['volume_type'] == 'sc1':
            if int(kwargs['size']) < 500:
                raise Exception("minimum volume size for sc1 is 500 GB")

        if kwargs['snapshot'] != "None":
            r = self.client.create_volume(
                AvailabilityZone=kwargs['region'],
                Encrypted=kwargs['encrypted'],
                Size=int(kwargs['size']),
                SnapshotId=kwargs['snapshot'],
                VolumeType=kwargs['volume_type'],
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
            )
        else:
            r = self.client.create_volume(
                AvailabilityZone=kwargs['region'],
                Encrypted=kwargs['encrypted'],
                Size=int(kwargs['size']),
                VolumeType=kwargs['volume_type'],
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
            )
        r = [r]
        result = {}
        result['Volumes'] = r
        result['Volumes'][0]['AttachedToVm'] = []
        return result

    def list(self,
             **kwargs
             ):

        """
        This function list all volumes as following:
        If NAME (volume name) is specified, it will print out info of NAME.
        If NAME (volume name) is not specified, it will print out info of all
          volumes under current cloud.
        If vm is specified, it will print out all the volumes attached to vm.
        If region(availability zone) is specified, it will print out
          all the volumes in that region.

        :param NAME: name of volume
        :param vm: name of vm
        :param region: name of availability zone
        :return: dict
        """
        if kwargs and kwargs['refresh'] == True:
            result = self.client.describe_volumes()
            for key in kwargs:
                if key == 'NAME' and kwargs['NAME']:
                    result = self.client.describe_volumes(
                        # DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'tag:Name',
                                'Values': [kwargs['NAME'], ]
                            },
                        ],
                    )

                elif key == 'NAMES' and kwargs['NAMES']:
                    if type(kwargs['NAMES']) == str:
                        kwargs['NAMES'] = [kwargs['NAMES']]
                    result = self.client.describe_volumes(
                        # DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'tag:Name',
                                'Values': kwargs['NAMES'],
                            },
                        ],
                    )
                elif key == 'vm' and kwargs['vm']:
                    vm_id = self.find_vm_id(kwargs['vm'])
                    result = self.client.describe_volumes(
                        # DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'attachment.instance-id',
                                'Values': [vm_id, ]
                            },
                        ],
                    )
                elif key == 'region' and kwargs['region']:
                    result = self.client.describe_volumes(
                        # DryRun=dryrun,
                        Filters=[
                            {
                                'Name': 'availability-zone',
                                'Values': [kwargs['region'], ]
                            },
                        ],
                    )
            result = self.update_AttachedToVm(result)
            result = self.update_dict(result)
        elif kwargs and kwargs['refresh'] == False:
            result = self.cm.find(cloud=self.cloud, kind='volume')
            for key in kwargs:
                if key == 'NAME' and kwargs['NAME']:
                    result = self.cm.find_name(name=kwargs['NAME'])
                elif key == 'NAMES' and kwargs['NAMES']:
                    result = self.cm.find_names(names=kwargs['NAMES'])
                elif key == 'vm' and kwargs['vm']:
                    result = self.cm.find(collection=f"{self.cloud}-volume",
                                          query={'AttachedToVm': kwargs['vm']})
                elif key == 'region' and kwargs['region']:
                    result = self.cm.find(collection=f"{self.cloud}-volume",
                                          query={'AvailabilityZone': kwargs[
                                              'region']})
        else:
            result = self.client.describe_volumes()
            result = self.update_AttachedToVm(result)
            result = self.update_dict(result)
        return result

    def delete(self, name):
        """
        This function delete one volume.
        It will return the info of volume with "state" updated as "deleted"
        and will show in Database.

        :param NAME (string): volume name
        :return: dict
        """

        result = self.client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [name]
                },
            ], )
        volume_id = self.find_volume_id(name)
        if result['Volumes'][0]['State'] == 'available':
            response = self.client.delete_volume(VolumeId=volume_id)
            stop_timeout = 360
            time = 0
            while time <= stop_timeout:
                sleep(5)
                time += 5
                try:
                    volume_status = self.status(name=name)[0]['State']
                except:
                    break
            result['Volumes'][0]['State'] = 'deleted'
        else:
            Console.error("volume is not available")
        result = self.update_dict(result)
        return result

    def attach(self,
               names,
               vm,
               dryrun=False):

        """
        This function attach one or more volumes to vm. It returns self.list()
        to list the updated volume. The updated dict with "AttachedToVm" showing
        the name of vm where the volume attached to.

        :param names (string): names of volumes
        :param vm (string): name of vm
        :param dryrun (boolean): True|False
        :return: list of dict
        """

        devices = [
            "/dev/sdb",
            "/dev/sdd",
            "/dev/sde",
            "/dev/sdf",
            "/dev/sdg",
            "/dev/sdh", ]

        vm_id = self.find_vm_id(vm)
        for name in names:
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

        return self.list(NAMES=names, refresh=True)

    def detach(self,
               name):

        """
        This function detach a volume from vm. It returns self.list() to list
        the updated volume. The vm under "AttachedToVm" will be removed if
        volume is successfully detached.

        :param name: name of volume to dettach
        :return: dict
        """

        volume_status = self.status(name=name)[0]['State']
        if volume_status == 'in-use':
            volume_id = self.find_volume_id(volume_name=name)
            rresponse = self.client.detach_volume(VolumeId=volume_id)
        stop_timeout = 360
        time = 0
        while time <= stop_timeout:
            sleep(5)
            time += 5
            volume_status = self.status(name=name)[0]['State']
            if volume_status == "available":
                break
        return self.list(NAME=name, refresh=True)[0]

    def add_tag(self, **kwargs):

        """
        This function add tag to a volume.
        In aws Boto3, key for volume name is "Name". For example,
           key="Name", value="user-volume-1".
        It could also be used to rename or name a volume.
        If NAME is not specified, then tag will be added to the last volume.

        :param NAME: name of volume
        :param key: name of tag
        :param value: value of tag
        :return: dict
        """
        key = kwargs['key']
        value = kwargs['value']
        volume_id = self.find_volume_id(volume_name=kwargs['NAME'])
        re = self.client.create_tags(
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
            result = self.list(NAME=value, refresh=True)[0]
        else:
            result = self.list(NAME=kwargs['NAME'], refresh=True)[0]
        return result

    def migrate(self, **kwargs):
        """
        Migrate volume from one vm to another vm.

        :param NAME (string): the volume name
        :param vm (string): the vm name
        :param region (string): the availability zone
        :return: dict
        """
        volume_name = kwargs['NAME']
        vm = kwargs['vm']
        volume_status = self.status(NAME=volume_name)[0]['State']
        volume_region = self.list(NAME=volume_name, refresh=True)[0]['cm'][
            'region']
        volume_id = self.find_volume_id(volume_name=volume_name)
        vm_info = self.vm_info(vm=vm)
        vm_status = vm_info['Reservations'][0]['Instances'][0]['State']['Name']
        vm_region = vm_info['Reservations'][0]['Instances'][0]['Placement'][
            'AvailabilityZone']
        vm_id = self.find_vm_id(vm_name=vm)

        # migrate within same region:
        if vm_status == 'running':
            if volume_region == vm_region:
                # if volume and vm are in the same zone,
                if volume_status == "in-use":
                    # if volume is attached to a vm, first detach and than
                    #       attach to vm
                    self.detach(name=volume_name)
                    self.attach(names=[volume_name, ], vm=vm)
                elif volume_status == "available":
                    # if volume is available, attach to vm
                    self.attach(names=[volume_name, ], vm=vm)
                return self.list(NAME=volume_name, refresh=True)
            else:
                # if volume and vm are not in the same zone, create a snapshot,
                #       create a new volume with the snapshot and in the
                #       same zone as vm, delete old volume

                snapshot_id = self.client.create_snapshot(
                    VolumeId=volume_id, )['SnapshotId']
                ec2 = boto3.resource('ec2')
                snapshot = ec2.Snapshot(snapshot_id)
                start_timeout = 360
                time = 0
                while time <= start_timeout:
                    sleep(5)
                    time += 5
                    if snapshot.state == "completed":
                        break
                kwargs['snapshot'] = snapshot_id
                kwargs['region'] = vm_region
                new_volume = self.create(name=volume_name, **kwargs)
                start_timeout = 360
                time = 0
                while time <= start_timeout:
                    sleep(5)
                    time += 5
                    status = self.status(name=volume_name)[0]['State']
                    if status == "available":
                        break
                self.attach(names=[volume_name, ], vm=vm)
                response = self.client.delete_volume(VolumeId=volume_id)

        else:
            Console.error("vm is not available")
        return self.list()

    def sync(self, names):
        """
        sync contents of one volume to another volume

        :param NAMES (list): list of volume names
        :return: dict
        """
        volume_1 = names[0]
        volume_1_region = self.list(NAME=volume_1, refresh=True)[0]['cm'][
            'region']
        volume_2 = names[1]
        volume_2_id = self.find_volume_id(volume_name=volume_2)
        # make a snapshot of volume_2
        snapshot_id = self.client.create_snapshot(
            VolumeId=volume_2_id, )['SnapshotId']
        ec2 = boto3.resource('ec2')
        snapshot = ec2.Snapshot(snapshot_id)
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            if snapshot.state == "completed":
                break
        # delete volume_1
        self.delete(name=volume_1)
        # create volume_1 with snapshot of volume_2
        kwargs = {}
        kwargs['region'] = volume_1_region
        kwargs['snapshot'] = snapshot_id
        kwargs['NAME'] = volume_1

        new_volume = self.create(**kwargs)
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            status = self.status(name=volume_1)[0]['State']
            if status == "available":
                break
        return self.list(NAME=volume_1, refresh=True)[0]
