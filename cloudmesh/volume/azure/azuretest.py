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
            heading: azure
            host: TBD
            label: {name}
            kind: azure
            version: TBD
            service: volume
          credentials:
            client_id: AZURE_APPLICATION_ID
            secret: AZURE_SECRET_KEY
            tenant: AZURE_TENANT_ID
            subscription: AZURE_SUBSCRIPTION_ID
    """

    volume_states = [
        'in-use',
        'available',
        'creating',
        'deleted',
        'deleting',
        'error',
        'inuse'
    ]

    output = {

        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "cm.region",
                      #"AvailabilityZone",
                      "CreateTime",
                      "Encrypted",
                      "Size",
                      #"SnapshotId",
                      "States",
                      #"VolumeId",
                      "Iops",
                      #"Tags",
                      "VolumeType",
                      #"created",
                      "AttachedToVm"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "Region",
                       #"AvailabilityZone",
                       "CreateTime",
                       "Encrypted",
                       "Size",
                       #"SnapshotId",
                       "Status",
                        #"VolumeId",
                       "Iops",
                       #"Tags",
                       "VolumeType",
                       #"Created",
                       "AttachedToVm"
                       ],
        }
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
            secret=cred['AZURE_SECRET_KEY'],
            tenant=cred['AZURE_TENANT_ID']
        )

        subscription = cred['AZURE_SUBSCRIPTION_ID']

        # Management Clients
        self.resource_client = ResourceManagementClient(
            credentials, subscription)
        self.compute_client = ComputeManagementClient(
            credentials, subscription)