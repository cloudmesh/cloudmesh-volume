from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.compute import ComputeManagementClient
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.VolumeABC import VolumeABC


class Provider(VolumeABC):
    """The provider class is a category of objects, and in this case objects
    related to creating, deleting, and listing a volume, along with other
    volume related functions."""

    kind = "volume"

    sample = """
    cloudmesh:
      volume:
        azure:
          cm:
            active: true
            heading: Azure
            host: azure.microsoft.com
            label: Azure
            kind: azure
            version: latest
            service: compute
          default:
            image: Canonical:UbuntuServer:16.04.0-LTS:latest
            size: Basic_A0
            group: default
            storage_account: cmdrive
            network: cmnetwork
            subnet: cmsubnet
            blob_container: vhds
            AZURE_VM_IP_CONFIG: cloudmesh-ip-config
            AZURE_VM_NIC: cloudmesh-nic
            AZURE_VM_DISK_NAME: cloudmesh-os-disk
            AZURE_VM_USER: cloudmesh
            AZURE_VM_PASSWORD: {password}
            AZURE_VM_NAME: cloudmeshVM
          credentials:
             AZURE_TENANT_ID: {tenantid}
             AZURE_SUBSCRIPTION_ID: {subscriptionid}
             AZURE_APPLICATION_ID: {applicationid}
             AZURE_SECRET_KEY: {secretkey}
             AZURE_REGION: eastus

    """

    volume_states = [
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
                      "cm.kind",
                      "cm.location",
                      "cm.size",
                      "cm.group_name",
                      "id",
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Region",
                       "Size",
                       "Group_Name",
                       "Id",
                       ],
        }
    }

    # need to update output

    def __init__(self, name="azure", configuration=None, credentials=None):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
        # configuration = configuration if configuration is not None \
        # else CLOUDMESH_YAML_PATH

        conf = Config(configuration)["cloudmesh"]

        self.user = Config()["cloudmesh"]["profile"]["user"]

        self.spec = conf["volume"][name]
        self.cloud = name
        self.location = 'eastus'
        self.size = 1
        self.group_name = self.spec["default"]['group']

        cred = self.spec["credentials"]
        self.default = self.spec["default"]
        self.cloudtype = self.spec["cm"]["kind"]
        super().__init__(name, configuration)

        # update credentials with the passed dict
        if credentials is not None:
            cred.update(credentials)

        # VERBOSE(cred, verbose=10)

        if self.cloudtype != 'azure':
            Console.error("This class is meant for azure cloud")

        # ServicePrincipalCredentials related Variables to configure in
        # cloudmesh.yaml file

        # AZURE_APPLICATION_ID = '<Application ID from Azure Active Directory
        # App Registration Process>'

        # AZURE_SECRET_KEY = '<Secret Key from Application configured in
        # Azure>'

        # AZURE_TENANT_ID = '<Directory ID from Azure Active Directory
        # section>'

        credentials = ServicePrincipalCredentials(
            client_id=cred['AZURE_APPLICATION_ID'],
            # application and client id are same thing
            secret=cred['AZURE_SECRET_KEY'],
            tenant=cred['AZURE_TENANT_ID']
        )

        subscription = cred['AZURE_SUBSCRIPTION_ID']

        # Management Clients
        self.compute_client = ComputeManagementClient(
            credentials, subscription)

    def Print(self, data, kind=None, output="table"):
        """
        Print out the result dictionary as table(by default) or json.

        :param data: dic returned from volume functions
        :param kind: kind of provider
        :param output: "table" or "json"
        :return:
        """
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
        elements. Libcloud returns an object or list of objects with the dict
        method. This object is converted to a dict. Typically this method is
        used internally.

        :param results: the original dicts.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
        :return: The list with the modified dicts
        """

        if results is None:
            return None

        d = []

        for entry in results:
            print("entry", entry)
            volume_name = entry['name']
            if "cm" not in entry:
                entry['cm'] = {}

            entry["cm"].update({
                "cloud": self.cloud,
                "kind": "volume",
                "name": volume_name,
                "location": self.location,
                "size": self.size,
                "group_name": self.group_name,
            })
            d.append(entry)
        return d

    def create(self, **kwargs):
        """
        Create a volume.

           :param name (string): name of volume
           :param region (string): availability-zone
           :param size (integer): size of volume
           :param volume_type (string): type of volume.
           :param description (string)
           :return: dict
        """
        disk_creation = self.compute_client.disks.create_or_update(
            self.group_name,
            kwargs['NAME'],
            {
                'location': self.location,
                'disk_size_gb': self.size,
                'creation_data': {
                    'create_option': 'Empty'
                }
            }
        )
        # return after create
        results = disk_creation.result().as_dict()
        result = self.update_dict([results])
        return result

    def delete(self, name=None):
        """
        Delete volumes.
        If name is not given, delete the most recent volume.

        :param name: List of volume name
        :return:
        """
        disk_deletion = self.compute_client.disks.delete(
            self.group_name,
            name,
            {
                'location': self.location
            }
        )
        # return after deleting
        results = disk_deletion.result()
        result = self.update_dict(results)
        return result

    def list(self, **kwargs):
        """
        This command list all volumes as follows:

        If NAMES are given, search through all the active clouds and list all
        the volumes.
        If NAMES and cloud are given, list all volumes under the cloud.
        If cloud is given, list all the volumes under the cloud.
        If cloud is not given, list all the volumes under current cloud.
        If vm is given, under the current cloud, list all the volumes attaching
        to the vm.
        If region is given, under the current cloud, list all volumes in that
        region.

        :param names: List of volume names
        :param vm: The name of the virtual machine
        :param region:  The name of the region
        :param cloud: The name of the cloud
        :param refresh: If refresh the information is taken from the cloud
        :return: dict
        """
        disk_list = \
            self.compute_client.disks.list_by_resource_group(self.group_name)
        # return disk_list
        found = []
        for disk in disk_list:
            results = disk.as_dict()
            result = self.update_dict([results])
            found.extend(result)
        return found

    def attach(self, names=None, vm=None):
        """
        This function attaches a given volume to a given instance

        :param names: Names of Volumes
        :param vm: Instance name
        :return: Dictionary of volumes
        """
        self.vms = self.compute_client.virtual_machines
        virtual_machine = self.vms.get(self.group_name, vm)
        results = []
        for name in names:
            disk = self.compute_client.disks.get(self.group_name, name)
            disk_attach = virtual_machine.storage_profile.data_disks.append({
                'lun': 1,
                'name': disk.name,
                'create_option': DiskCreateOption.attach,
                'managed_disk': {
                    'id': disk.id
                }
            })
            async_disk_attach = \
                self.vms.create_or_update(
                    self.group_name,
                    vm,
                    virtual_machine
                )
            async_disk_attach.wait(10)
            results = async_disk_attach.result().as_dict()
            result = self.update_dict([results])
            return result

    def detach(self, name=None):
        """
        Detach volumes from vm.
        If success, the last volume will be saved as the most recent volume.

        :param name: name of volumes to detach
        :return: dict
        """
        vm_info = self.compute_client.disks.get(self.group_name,
                                                name).as_dict()['managed_by']
        vm = vm_info.split(sep="/")[-1]
        self.vms = self.compute_client.virtual_machines
        virtual_machine = self.vms.get(self.group_name, vm)
        data_disks = virtual_machine.storage_profile.data_disks
        data_disks[:] = [
            disk for disk in data_disks if disk.name != name]
        async_vm_update = self.compute_client.virtual_machines.create_or_update(
            self.group_name,
            vm,
            virtual_machine
        )
        # return after detaching
        results = async_vm_update.result().as_dict()
        result = self.update_dict([results])
        return result[0]

    # Status and info use same code. Unable to only pull out 'disk_state' for
    #       status.

    def status(self, name=None):
        """
        This function returns status of volume, such as "available", "in-use"
        and etc..

        :param name: name of volume
        :return: string
        """
        disk_status = self.compute_client.disks.get(
            self.group_name,
            name
        )
        # return after getting info
        results = disk_status.as_dict()
        # res = dict((k, results[k]) for k in ['disk_state']
        #            if k in results)
        # return res
        result = self.update_dict([results])
        return result

    def info(self, name=None):
        """
        Search through the list of volumes, find the matching volume with name,
        return the dict of matched volume

        :param name: volume name to match
        :return: dict
        """
        disk_status = self.compute_client.disks.get(
            self.group_name,
            name
        )
        # return after getting info
        results = disk_status.as_dict()
        result = self.update_dict([results])
        return result

    def add_tag(self, **kwargs):
        """
        This function add tag to a volume.
        If NAME is not specified, then tag will be added to the last volume.
        If success, the volume will be saved as the most recent volume.

        :param name: name of volume
        :param kwargs:
                     key: name of tag
                     value: value of tag
        :return: self.list()
        """
        key = kwargs['key']
        value = kwargs['value']
        async_vm_update = self.compute_client.disks.create_or_update(
            self.group_name,
            kwargs['NAME'],
            {
                'location': self.location,
                'disk_size_gb': self.size,
                'creation_data': {
                    'create_option': 'Empty',
                },
                'tags': {
                    'Key': key,
                    'Value': value
                }
            }
        )
        async_vm_update.wait()
        # return after adding tags
        results = async_vm_update.result().as_dict()
        result = self.update_dict([results])
        return result[0]

    def migrate(self, **kwargs):
        """
        Migrate volume from one vm to another vm.

        :param name (string): the volume name
        :param vm (string): the vm name
        :param region (string): the availability zone
        :return: dict
        """
        raise NotImplementedError

    def sync(self, names):
        """
        synchronize one volume with another volume

        :param names (list): list of volume names
        :return: dict
        """
        raise NotImplementedError
