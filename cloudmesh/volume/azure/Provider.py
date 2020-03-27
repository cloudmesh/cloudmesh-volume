import pprint
import azure
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.common.util import banner
from cloudmesh.common.Shell import Shell
from cloudmesh.configuration.Config import Config
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.Printer import Printer

from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient

client = get_client_from_auth_file(ComputeManagementClient, auth_path=C:\Users\plj2861\Documents\AshleyPersonal\School\IndianaUniversity\CloudComputing\azure_credentials.json)


class Provider(VolumeABC):

    """The provider class is a category of objects, and in this case objects
    related to creating, deleting, and listing a volume, along with other
    volume related functions."""

    kind = "volume"

    sample = """
        cloudmesh:
          cloud:
            {name}:
              cm:
                active: true
                heading: {name}
                host: TBD
                label: {name}
                kind: azure
                version: latest
                service: compute
              default:
                image: Canonical:UbuntuServer:16.04.0-LTS:latest
                size: Basic_A0
                resource_group: cloudmesh
                storage_account: cmdrive
                network: cmnetwork
                subnet: cmsubnet
                blob_container: vhds
                AZURE_VM_IP_CONFIG: cloudmesh-ip-config
                AZURE_VM_NIC: cloudmesh-nic
                AZURE_VM_DISK_NAME: cloudmesh-os-disk
                AZURE_VM_USER: TBD
                AZURE_VM_PASSWORD: TBD
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
        "vm": {
            "sort_keys": ["cm.name"],
            "order": [
                "cm.name",
                "cm.cloud",
                "id",
                "type",
                "location",
                "hardware_profile.vm_size",
                "storage_profile.image_reference.offer",
                "storage_profile.image_reference.sku",
                "storage_profile.os_disk.disk_size_gb",
                "provisioning_state",
                "vm_id",
                "cm.kind"],
            "header": [
                "Name",
                "Cloud",
                "Id",
                "Type",
                "Location",
                "VM Size",
                "OS Name",
                "OS Version",
                "OS Disk Size",
                "Provisioning State",
                "VM ID",
                "Kind"]
        },
        "image": {
            "sort_keys": ["cm.name",
                          "plan.publisher"],
            "order": ["cm.name",
                      "location",
                      "plan.publisher",
                      "plan.name",
                      "plan.product",
                      "operating_system"],
            "header": ["Name",
                       "Location",
                       "Publisher",
                       "Plan Name",
                       "Product",
                       "Operating System",
                       ]
        },
        "flavor": {
            "sort_keys": ["name",
                          "number_of_cores",
                          "os_disk_size_in_mb"],
            "order": ["name",
                      "number_of_cores",
                      "os_disk_size_in_mb",
                      "resource_disk_size_in_mb",
                      "memory_in_mb",
                      "max_data_disk_count"],
            "header": ["Name",
                       "NumberOfCores",
                       "OS_Disk_Size",
                       "Resource_Disk_Size",
                       "Memory",
                       "Max_Data_Disk"]},
    }


    def __init__(self, name="azure", configuration=None, credentials=None):
        """
        Initializes the provider. The default parameters are read from the
        configuration file that is defined in yaml format.

        :param name: The name of the provider as defined in the yaml file
        :param configuration: The location of the yaml configuration file
        """
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

        VERBOSE(cred, verbose=10)

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
            #application and client id are same thing
            secret=cred['AZURE_SECRET_KEY'],
            tenant=cred['AZURE_TENANT_ID']
        )

        subscription = cred['AZURE_SUBSCRIPTION_ID']

        # Management Clients
        self.compute_client = ComputeManagementClient(
            credentials, subscription)


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


    def update_dict(self, elements, kind=None):
        """
        The cloud returns an object or list of objects With the dict method this
        object is converted to a cloudmesh dict. Typically this method is used
        internally.

        :param elements: the elements
        :param kind: Kind is image, flavor, or node, secgroup and key
        :return:
        """

        if elements is None:
            return None
        elif type(elements) == list:
            _elements = elements
        else:
            _elements = [elements]
        d = []

        for entry in _elements:

            if "cm" not in entry.keys():
                entry['cm'] = {}

            entry["cm"].update({
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": entry['name']
            })

            if kind == 'vm':
                if 'created' not in entry["cm"].keys():
                    entry["cm"]["created"] = str(datetime.utcnow())
                entry["cm"]["updated"] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
                entry["cm"]["type"] = entry[
                    "type"]  # Check feasibility of the following items
                entry["cm"]["location"] = entry[
                    "location"]  # Check feasibility of the following items
                if 'status' in entry.keys():
                    entry["cm"]["status"] = str(entry["status"])
                if 'ssh_key_name' in entry.keys():
                    entry["cm"]["ssh_key_name"] = str(entry["ssh_key_name"])

            elif kind == 'flavor':

                entry["cm"]["created"] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]
                entry["cm"]["number_of_cores"] = entry["number_of_cores"]
                entry["cm"]["os_disk_size_in_mb"] = entry["os_disk_size_in_mb"]
                entry["cm"]["resource_disk_size_in_mb"] = entry[
                    "resource_disk_size_in_mb"]
                entry["cm"]["memory_in_mb"] = entry["memory_in_mb"]
                entry["cm"]["max_data_disk_count"] = entry[
                    "max_data_disk_count"]
                entry["cm"]["updated"] = str(datetime.utcnow())

            elif kind == 'image':

                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())
                entry["cm"]["name"] = entry["name"]

            elif kind == 'secgroup':

                entry["cm"]["name"] = entry["name"]
                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())

            elif kind == 'key':

                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())

            elif kind == 'secrule':

                entry['cm']['created'] = str(datetime.utcnow())
                entry['cm']['updated'] = str(datetime.utcnow())

            d.append(entry)
            # VERBOSE(d, verbose=10)

        return d


    def list(self,**kwargs):
        if kwargs["--refresh"]:
            con = openstack.connect(**self.config)
            results = con.list_volumes()
            result = self.update_dict(results)
            print(self.Print(result, kind='volume', output=kwargs['output']))
        else:
            # read record from mongoDB
            refresh = False
