import os
import json

from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config

class Provider(VolumeABC):
    kind = "aws"

    sample = """
    cloudmesh:
      volume:
        {name}:
          cm:
            active: true
            heading: {name}
            host: TBD
            label: {name}
            kind: aws
            version: TBD
            service: volume
          credentials:
            auth:
              username: $USER
            key_path: ~/.ssh/id_rsa.pub
          default:
            size: m1.medium
            image: lts
    """

    vm_state = [
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
        self.cloud = name

    def create(self,
               name=None,
               zone=None,
               size=None,
               voltype=gp2,
               iops=1000,
               image=None,
               snapshot=None,
               encrypted=False,
               source=None,
               description=None):
        """
        Create a volume.

        :param name: name of volume
        :param zone: name of availability-zone
        :param size: size of volume
        :param voltype: type of volume
        :param iops: The number of I/O operations per second (IOPS) that the volume supports (from 100 to 64,000 for\
         io1 type volume).
        :param image:
        :param snapshot: snapshot id
        :param source:
        :param description: 'ResourceType=volume,Tags=[{Key=purpose,Value=production},{Key=cost-center,Value=cc123}]'
        :return:

        """

        banner(f"create volume")
        if zone == False:
            raise Exception('Must specify zone')
        else:
            if voltype == "io1":
                if iops ==False:
                    raise Exception('Please specify --iops')
                else:
                    result = Shell.run(
                        f"aws ec2 create-volume --availability-zone {zone} --volume-type {voltype} --iops {iops}/"
                        f" --size {size} --snapshot-id {snapshot} --encrypted {encrypted} --tag-specifications {description}")
            else:
                result = Shell.run(
                    f"aws ec2 create-volume --availability-zone {zone} --volume-type {voltype} --iops {iops}/"
                    f" --size {size} --snapshot-id {snapshot} --encrypted {encrypted} --tag-specifications {description}")
        result = eval(result)['volume']
        return result


    def list(self,
             vm=None,
             vm_id=None,
             region=None,
             zone=None,
             cloud=None,
             refresh=False):
        """
        List of volume.

        :param vm: name of vm
        :param vm_id: vm id
        :param region: name of region
        :param zone: name of availability-zone
        :param cloud: name of cloud
        :param refresh: refresh
        :return: dict
        """
        banner(f"list volume")

        if cloud == 'aws':
            result = Shell.run(f"aws ec2 describe-volumes --region {region}/"
                           f" --filters Name=attachment.instance-id,Values={vm_id} Name=availability-zone,Values={zone}")
            result = eval(result)['volume']
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
             zone,
             cloud=None):
        """
        sync contents of one volume to another volume

        :param volume_id: id of volume A
        :param zone: zone where new volume will be created
        :param cloud: the provider where volumes will be hosted
        :return: str
        """
        banner(f"sync volume")
        if cloud == 'aws':
            snapshot = Shell.run(f"aws ec2 create-snapshot --volume-id {volume_id}")
            snapshot_id = snapshot["SnapshotId"]
            result = p.create(zone=zone, size=None, voltype = 'gp2', iops=1000, snapshot=snapshot_id, encrypted=False)
            result = eval(result)['volume']
            return result

    def mount(self, volume_id, vm_id):
        """
        mounts volume
        :param volume_id: volume id
        :param vm_id: instance id
        :return: dict
        """
        banner(f"mount volume")
        if cloud == 'aws':
            result = Shell.run(f"aws ec2 attach-volumes --volume-id {volume_id} --instance-id {vm_id} --device /dev/sdf")
            result = eval(result)['volume']
            return result

    def unmount(self, volume_id):
        """
        unmounts volume
        :param volume_id: volume id
        :return: dict
        """
        banner(f"unmount volume")
        if cloud == 'aws':
            result = Shell.run((f"aws ec2 dettach-volumes --volume-id {volume_id})
            result = eval(result)['volume']
            return result

    def delete(self, volume_id):

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
        deregister - volume
        raise NotImplementedError



if __name__ == "__main__":
    p = Provider()
    p.create()
    p.list()
