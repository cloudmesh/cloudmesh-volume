import os
import json

from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from datetime import datetime
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
import boto3
import boto

CLOUDMESH_YAML_PATH = "~/.cloudmesh/cloudmesh.yaml"

class Provider(VolumeABC):
    kind = "aws"

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
            service: compute
          default:
            volume_type: "gp2"
            size: 2
            iops: 1000
            encrypted: False
            multi_attach_enabled: True
            tag_key: "volume"
          credentials:
            region: {region}
            EC2_SECURITY_GROUP: cloudmesh
            EC2_ACCESS_ID: {EC2_ACCESS_ID}
            EC2_SECRET_KEY: {EC2_SECRET_KEY}
            EC2_PRIVATE_KEY_FILE_PATH: ~/.cloudmesh/aws_cert.pem
            EC2_PRIVATE_KEY_FILE_NAME: aws_cert
    """

    output = {

       "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "AvailabilityZone",
                      "CreateTime",
                      "Encrypted",
                      "Size",
                      "SnapshotId",
                      "State",
                      "VolumeId",
                      "Iops",
                      "Tags",
                      "VolumeType"],

            "header": ["Name",
                       "Cloud",
                       "AvailabilityZone",
                       "CreateTime",
                       "Encrypted",
                       "Size",
                       "SnapshotId",
                       "State",
                       "VolumeId",
                       "Iops",
                       "Tags",
                       "VolumeType"],
        }
    }

    def __init__(self,name):
        """
                Initializes the provider. The default parameters are read from the
                configuration file that is defined in yaml format.
                :param name: The name of the provider as defined in the yaml file
                :param configuration: The location of the yaml configuration file

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
        """
        self.cloud = name
        self.ec2 = boto3.resource('ec2')

    def update_dict(self, elements, kind=None):
        """
        converts the dict into a list

        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """

        if elements is None:
            return None

        d = []
        for key, entry in elements.items():

            entry['name'] = key

            if "cm" not in entry:
                entry['cm'] = {}

            # if kind == 'ip':
            #    entry['name'] = entry['floating_ip_address']

            entry["cm"].update({
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": key
            })

            if kind == 'vm':

                entry["cm"]["updated"] = str(DateTime.now())

                # if 'public_v4' in entry:
                #    entry['ip_public'] = entry['public_v4']

                # if "created_at" in entry:
                #    entry["cm"]["created"] = str(entry["created_at"])
                # del entry["created_at"]
                #    if 'status' in entry:
                #        entry["cm"]["status"] = str(entry["status"])
                # else:
                #    entry["cm"]["created"] = entry["modified"]

            elif kind == 'image':

                entry["cm"]["created"] = entry["updated"] = str(
                    DateTime.now())

            # elif kind == 'version':

            #    entry["cm"]["created"] = str(DateTime.now())

            d.append(entry)
        return d

    def create(self,
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
               tag_key="volume",
               #tag_value=None,
               multi_attach_enabled=True,
               dryrun=False):
        """
        Create a volume.

        :param name (string): name of volume
        :param zone (string): availability-zone
        :param encrypted (boolean): True|False
        :param size (integer): size of volume
        :param volume_type (string): type of volume. This can be gp2 for General Purpose SSD, io1 for Provisioned IOPS SSD,
                                st1 for Throughput Optimized HDD, sc1 for Cold HDD, or standard for Magnetic volumes.
        :param iops (integer): The number of I/O operations per second (IOPS) that the volume supports \
                                (from 100 to 64,000 for io1 type volume).
        :param kms_key_id (string): The identifier of the AWS Key Management Service (AWS KMS) customer master key (CMK)\
                                    to use for Amazon EBS encryption. If KmsKeyId is specified, the encrypted state \
                                    must be true.
        :param outpost_arn (string): The Amazon Resource Name (ARN) of the Outpost.
        :param image:
        :param snapshot (string): snapshot id
        :param source:
        :param description (string):
        :param tag_key (string): Tag keys are case-sensitive and accept a maximum of 127 Unicode characters.
                                        May not begin with aws.
        :param tag_value (string): Tag values are case-sensitive and accept a maximum of 255 Unicode characters.

        :param multi_attach_enabled (boolean):
        :return:

        """

        banner(f"create volume")
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
                            'Key': tag_key,
                            'Value': description
                        },
                    ]
                },
            ],
            MultiAttachEnabled= multi_attach_enabled
        )
        return result


    def list(self, filter_name, filter_value, volume_ids, dryrun):
        """
        Describes the specified EBS volumes or all of your EBS volumes.

        :param filter_name (string)
        :param filter_value (string)
        :param volume_ids (list): The volume IDs
        :return: dict

        """
        banner(f"list volume")

        client = boto.client('ec2')
        result = client.describe_volumes(
            Filters=[
                {
                    'Name': filter_name,
                    'Values': [
                        filter_value,
                    ]
                },
            ],
            VolumeIds=[
                volume_ids,
            ],
            DryRun=dryrun,
            MaxResults=123,
            NextToken='string'
        )

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
        if zone == None:
            availability_zone= self.ec2.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]['availability-zone']
        else:
            availability_zone = zone
        result = self.ec2.create_volume(SnapshotId=snapshot, AvailabilityZone = availability_zone, DryRun=dryrun)
        return result

    def mount(self, volume_id, vm_id, device='dev/sdh', dryrun=False):
        """
        mounts volume

        :param volume_id (string): volume id
        :param vm_id (string): instance id
        :param device (string): The device name (for example, /dev/sdh or xvdh )
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
        return result

    def unmount(self, volume_id, vm_id, device='dev/sdh', force=False, dryrun=False):
        """
        unmounts volume
        :param volume_id (string): volume id
        :param device (string): The device name (for example, /dev/sdh or xvdh )
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
        return result

    def set(self, volume_id, attribute=None, tag_key=None, tag_value=None, size=None, volume_type=None, iops=None,
            dryrun=False):

        """
            modify-volume-attribute: resume I/O access to the volume, or add or overwrite the specified tags, \
                                        or modify volume size, volume type, iops value

                :param volume_id <(string): volume id
                :param attribute (sting): can be "auto_enable_io", "tag"
                :param tag_key (string):Tag keys are case-sensitive and accept a maximum of 127 Unicode characters.
                                        May not begin with aws.
                :param tag_value (string): Tag values are case-sensitive and accept a maximum of 255 Unicode characters.
                :param size (integer): The target size of the volume, in GiB.
                :param volume_type (string): Type of volume. This can be 'gp2' for General Purpose SSD,
                                        'io1' for Provisioned IOPS SSD, 'st1' for Throughput Optimized HDD,
                                        'sc1' for Cold HDD, or 'standard' for Magnetic volumes.
                :param iops (integer): The number of I/O operations per second (IOPS) that the volume supports
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
                VolumeType=volume_type,
                Iops=iops
            )

        return result

    def unset(self, volume_id, attribute=None, dryrun=False):

        """
            modify-volume-attribute: suspend I/O access to the volume, or overwrite tag by an empty string

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

        elif attribute =="tag":
            result = volume.create_tags(
                DryRun=dryrun,
                Tags=[
                    {
                        'Key': " ",
                        'Value': " "
                    },
                ]
            )

        return result



if __name__ == "__main__":
    # region = 'us-east-2'
    p = Provider()
    p.create()
    p.list()
    p.mount()
    p.set()
    p.sync()
    p.unset()
    p.unmount()
    p.migrate()
    p.delete()

