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
          credentials:
            region: {region}
            EC2_SECURITY_GROUP: cloudmesh
            EC2_ACCESS_ID: {EC2_ACCESS_ID}
            EC2_SECRET_KEY: {EC2_SECRET_KEY}
            EC2_PRIVATE_KEY_FILE_PATH: 
            EC2_PRIVATE_KEY_FILE_NAME: 
    """

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "cm.region",
                      "AvailabilityZone",
                      "CreateTime",
                      "Encrypted",
                      "Size",
                      #"SnapshotId",
                      "State",
                      "VolumeId",
                      "Iops",
                      #"Tags",
                      "VolumeType",
#                      "created"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Region",
                       "AvailabilityZone",
                       "CreateTime",
                       "Encrypted",
                       "Size",
                       #"SnapshotId",
                       "State",
                       "VolumeId",
                       "Iops",
                       #"Tags",
                       "VolumeType",
#                       "Created"
                       ],
        }
    }

    def __init__(self, name=None):
        self.cloud = name
        self.ec2 = boto3.resource('ec2')

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
        elements.
        Libcloud
        returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used
        internally.

        :param results: the original dicts.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """

        if results is None:
            return None
        # elif type(elements) == list:
        #     _elements = elements
        # else:
        #     _elements = [elements]
        d = []

        elements = results['Volumes']
#        print(type(elements))
        for entry in elements:
#            print("entry['Tags']", entry['Tags'])
#            print(type(entry['Tags']))
            for item in entry['Tags']:
                if item['Key'] == 'Name':
                    volume_name = item['Value']
                else:
                    volume_name =" "
            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": volume_name,
                "region": entry["AvailabilityZone"], # for aws region = AvailabilityZone
                "vm name":
            })

#            entry["cm"]["created"] = str(DateTime.now())

            d.append(entry)
        return d

    def create(self, name=None, **kwargs):
        config = Config()
        default = config[f"cloudmesh.volume.{name}.default"]
        self._create(name=name, **default)

            #size: 2
            #iops: 1000
            #encrypted: False
            #multi_attach_enabled: True

    def _create(self,
               name=None,
               zone=None,
               size=2,
               volume_type="gp2",
               iops=1000,
               kms_key_id=None,
               outpost_arn=None,
               image=None,
               snapshot=None,
               encrypted=False,
               source=None,
               description=None,
               multi_attach_enabled=True,
               dryrun=False):
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
                               (from 100 to 64,000 for io1 type volume).
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

        banner(f"create volume {name}")
        result = self.ec2.create_volume(
            AvailabilityZone=zone,
            Encrypted=encrypted,
            Iops=iops,
            KmsKeyId=kms_key_id,
            OutpostArn=outpost_arn,
            Size=size,
            SnapshotId=snapshot,
            VolumeType=volume_type,
            DryRun=dryrun,
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': [
                        {
                            'Key': "volume",
                            'Value': description
                        },
                    ]
                },
            ],
            MultiAttachEnabled=multi_attach_enabled
        )
        result = [result]
        result = self.update_dict(result)

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
        if kwargs["--dryrun"]:
            dryrun = kwargs["--dryrun"]
        else: dryrun = False
        if kwargs["--refresh"]:
            refresh = kwargs["--refresh"]
            result = client.describe_volumes(
                DryRun=dryrun,
                Filters=[
                    {
                        'Name': {},
                        'Values': [
                            filter_value,
                        ]
                    },
                ],
            )
            banner("raw results")
            print(result)
            banner("raw results end")
 #       else:
            #read record from mongoDB
 #           refresh = False

        result = self.update_dict(result)

#        print(self.Print(result, kind='volume', output=kwargs['output']))

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
        return result

    def mount(self, volume_id, vm_id, device='dev/sdh', dryrun=False):
        """
        mounts volume

        :param volume_id (string): volume id
        :param vm_id (string): instance id
        :param device (string): The device name (for example, /dev/sdh or xvdh)
        :param dryrun (boolean): True|False
        :return: dict

        """
        banner(f"mount volume")
        volume = self.ec2.Volume(volume_id)
        result = volume.attach_to_instance(
            Device=device,
            InstanceId=vm_id,
            DryRun=dryrun
        )
        # This is wrong not updated
        return result

    def unmount(self,
                volume_id, vm_id,
                device='dev/sdh',
                force=False,
                dryrun=False):
        """
        unmounts volume
        :param volume_id (string): volume id
        :param device (string): The device name (for example, /dev/sdh or xvdh)
        :param force (boolean): True|False
        :param dryrun (boolean): True|False
        :return: dict

        banner(f"unmount volume")
        if cloud == 'aws':
            result = Shell.run((f"aws ec2 dettach-volumes --volume-id {volume_id})
            result = eval(result)['volume']
            return result
        """

        banner(f"unmount volume")
        volume = self.ec2.Volume(volume_id)
        result = volume.detach_from_instance(
            Device=device,
            Force=force,
            InstanceId=vm_id,
            DryRun=dryrun
        )
        # This is wrong not updated
        return result

    def delete(self, volume_id, dryrun=False):
        """
        delete volume

        :param volume_id (string): volume id
        :param dryrun (boolean): True|False
        :return: dict
        """

        banner(f"delete volume")
        volume = self.ec2.Volume(volume_id)
        result = volume.delete(
            DryRun=dryrun
        )
        # This is wrong not updated
        return result

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
