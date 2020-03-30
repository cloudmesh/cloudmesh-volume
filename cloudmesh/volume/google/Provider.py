import json
import time
from pprint import pprint

import yaml

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
            sizeGB: 200
          credentials:
            type: {type}
            auth:
              json_file: {filename}
              project_id: {project_id}
              client_email: {client_email}
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
        self.default = config["cloudmesh.volume.google.default"]
        self.credentials = config["cloudmesh.volume.google.credentials"]
        self.auth = self.credentials['auth']
        self.compute_scopes = ['https://www.googleapis.com/auth/compute',
                               'https://www.googleapis.com/auth/cloud-platform',
                               'https://www.googleapis.com/auth/compute.readonly']

    def update_dict(self, elements, kind=None):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements.
        returns an object or list of objects With the dict method
        this object is converted to a dict. Typically this method is used
        internally.
        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
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
                "kind": kind,
                "cloud": self.cloud,
                "name": entry["name"],
                "driver": kind
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
        # Authenticate using service account.
        _credentials = service_account.Credentials.from_service_account_file(
            filename=path_to_service_account_file,
            scopes=scopes)
        return _credentials

    def _get_compute_service(self):
        """
            Method to get google compute service v1.
        """
        service_account_credentials = self._get_credentials(
            self.auth['path_to_json_file'],
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
            project=self.auth["project_id"]).execute()
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
        name = volume.create_name()
        print(name)
        create_disk = compute_service.disks().insert(
            project=self.auth["project_id"]).execute()


        raise NotImplementedError

    def delete(self, name=None):
        """
        Delete volume
        :param name:
        :return:
        """
        raise NotImplementedError

    def attach(self, NAME=None, vm=None):

        """
        attatch volume to a vm

        :param NAME: volume name
        :param vm: vm name which the volume will be attached to
        :return: dict
        """

        raise NotImplementedError

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