import json
import time
from pprint import pprint

import yaml

from google.oauth2 import service_account
from googleapiclient.discovery import build
from cloudmesh.common.DateTime import DateTime
from cloudmesh.volume.VolumeABC import VolumeABC
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
                      "status",
                      "id"
                      "zone"],
            "header": ["Name",
                       "Cloud",
                       "Status",
                       "ID",
                       "Zone"]
        }
    }

    def __init__(self, name):
        cloud = name
        config = Config()
        self.default = config["cloudmesh.volume.google.default"]
        self.credentials = config["cloudmesh.volume.google.credentials"]
        self.auth = self.credentials['auth']
        self.compute_scopes = ['https://www.googleapis.com/auth/compute',
                               'https://www.googleapis.com/auth/cloud-platform',
                               'https://www.googleapis.com/auth/compute.readonly']

    def update_dict(self, elements):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements.
        Libcloud
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
                "kind": "volume",
                "cloud": self.cloud,
                "name": self.name,

            })

            entry["cm"]["created"] = entry["updated"] = str(
                DateTime.now())

            d.append(entry)
        return d

    def _get_credentials(self, client_secret_file, scopes):
        """
        Method to get the credentials using the Service Account JSON file.
        :param client_secret_file: Service Account JSON File path.
        :param scopes: Scopes needed to provision.
        :return:
        """
        # Authenticate using service account.
        _credentials = service_account.Credentials.from_service_account_file(
            filename=client_secret_file,
            scopes=scopes)
        return _credentials

    def _get_compute_service(self):
        """
            Method to get compute service.
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

    def _process_disk(self, disk):
        """
        Method to convert the disk json to dict.
        :param disk: JSON with disk details
        :return:
        """
        disk_dict = {}
        disk_dict["name"] = disk["name"]
        disk_dict["zone"] = disk["zone"]
        disk_dict["type"] = disk["type"]
        disk_dict["SizeGb"] = disk["sizeGb"]
        disk_dict["status"] = disk["status"]
        disk_dict["created"] = disk["creationTimestamp"]
        disk_dict["id"] = disk["id"]
        disk_dict["cm.cloud"] = self.kind
        disk_dict["cm.kind"] = disk["kind"]
        disk_dict["cm.name"] = disk["name"]

        return disk_dict

    def _format_aggregate_list(self, disk_list):
        """
        Method to format the instance list to flat dict format.
        :param disk_list:
        :return: dict
        """
        result = []
        if disk_list is not None:
            if "items" in disk_list:
                items = disk_list["items"]
                for item in items:
                    if "disks" in items[item]:
                        disks = items[item]["disks"]
                        for disk in disks:
                            # Extract the disk details.
                            result.append(self._process_disk(disk))

        return result

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

    def list(self, **kwargs):
        """
        Retrieves an aggregated list of persistent disks.
        Currently, only sorting by "name" or "creationTimestamp desc"
        is supported.
        :return: an array of dicts representing the disks
        """
        result = None
        try:
            compute_service = self._get_compute_service()
            disk_list = compute_service.disks().aggregatedList(
                project=self.auth["project_id"],
                orderBy="name").execute()
            result = self._format_aggregate_list(disk_list)
            print(self.Print(result, kind='volume', output=kwargs['output']))
        except Exception as se:
            print(se)
        return result

    def create(self, name=None, **kwargs):
        # def create(self,
        #            NAME=None,
        #            size=None,
        #            volume_type=None,
        #            description=None,
        #            dryrun=None
        #            ):
        """
        Create a volume.
        """

        raise NotImplementedError

    def delete(self, name=None):
        """
        Delete volume
        :param name:
        :return:
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
        raise NotImplementedError

    def mount(self, volume=None, vm=None):
        """
        mounts volume
        :param name: the name of the volume
        :param volume: volume id
        :return: dict
        """
        raise NotImplementedError