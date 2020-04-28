from cloudmesh.common.util import banner
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.VolumeABC import VolumeABC
from google.oauth2 import service_account
from googleapiclient.discovery import build
from time import sleep
from googleapiclient.errors import HttpError
from cloudmesh.mongo.CmDatabase import CmDatabase


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
            version: TBD
            service: volume
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
        self.cm = CmDatabase()
        self.default = config[f"cloudmesh.volume.{name}.default"]
        self.credentials = config[f"cloudmesh.volume.{name}.credentials"]
        self.compute_scopes = [
            'https://www.googleapis.com/auth/compute',
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/compute.readonly']

    def _wait(self, time=None):
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
            if 'users' in entry:
                _users = []
                for user in entry['users']:
                    _users.append(user)
                    for item in _users:
                        if '/' in item:
                            _users = []
                            remove_user_url = user.rsplit('/', 1)[1]
                            _users.append(remove_user_url)
                entry['users'] = _users
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

    def _get_disk(self, zone, disk):
        """
        Get the specified persistent disk from the cloud

        :param zone: name of the zone in which the disk is located
        :param disk: name of the disk
        :return: a dict representing the disk
        """
        compute_service = self._get_compute_service()
        disk = compute_service.disks().get(
            project=self.credentials["project_id"],
            zone=zone,
            disk=disk).execute()
        return disk

    def _list_instances(self, instance=None):
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
                if instance is not None:
                    for vm in instances:
                        if vm == instance:
                            found_instances.append(vm)
                            continue
                else:
                    for vm in instances:
                        found_instances.append(vm)
        return found_instances

    def list(self, **kwargs):
        """
        Retrieves an aggregated list of persistent disks with most recently
        created disks listed first.

        :return: an array of dicts representing the disks
        """
        compute_service = self._get_compute_service()
        if kwargs and kwargs['refresh'] is False:
            result = self.cm.find(cloud=self.cloud, kind='volume')
            for key in kwargs:
                if key == 'NAME' and kwargs['NAME']:
                    result = self.cm.find_name(name=kwargs['NAME'])
                elif key == 'NAMES' and kwargs['NAMES']:
                    result = self.cm.find_names(names=kwargs['NAMES'])

            found = []
            if kwargs['region'] is not None:
                disk_list = compute_service.disks().list(
                    project=self.credentials['project_id'],
                    zone=kwargs['region'],
                    orderBy='creationTimestamp desc').execute()
                if 'items' in disk_list:
                    disks = disk_list['items']
                    for disk in disks:
                        found.append(disk)

                result = self.update_dict(found)

            if kwargs['NAMES'] is not None or kwargs['vm'] is not None:
                disk_list = compute_service.disks().aggregatedList(
                    project=self.credentials["project_id"],
                    orderBy='creationTimestamp desc').execute()

                if kwargs['NAMES'] is not None:
                    items = disk_list["items"]
                    for item in items:
                        if "disks" in items[item]:
                            disks = items[item]["disks"]
                            for disk in disks:
                                if disk in kwargs['NAMES']:
                                    found.append(disk)

                if kwargs['vm'] is not None:
                    items = disk_list["items"]
                    for item in items:
                        if "disks" in items[item]:
                            disks = items[item]["disks"]
                            for disk in disks:
                                if 'users' in disk:
                                    users = disk['users']
                                    for user in users:
                                        remove_user_url = user.rsplit('/', 1)[1]
                                        if remove_user_url == kwargs['vm']:
                                            found.append(disk)

                else:
                    items = disk_list["items"]
                    for item in items:
                        if "disks" in items[item]:
                            disks = items[item]["disks"]
                            for disk in disks:
                                found.append(disk)

                result = self.update_dict(found)

            return result

        elif kwargs and kwargs['refresh'] is True:

            found = []
            if kwargs['region'] is not None:
                disk_list = compute_service.disks().list(
                    project=self.credentials['project_id'],
                    zone=kwargs['region'],
                    orderBy='creationTimestamp desc').execute()
                if 'items' in disk_list:
                    disks = disk_list['items']
                    for disk in disks:
                        found.append(disk)

            elif kwargs['NAMES'] is not None or kwargs['vm'] is not None:
                disk_list = compute_service.disks().aggregatedList(
                    project=self.credentials["project_id"],
                    orderBy='creationTimestamp desc').execute()

                if kwargs['NAMES'] is not None:
                    items = disk_list["items"]
                    for item in items:
                        if "disks" in items[item]:
                            disks = items[item]["disks"]
                            for disk in disks:
                                if disk in kwargs['NAMES']:
                                    found.append(disk)

                elif kwargs['vm'] is not None:
                    items = disk_list["items"]
                    for item in items:
                        if "disks" in items[item]:
                            disks = items[item]["disks"]
                            for disk in disks:
                                if 'users' in disk:
                                    users = disk['users']
                                    for user in users:
                                        remove_user_url = user.rsplit('/', 1)[1]
                                        if remove_user_url == kwargs['vm']:
                                            found.append(disk)
            else:
                disk_list = compute_service.disks().aggregatedList(
                    project=self.credentials["project_id"],
                    orderBy='creationTimestamp desc').execute()
                items = disk_list["items"]
                for item in items:
                    if "disks" in items[item]:
                        disks = items[item]["disks"]
                        for disk in disks:
                            found.append(disk)

            result = self.update_dict(found)

            return result

        else:
            disk_list = compute_service.disks().aggregatedList(
                project=self.credentials["project_id"],
                orderBy='creationTimestamp desc').execute()

            found = []
            items = disk_list["items"]
            for item in items:
                if "disks" in items[item]:
                    disks = items[item]["disks"]
                    for disk in disks:
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
        zone = kwargs['region']
        if volume_type is None:
            volume_type = self.default["type"]
        if size is None:
            size = self.default["sizeGb"]
        if zone is None:
            zone = self.default['zone']
        compute_service.disks().insert(
            project=self.credentials["project_id"],
            zone=self.default['zone'],
            body={'type': volume_type,
                  'name': kwargs['NAME'],
                  'sizeGb': str(size),
                  'description': description}).execute()
        new_disk = self._get_disk(self.default['zone'], kwargs['NAME'])

        # wait for disk to finish being created
        while new_disk['status'] != 'READY':
            self._wait(1)
            new_disk = self._get_disk(zone, kwargs['NAME'])

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
        zone = None
        for disk in disk_list:  # find disk in list and get zone
            if disk['name'] == name:
                zone = str(disk['zone'])
        if zone is None:
            banner(f'{name} was not found')
            return
        compute_service.disks().delete(
            project=self.credentials["project_id"],
            zone=zone,
            disk=name).execute()

        # attempt to call disk from cloud
        try:
            deleted_disk = self._get_disk(zone, name)
            # wait for disk to be deleted if found in cloud
            if deleted_disk['status'] == 'DELETING':
                while deleted_disk['status'] == 'DELETING':
                    self._wait(1)
                    try:
                        deleted_disk = self._get_disk(zone, name)
                    except HttpError:
                        pass
        except HttpError:
            pass

    def _get_instance(self, zone, instance):
        """
        Get the specified instance from the cloud

        :param zone: zone in which the instance is located
        :param instance: name of the instance
        :return: a dict representing the instance
        """
        compute_service = self._get_compute_service()
        vm = compute_service.instances().get(
            project=self.credentials["project_id"],
            zone=zone,
            instance=instance).execute()
        return vm

    def _stop_instance(self, name=None, zone=None):
        """
        stops the instance with the given name

        :param name: name of the instance
        :zone: zone in which the instance is located
        """
        compute_service = self._get_compute_service()
        compute_service.instances().stop(
            project=self.credentials['project_id'],
            zone=zone,
            instance=name).execute()

        vm = self._get_instance(zone, name)
        # Wait for the instance to stop
        while vm['status'] != 'TERMINATED':
            self._wait(1)
            vm = self._get_instance(zone, name)

    def _start_instance(self, name=None, zone=None):
        """
        stops the instance with the given name

        :param name: name of the instance
        :zone: zone in which the instance is located
        """
        compute_service = self._get_compute_service()
        compute_service.instances().start(
            project=self.credentials['project_id'],
            zone=zone,
            instance=name).execute()

        vm = self._get_instance(zone, name)
        # Wait for the instance to start
        while vm['status'] != 'RUNNING':
            self._wait(1)
            vm = self._get_instance(zone, name)

    def attach(self, names, vm=None):
        """
        Attach one or more disks to an instance.  GCP requires that the
        instance be stopped when attaching a disk.  If the instance is running
        when the attach function is called, the function will stop the instance
        and then restart the instance after attaching the disk.

        :param names: name(s) of disk(s) to attach
        :param vm: instance name which the volume(s) will be attached to
        :return: updated disks with current status
        """
        compute_service = self._get_compute_service()
        instance_list = self._list_instances()
        zone_url = None
        instance_status = None
        for instance in instance_list:
            if instance['name'] == vm:
                zone_url = instance['zone']
                instance_status = instance['status']
        zone = zone_url.rsplit('/', 1)[1]

        # Stop the instance if necessary
        if instance_status == 'RUNNING':
            banner(f"Stopping VM {vm}")
            self._stop_instance(vm, zone)

        # get URL source to disk(s) from list of disks
        disk_list = self.list()
        for name in names:
            source = None
            for disk in disk_list:
                if disk['name'] == name:
                    source = disk['selfLink']
            banner(f"Attaching {name}")
            compute_service.instances().attachDisk(
                project=self.credentials['project_id'],
                zone=zone,
                instance=vm,
                body={'source': source,
                      'deviceName': name}).execute()
        new_attached_disks = []
        for name in names:
            get_disk = self._get_disk(zone, name)
            # wait for disk to finish attaching
            while 'users' not in get_disk:
                self._wait(1)
                get_disk = self._get_disk(zone, name)
            new_attached_disks.append(get_disk)
        # update newly attached disks
        result = self.update_dict(new_attached_disks)

        # Restart the instance if previously running
        if instance_status == 'RUNNING':
            banner(f"Restarting VM {vm}")
            self._start_instance(vm, zone)

        return result

    def detach(self, name=None):
        """
        Detach a disk from all instances.  GCP requires that the
        instance be stopped when detaching a disk.  If the instance is running
        when the detach function is called, the function will stop the instance
        and then restart the instance after detaching the disk.

        :param name: name of disk to detach
        :return: dict representing updated status of detached disk
        """
        compute_service = self._get_compute_service()
        instances = []
        zone = None
        disk_list = self.list()
        for disk in disk_list:
            if disk['name'] == name:
                zone = disk['zone']
                for user in disk['users']:
                    instances.append(user)

        # detach disk from all instances
        result = None
        for instance in instances:
            vm = self._get_instance(zone, instance)
            instance_status = vm['status']

            # Stop the instance if necessary
            if instance_status == 'RUNNING':
                banner(f"Stopping VM {instance}")
                self._stop_instance(instance, zone)

            banner(f"Detaching {name}")
            compute_service.instances().detachDisk(
                project=self.credentials['project_id'],
                zone=zone,
                instance=instance,
                deviceName=name).execute()

            # Wait for disk to detach
            detached_disk = self._get_disk(zone, name)
            if 'users' in detached_disk:
                while instance in detached_disk['users']:
                    self._wait(1)
                    detached_disk = self._get_disk(zone, name)

            # Restart the instance if necessary
            if instance_status == 'RUNNING':
                banner(f"Restarting VM {instance}")
                self._start_instance(instance, zone)

            # update newly detached disk
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
        label_fingerprint = None
        for disk in disk_list:
            if disk['name'] == kwargs['NAME']:
                zone = str(disk['zone'])
                label_fingerprint = disk['labelFingerprint']
        compute_service.disks().setLabels(
            project=self.credentials['project_id'],
            zone=zone,
            resource=kwargs['NAME'],
            body={'labelFingerprint': label_fingerprint,
                  'labels': {kwargs['key']: str(kwargs['value'])}}).execute()

        tagged_disk = self._get_disk(self.default['zone'], kwargs['NAME'])

        # wait for tag to be applied
        while 'labels' not in tagged_disk:
            self._wait(1)
            tagged_disk = self._get_disk(self.default['zone'], kwargs['NAME'])

        updated_disk = self.update_dict(tagged_disk)
        return updated_disk[0]

    def status(self, name=None):
        """
        Get status of specified disk, such as 'READY'

        :param name: name of disk
        :return: list containing dict representing the disk
        """
        disk_list = self.list()
        vol = []
        for disk in disk_list:
            if disk['name'] == name:
                vol.append(disk)
                break
        result = self.update_dict(vol)
        return result

    def migrate(self,
                name=None,
                from_vm=None,
                to_vm=None):

        """
        Migrate volume from one vm to another vm.

        :param name: name of volume
        :param from_vm: name of vm where volume will be moved from
        :param to_vm: name of vm where volume will be moved to
        :return: dict of disk with updated info
        """
        self.detach(name)
        self.attach(name, vm=to_vm)
        result = self.status(name)
        # this only would work when disk and instances are all in the same zone
        # include how to migrate disks between zones and regions
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
        # delete to_volume then recreate from source of from_volume?
        raise NotImplementedError
