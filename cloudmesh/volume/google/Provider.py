#
# class Provider(VolumeABC):
#
#   def list( .... ):
#      raise ImpelentainError

from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config

class Provider(VolumeABC):
    kind = "google"

    sample = """
    cloudmesh:
      volume:
        {name}:
          cm:
            active: true
            heading: {name}
            host: TBD
            label: {name}
            kind: google
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
        "status": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "vm_state",
                      "status",
                      "task_state"],
            "header": ["Name",
                       "Cloud",
                       "State",
                       "Status",
                       "Task"]
        },
        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "vm_state",
                      "status",
                      "task_state",
                      "metadata.image",
                      "metadata.flavor",
                      "ip_public",
                      "ip_private",
                      "cm.creation_time",
                      "launched_at"],
            "header": ["Name",
                       "Cloud",
                       "State",
                       "Status",
                       "Task",
                       "Image",
                       "Flavor",
                       "Public IPs",
                       "Private IPs",
                       "Creation time",
                       "Started at"],
            "humanize": ["launched_at"]
        },
        "image": {
            "sort_keys": ["cm.name",
                          "extra.minDisk"],
            "order": ["cm.name",
                      "size",
                      "min_disk",
                      "min_ram",
                      "status",
                      "cm.driver"],
            "header": ["Name",
                       "Size (Bytes)",
                       "MinDisk (GB)",
                       "MinRam (MB)",
                       "Status",
                       "Driver"]
        },
        "flavor": {
            "sort_keys": ["cm.name",
                          "vcpus",
                          "disk"],
            "order": ["cm.name",
                      "vcpus",
                      "ram",
                      "disk"],
            "header": ["Name",
                       "VCPUS",
                       "RAM",
                       "Disk"]
        },
        "key": {
            "sort_keys": ["name"],
            "order": ["name",
                      "type",
                      "format",
                      "fingerprint",
                      "comment"],
            "header": ["Name",
                       "Type",
                       "Format",
                       "Fingerprint",
                       "Comment"]
        },
        "secrule": {
            "sort_keys": ["name"],
            "order": ["name",
                      "tags",
                      "direction",
                      "ethertype",
                      "port_range_max",
                      "port_range_min",
                      "protocol",
                      "remote_ip_prefix",
                      "remote_group_id"
                      ],
            "header": ["Name",
                       "Tags",
                       "Direction",
                       "Ethertype",
                       "Port range max",
                       "Port range min",
                       "Protocol",
                       "Range",
                       "Remote group id"]
        },
        "secgroup": {
            "sort_keys": ["name"],
            "order": ["name",
                      "tags",
                      "description",
                      "rules"
                      ],
            "header": ["Name",
                       "Tags",
                       "Description",
                       "Rules"]
        },
        "ip": {
            "order": ["name", 'floating_ip_address', 'fixed_ip_address'],
            "header": ["Name", 'Floating', 'Fixed']
        },
    }
    def __init__(self,name):
        self.cloud = name

    def create(self,
                name=None,
                csek_key_file=None,
                description=None,
                guest_os_features=None,
                labels=None,
                licenses=None,
                replica_zones=None,
                resources_policies=None,
                require_csek_key=False,
                size=None,
                type=None,
                image_project=None,
                image=None,
                image_family=None,
                source_snapshot=None,
                kms_key=None,
                kms_keyring=None,
                kms_location=None,
                kms_project=None,
                region=None,
                zone=None,
                dryrun=False):

        """
        Create a disk.

        :param name: Names of the disks to create
        :param csek_key_file: Path to a Customer-Supplied Encryption Key (CSEK)
        :param description: An optional, textual description for the disks
                            being created.
        :param guest_os_features: This parameter enables one or more features
                                    for VM instances that use the image for
                                    their boot disks. Must be one of:
                                    MULTI_IP_SUBNET, SECURE_BOOT,
                                    UEFI_COMPATIBLE, VIRTIO_SCSI_MULTIQUEUE,
                                    WINDOWS
        :param labels: List of label key-value pairs
        :param liscences: List of URI's to licence resources
        :param replica_zones: A comma-separated list of exactly 2 zones that a
                                regional disk will be replicated to.
        :param require_csek_key: Refuse to create resources not protected by
                                    a user managed key in the key file
        :param resoucrces_policies: A list of resource policy names to be
                                    added to the disk
        :param size: Size of the disk. Whole number followed by 'GB' or 'TB'
                                for gigabyte or terabyte
        :param type: Type of the disk
        :param image_project: Project against which all image and image family
                                references will be resolved.
        :param image: An image to apply to the disks being created.
        :param image_family: The image family for the operating system that
                                the boot disk will be initialized with.
        :param source_snapshot: Source snapshot used to create the disks.
        :param kms_key: ID of the key or fully qualified identifier for the key.
        :param kms_keyring: The KMS keyring of the key
        :param kms_project: The cloud project for the key
        :param region: Region of the disks to create.
        :param zone: Zone of the disks to create.
        :param dryrun:
        :return:
        """
        raise NotImplementedError

    def delete(self,
               name=None,
               region=None,
               zone=None,
               dryrun=False):
        """
        Delete a disk

        :param name: Name of the disk
        :param region: Region of the disk
        :param zone: Zone of the disk
        :param dryrun:
        :return:
        """
        raise NotImplementedError

    def describe(self,
                 name=None,
                 region=None,
                 zone=None,
                 dryrun=False):
        """
        Displays all data associated with a disk in a project.

        :param name: Name of the disk
        :param region: Region of the disk
        :param zone: Zone of the disk
        :param dryrun:
        :return:
        """
        raise NotImplementedError

    def list(self,
             name=None,
             regexp=None,
             regions=None,
             zones=None,
             filter=None,
             limit=None,
             page_size=None,
             sort_by=None,
             uri=None,
             dryrun=False):
        """
        Displays all disks in a project

        :param name: (DEPRECATED) If provided, show details for the specified
                        names and/or URIs of resources.
        :param regexp: (DEPRECATED) Regular expression to filter the names of
                        the results on. Any names that do not match the entire
                        regular expression will be filtered out.
        :param regions: (DEPRECATED) If provided, only regional resources
                        are shown.
        :param zones: (DEPRECATED) If provided, only zonal resources are shown.
        :param filter: Apply a Boolean filter to each resource item to
                        be listed.
        :param limit: Specifies the maximum number of resources to list.
        :param page_size:  Specifies the maximum number of resources per page.
        :param sort_by: Comma-separated list of resource field key names
                        to sort by.
        :param uri: Print a list of resource URIs instead of the default output.
        :param dryrun:
        :return:
        """
        raise NotImplementedError