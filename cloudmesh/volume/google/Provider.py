from cloudmesh.common.util import banner
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.VolumeABC import VolumeABC
from google.oauth2 import service_account
from googleapiclient.discovery import build
from time import sleep
from googleapiclient.errors import HttpError
from cloudmesh.common.console import Console
from pprint import pprint

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
            sizeGb: '200'
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
                      "zone",
                      "users",
                      "description",
                      "labels"],
            "header": ["Name",
                       "Kind",
                       "Cloud",
                       "Status",
                       "Size",
                       "Type",
                       "Created",
                       "ID",
                       "Zone",
                       "VMs",
                       "Description",
                       "Tags"]
        }
    }

    def __init__(self, name):
        """
        Get Google Cloud credentials and defaults from cloudmesh.yaml and set
        scopes for Google Compute Engine

        :param name: name of cloud provider in cloudmesh.yaml file under
                     cloudmesh.volume
        """
        self.cloud = name
        config = Config()
        self.default = config[f"cloudmesh.volume.{name}.default"]
        self.credentials = config[f"cloudmesh.volume.{name}.credentials"]
        self.compute_scopes = [
            'https://www.googleapis.com/auth/compute',
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/compute.readonly']

    def _wait(self,
             time=None):
        """
        This function waiting for volume to be updated

        :param time: time to wait in seconds
        """
        sleep(time)

    def update_dict(self, elements):
        """
        This function adds a cloudmesh cm dict to each dict in the list
        elements. Typically this method is used internally.

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
            if '/' in entry['type']:
                entry['type'] = entry['type'].rsplit('/', 1)[1]
            if '/' in entry['zone']:
                entry['zone'] = entry['zone'].rsplit('/', 1)[1]
            if 'targetLink' in entry:
                name = entry['targetLink'].rsplit('/', 1)[1]
            else:
                name = entry['name']
            vm_list = []
            if 'users' in entry:
                for user in entry['users']:
                    user = user.rsplit('/', 1)[1]
                    vm_list.append(user)
            entry['users'] = vm_list
            _labels = []
            if 'labels' in entry:
                for label in entry['labels']:
                    _labels.append(label)
            entry['labels'] = _labels
            if "cm" not in entry:
                entry['cm'] = {}
            entry["cm"].update({
                "kind": 'volume',
                "cloud": self.cloud,
                "name": name,
                "status": entry['status']
            })
            d.append(entry)
        return d

    def _get_credentials(self, path_to_service_account_file, scopes):
        """
        Method to get the credentials using the Service Account JSON file.

        :param path_to_service_account_file: Service Account JSON File path.
        :param scopes: Scopes needed to provision.
        :return: credentials used to get compute service
        """
        _credentials = service_account.Credentials.from_service_account_file(
            filename=path_to_service_account_file,
            scopes=scopes)
        return _credentials

    def _get_compute_service(self):
        """
        Method to get google compute service v1.

        :return: Google Compute Engine API
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
        # add kwargs['NAMES']
        # add kwargs['NAME']
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

    def create(self, **kwargs):
        """
        Creates a persistent disk in the specified project using the data in
        the request.

        :return: a list containing the newly created disk
        """
        compute_service = self._get_compute_service()
        volume_type = kwargs['volume_type']
        size = kwargs['size']
        description = kwargs['description']
        if volume_type is None:
            volume_type = self.default["type"]
        if size is None:
            size = self.default["sizeGb"]
        compute_service.disks().insert(
            project=self.credentials["project_id"],
            zone=self.default['zone'],
            body={'type': volume_type,
                  'name': kwargs['NAME'],
                  'sizeGb': str(size),
                  'description': description}).execute()
        new_disk = compute_service.disks().get(
                project=self.credentials["project_id"],
                zone=self.default['zone'],
                disk=kwargs['NAME']).execute()
        # wait for disk to finish being created
        while new_disk['status'] != 'READY':
            self._wait(1)
            new_disk = compute_service.disks().get(
                project=self.credentials["project_id"],
                zone=self.default['zone'],
                disk=kwargs['NAME']).execute()

        update_new_disk = self.update_dict(new_disk)

        return update_new_disk

    def delete(self, name=None):
        """
        Deletes the specified persistent disk.
        Deleting a disk removes its data permanently and is irreversible.

        :param name: Name of the disk to delete
        """
        compute_service = self._get_compute_service()
        disk_list = self.list()
        # find disk in list and get zone
        zone = None
        for disk in disk_list:
            if disk['name'] == name:
                zone = str(disk['zone'])
        if zone is None:
            banner(f'{name} was not found')
            return
        compute_service.disks().delete(
            project=self.credentials["project_id"],
            zone=zone,
            disk=name).execute()
        deleted_disk = compute_service.disks().get(
            project=self.credentials["project_id"],
            zone=zone,
            disk=name).execute()
        # wait for disk to be deleted
        while deleted_disk['status'] == 'DELETING':
            self._wait(1)
            try:
                deleted_disk = compute_service.disks().get(
                    project=self.credentials["project_id"],
                    zone=zone,
                    disk=name).execute()
            except HttpError:
                return

    def _list_instances(self):
        """
        Gets a list of available VM instances

        :return: list of dicts representing VM instances
        """
        compute_service = self._get_compute_service()
        instance_list = compute_service.instances().aggregatedList(
            project=self.credentials["project_id"],
            orderBy='creationTimestamp desc').execute()
        found_instances = []
        items = instance_list["items"]
        for item in items:
            if "instances" in items[item]:
                instances = items[item]["instances"]
                for instance in instances:
                    # Add instance details to found_instance.
                    found_instances.append(instance)
        return found_instances

    def attach(self, names, vm=None):
        """
        Attach one or more disks to an instance

        :param names: name(s) of disk(s) to attach
        :param vm: instance name which the volume(s) will be attached to
        :return: updated disks with current status
        """
        compute_service = self._get_compute_service()
        # get zone of vm from list of vm
        instance_list = self._list_instances()
        zone_url = None
        for instance in instance_list:
            if instance['name'] == vm:
                zone_url = instance['zone']
        zone = zone_url.rsplit('/', 1)[1]
        # get URL source to disk(s) from list of disks
        disk_list = self.list()
        for name in names:
            source = None
            for disk in disk_list:
                if disk['name'] == name:
                    source = disk['selfLink']
            compute_service.instances().attachDisk(
                project=self.credentials['project_id'],
                zone=zone,
                instance=vm,
                body={'source': source,
                      'deviceName': name}).execute()

        attached_disks = []
        get_instance = compute_service.instances().get(
            project=self.credentials["project_id"],
            zone=zone,
            instance=vm).execute()
        for disk in get_instance['disks']:
            attached_disks.append(disk['deviceName'])
        # wait for disks to be attached
        while names not in attached_disks:
            self._wait(1)
            get_instance = compute_service.instances().get(
                project=self.credentials["project_id"],
                zone=zone,
                instance=vm).execute()
            for disk in get_instance['disks']:
                attached_disks.append(disk['deviceName'])

        result = self.list()

        return result

    def detach(self, name=None):
        """
        Detach a disk from all instances

        :param name: name of disk to detach
        :return: dict representing updated status of detached disk
        """
        compute_service = self._get_compute_service()
        # Get name of attached instance(s) from list of disks
        instances = []
        zone = None
        disk_list = self.list()
        for disk in disk_list:
            if disk['name'] == name:
                zone = disk['zone']
                for user in disk['users']:
                    instances.append(user)
        # detach disk from all instances
        for instance in instances:
            compute_service.instances().detachDisk(
                project=self.credentials['project_id'],
                zone=zone,
                instance=instance,
                deviceName=name).execute()

        detached_disk = compute_service.disks().get(
            project=self.credentials["project_id"],
            zone=zone,
            disk=name).execute()
        # wait for disk to be detached
        while 'users' in detached_disk:
            self._wait(1)
            detached_disk = compute_service.disks().get(
                project=self.credentials["project_id"],
                zone=zone,
                disk=name).execute()

        result = self.update_dict(detached_disk)

        return result[0]

    def add_tag(self, **kwargs):
        """
        Add a key:value label to the disk
        Unable to change the name of a disk in Google Cloud

        :param kwargs: name of the disk with a key and a value for the label
        :return: updated list of disks with new label
        """
        compute_service = self._get_compute_service()
        disk_list = self.list()
        # find disk in list and get zone
        zone = None
        labelfingerprint = None
        for disk in disk_list:
            if disk['name'] == kwargs['NAME']:
                zone = str(disk['zone'])
                labelfingerprint = disk['labelFingerprint']
        compute_service.disks().setLabels(
            project=self.credentials['project_id'],
            zone=zone,
            resource=kwargs['NAME'],
            body={'labelFingerprint': labelfingerprint,
                  'labels': {kwargs['key']: str(kwargs['value'])}}).execute()

        tagged_disk = compute_service.disks().get(
            project=self.credentials["project_id"],
            zone=self.default['zone'],
            disk=kwargs['NAME']).execute()
        # wait for tag to be applied
        while tagged_disk['labels']:
            self._wait(1)
            try:
                tagged_disk = compute_service.disks().get(
                    project=self.credentials["project_id"],
                    zone=self.default['zone'],
                    disk=kwargs['NAME']).execute()
            except KeyError:
                pass

        updated_disk = self.update_dict(tagged_disk)
        return updated_disk[0]

    def status(self, name=None):
        """
        Gets status of specified disk

        :param name: name of disk
        :return: status of disk
        """
        compute_service = self._get_compute_service()
        disk_list = self.list()
        vol = None
        for disk in disk_list:
            if disk['name'] == name:
                vol = disk
        volume_status = vol['status']
        volume_vm = vol['users']
        print(volume_status)
        print(volume_vm)

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
        print(name)
        print(from_vm)
        print(to_vm)
        self.detach(name)
        self.attach(name, vm=to_vm)

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
        # delete to_volume then recreate from source of from_volume
        raise NotImplementedError
