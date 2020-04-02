import json
import time
from pprint import pprint
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cloudmesh.common.DateTime import DateTime
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.volume.command import volume
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
from cloudmesh.common.Printer import Printer


class Provider(VolumeABC):
    kind = "google"

    sample = """
    cloudmesh:
      volume:
        {name}:
          cm:
            active: true
            heading: {name}
            host: https://console.cloud.google.com/compute/instances?project={project_id}
            label: {name}
            kind: google
            version: v1
            service: compute
          default:
            zone: us-central1-a
            type: projects/{project_id}/zones/{zone}/diskTypes/pd-standard
            sizeGB: '200'
          credentials:
            project_id: {project_id}
            path_to_service_account_json: {path}
    """

    output = {
        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.kind",
                      "cm.cloud",
                      "status",
                      "sizeGb",
                      "type",
                      "creationTimestamp",
                      "id",
                      "zone"],
            "header": ["Name",
                       "Kind",
                       "Cloud",
                       "Status",
                       "SizeGb",
                       "Type",
                       "Created",
                       "ID",
                       "Zone"]
        }
    }

    def __init__(self, name):
        self.cloud = name
        config = Config()
        self.default = config[f"cloudmesh.volume.{name}.default"]
        self.credentials = config[f"cloudmesh.volume.{name}.credentials"]
        self.compute_scopes=['https://www.googleapis.com/auth/compute',
                             'https://www.googleapis.com/auth/cloud-platform',
                             'https://www.googleapis.com/auth/compute.readonly']

    def update_dict(self, elements):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements.
        returns an object or list of objects with the dict method
        this object is converted to a dict. Typically this method is used
        internally.
        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :return: The list with the modified dicts
        """
        if elements is None:
            return None
        elif type(elements) == list:
            _elements = elements
        else:
            _elements = [elements]
        d = []
        for entry in _elements:
            if "cm" not in entry:
                entry['cm'] = {}
            entry["cm"].update({
                "kind": 'volume',
                "cloud": self.cloud,
                "name": entry["name"]
            })
            d.append(entry)
        return d

    def _get_credentials(self, path_to_service_account_file, scopes):
        """
        Method to get the credentials using the Service Account JSON file.
        :param path_to_service_account_file: Service Account JSON File path.
        :param scopes: Scopes needed to provision.
        :return:
        """
        _credentials = service_account.Credentials.from_service_account_file(
            filename=path_to_service_account_file,
            scopes=scopes)
        return _credentials

    def _get_compute_service(self):
        """
            Method to get google compute service v1.
        """
        service_account_credentials = self._get_credentials(
            self.credentials['path_to_service_account_json'],
            self.compute_scopes)
        # Authenticate using service account.
        if service_account_credentials is None:
            print('Credentials are required')
            raise ValueError('Cannot Authenticate without Credentials')
        else:
            compute_service = build('compute', 'v1',
                                    credentials=service_account_credentials)

        return compute_service

    def list(self, **kwargs):
        """
        Retrieves an aggregated list of persistent disks.
        Currently, only sorting by "name" or "creationTimestamp desc"
        is supported.
        :return: an array of dicts representing the disks
        """
        compute_service = self._get_compute_service()
        disk_list = compute_service.disks().aggregatedList(
            project=self.credentials["project_id"],
            orderBy='creationTimestamp desc').execute()
        # look thought all disk list zones and find zones w/ 'disks'
        # then get disk details and add to found
        found = []
        items = disk_list["items"]
        for item in items:
            if "disks" in items[item]:
                disks = items[item]["disks"]
                for disk in disks:
                    # Add disk details to found.
                    found.append(disk)

        result = self.update_dict(found)

        return result

    def create(self, name=None, **kwargs):
        """
        Creates a persistent disk in the specified project using the data in
        the request.
        :return: a dict representing the disk
        """

        compute_service = self._get_compute_service()
        banner('creating disk')
        if kwargs['volume_type'] is None:
            kwargs['volume_type'] = self.default["type"]
        if kwargs['size'] is None:
            kwargs['size'] = self.default["sizeGb"]
        create_disk = compute_service.disks().insert(
            project=self.credentials["project_id"],
            zone=self.default['zone'],
            body={'type': kwargs['volume_type'],
                  'name': kwargs['NAME'],
                  'sizeGB': kwargs['size']}).execute()
        pprint(create_disk)
        banner('disk created')
        result = self.update_dict(create_disk)
        return result

    def delete(self, name=None):
        """
        Deletes the specified persistent disk.
        Deleting a disk removes its data permanently and is irreversible.
        :param name: Name of the disk to delete
        """
        compute_service = self._get_compute_service()
        disk_list = self.list()
        # find disk in list and get zone
        zone_url = None
        for disk in disk_list:
            if disk['name'] == name:
                zone_url = str(disk['zone'])
        # get zone from end of zone_https
        zone = zone_url.rsplit('/', 1)[1]
        compute_service.disks().delete(project=self.credentials["project_id"],
                                       zone=zone, disk=name).execute()
        result = self.list()
        return result

    def attach(self, name=None, vm=None):

        """
        Attach a disk to an instance

        :param name: disk name
        :param vm: instance name which the volume will be attached to
        :return: dict
        """
        compute_service = self._get_compute_service()

        # get zone of vm from list of vm
        zone_url = None
        instance_list = compute_service.instance().aggregatedList(
            project=self.credentials["project_id"],
            orderBy='creationTimestamp desc').execute()
        found_instance = []
        items = instance_list["items"]
        for item in items:
            if "instances" in items[item]:
                instances = items[item]["instances"]
                for instance in instances:
                    # Add disk details to found.
                    found_instance.append(instance)
        for instance in found_instance:
            if instance['name'] == vm:
                zone_url = instance['zone']
        zone = zone_url.rsplit('/', 1)[1]

        # get URL source to disk from list of disks
        source = None
        disk_list = self.list()
        for disk in disk_list:
            if disk['name'] == name:
                source = disk['selfLink']
        compute_service.instance().attachDisk(
            project=self.credentials['project_id'],
            zone=zone,
            instance=vm,
            body={'source': source}).execute()

        result = self.list()
        return result

    def detach(self,
              NAME=None):

        """
        Dettach a volume from vm

        :param NAME: name of volume to dettach
        :return: str
        """
        raise NotImplementedError

    def migrate(self,
                name=None,
                from_vm=None,
                to_vm=None):

        """
        Migrate volume from one vm to another vm.

        :param name: name of volume
        :param from_vm: name of vm where volume will be moved from
        :param to_vm: name of vm where volume will be moved to
        :return: dict
        """
        raise NotImplementedError

    def sync(self,
             from_volume=None,
             to_volume=None):
        """
        Sync contents of one volume to another volume. It is  a copy of all
        changed content from one volume to the other.

        :param from_volume: name of the from volume
        :param to_volume: name of the to volume

        :return: str
        """
        raise NotImplementedError