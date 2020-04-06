# Cloudmesh Volume Management

## Abstract

A simple abstraction layer to manage Cloud Volumes for AWS, Azure,
Google, Openstack, Oracle and Multipass

In this project we will be developing features related to completing and
simplifying the volume management interface to an existing cloud. We
will also benchmark the clouds while comparing the volume management
functions that are deployed on different clouds.

## Volume Management functions

* volume list
  
  List volumes.
  
  If NAMES are given, search through all the active clouds and list all the volumes.
  
  If NAMES and cloud are given, list all volumes under the cloud.
  
  If cloud is given, list all the volumes under the cloud.
  
  If cloud is not given, list all the volumes under current cloud.

  If vm is given, under the current cloud, list all the volumes attaching to the vm.
  
  If region is given, under the current cloud, list all volumes in that region.
      
```
    volume list NAMES
                [--vm=VM]
                [--region=REGION]
                [--cloud=CLOUD]
                [--refresh]
                [--dryrun]
```

* volume create

    Create a volume.
    
    If success, the volume will be saved as the most recent volume.     
```
    volume create [NAME]
                  [--size=SIZE]
                  [--volume_type=TYPE]
                  [--description=DESCRIPTION]
                  [--dryrun]
```

* volume attach

    Attach volumes to a vm.
    
    If NAMES is not specified, attach the last created volume to vm.    
```
    volume attach [NAMES]
                  [--vm=VM]
```

* volume detach

    Detach volumes from vms.
    
    If NAMES is not specified, detach the last created volume from vm.
    
    If success, the last volume will be saved as the most recent volume. 
``` 
    volume detach [NAMES]  
```

* volume delete

    Delete volumes.
    
    If NAMES is not given, delete the most recent volume.
```
    volume delete [NAMES] 
```

* volume add_tag

    Add tag for a volume. For example: key="Name", value="user-volume-1".
     
    It could also be used to rename or name a volume.
     
    If NAME is not specified, then tag will be added to the most recent volume.
    
    If success, the volume will be saved as the most recent volume. 
    
```
    volume add_tag  [NAME]
                    [--key=KEY]
                    [--value=VALUE]
```
    
* volume migrate
  
  Migrate volume from one vm to another vm between different regions,
  services or providers. 
  
``` 
  volume migrate NAME FROM_VM TO_VM 
```

* volume sync
  
  Sync contents of one volume to another volume. It is  a copy of all 
  changed content from one volume to the other.
  
```
    volume sync FROM_VOLUME TO_VOLUME
```

## Volume Providers

### Multipass

* <https://freshbrewed.science/ubuntu-multipass-part-deux/index.html>

#### Multipass volume management functions

mount(self, name="cloudmesh", source=None, destination=None)
```
mounts the source into the instance at the given destination

Required Parameters: 

        source --
    
            The name of source (volume?)

        destination --

            The name of vm???
```

umount(self, name="cloudmesh", path=None)
```
Unmount a volume from an instance.

Required Parameters:

        source --

             The name of source (volume?)
```

transfer(self, name="cloudmesh", source=None, destination=None,
recursive=True):

``` Copies files or entire directories into the vm

Required Parameters: 

        source --
    
            The name of source (volume?)

        destination --

            The name of vm???
```

:o2: Add functions from provider with descriptions of required
parameters

### AWS

* AWS CLI:   
  <https://docs.aws.amazon.com/cli/latest/reference/ec2/create-volume.html>
* Amazon EBS:   
  <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-creating-volume.html>
* Amazon python api:   
  <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>
* REST api:   
  <https://docs.aws.amazon.com/apigateway/api-reference/>
* Documentation about volume cost:   
  <https://aws.amazon.com/ebs/pricing/>  
  <https://medium.com/@stefanroman/calculate-price-of-ebs-volumes-with-python-76687bb24530>
* manual:   
  <https://docs.aws.amazon.com/>

#### AWS volume management functions

list(**kwargs)

    """        
        This function list all volumes as following:
        If NAME (volume_name) is specified, it will print out info of NAME
        If NAME (volume_name) is not specified, it will print out info of all volumes
        If vm is specified, it will print out all the volumes attached to vm
        If region(availability zone) is specified, it will print out all the volumes in that region

        :param NAME: name of volume
        :param vm: name of vm
        :param region: name of availability zone
        :return: dict
    """

create(**kwargs)

    """
       Create a volume.

       :param NAME (string): name of volume
       :param region (string): availability-zone
       :param size (integer): size of volume
       :param volume_type (string): type of volume
       :return: dict
    """
    
delete volumes(NAME)
    
    """    
        This function delete one volume.

        :param NAME (string): volume name
        :return: dict        
    """
    
attach(NAMES, vm, device, dryrun=False):

    """        
        This function attach one or more volumes to vm. It returns self.list() to list the updated volume.
        The updated dict with
        "AttachedToVm" showing the name of vm where the volume attached to

        :param NAMES (string): names of volumes
        :param vm (string): name of vm
        :param device (string): The device name which is the attaching point to vm. 
                                This function provided 5 attaching points.
        :param dryrun (boolean): True|False
        :return: dict
    """

detach(NAME):

    """
        This function detach a volume from vm. It returns self.list(NAME) to list the updated volume. 
        The vm under "AttachedToVm" will be removed if volume is successfully detached.

        :param NAME: name of volume to detach
        :return: dict
    """
    
add_tag(NAME, **kwargs):

    """    
        This function add tag to a volume. 
        In aws Boto3, key for volume name is "Name". For example, key="Name", value="user-volume-1". 
        It could also be used to rename or name a volume. 

        :param NAME: name of volume
        :param kwargs:
                    key: name of tag
                    value: value of tag
        :return: dict        
    """

:o2: Add functions from provider with descriptions of required parameters

### Google

* python api:   
  <http://googleapis.github.io/google-api-python-client/docs/dyn/compute_v1.html>
* REST api for cumpute disks documentation:   
  <https://cloud.google.com/compute/docs/reference/rest/v1/disks?hl=en_US>
* Documentation about volume cost:   
  <https://cloud.google.com/compute/disks-image-pricing>
* manual:   
  <https://cloud.google.com/docs>

#### Google volume management functions

:o2: Add functions from provider with descriptions of required parameters

### Azure

* Azure CLI:   
  <https://docs.microsoft.com/en-us/cli/azure/netappfiles/volume?view=azure-cli-latest#az-netappfiles-volume-create>
* REST:   
  <https://docs.microsoft.com/en-us/rest/api/netapp/volumes>

#### Azure volume management functions

:o2: Add functions from provider with descriptions of required parameters

### OpenStack

* python:   
  <https://docs.openstack.org/python-cinderclient/latest/>
* REST:   
  <https://docs.openstack.org/api-ref/block-storage/>
* <https://docs.openstack.org/python-openstackclient/pike/cli/command-objects/volume.html>

#### OpenStack volume management functions

:o2: Add functions from provider with descriptions of required parameters

List Volumes
```
list(**kwargs):
    Lists all the volumes  
```

Create Volume
```
create(**kwargs)
    Create Volume Creates a new volume

Required Parameters: 
        name: Name of the volume
           
```

Delete Volume
```
delete(name)
    Deletes the specified volume. 

Required Parameters: 
        name: Name of the volume to be deleted
```

Attach Volume
```
attach(name,vm)
    Attaches the specified volume to the specified VM instance.

Required Parameters: 
        name: Name of the volume to be attached
        vm: Instance name
```

Detach Volume
```
Detach(name,vm)
    Detaches the specified volume from a VM instance

Required Parameters: 
        name: Name of the volume to be detached
        vm: Instance name
```
### Oracle

* API:   
  <https://docs.cloud.oracle.com/en-us/iaas/api/#/en/iaas/20160918/Volume/>
* OCI API:   
  <https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/core/client/oci.core.BlockstorageClient.html>

#### Oracle volume management functions

:o2: Add functions from provider with descriptions of required parameters

List Volumes
```
list(**kwargs):
    Lists the volumes in the specified compartment

Required Parameters: 
        compartment_id: The OCID of the compartment that contains the volume          
```

Create Volume
```
create(**kwargs)

    Create Volume Creates a new volume in the specified compartment.
    Volumes can be created in sizes ranging from 50GB to 32 TB, in 1 GB
    (1024 MB) increments. By default, volumes are 50GB.

Required Parameters: 
        availability_domain: The availability domain of the volume
                             Example: Uocm:PHX-AD-1
        compartment_id: The OCID of the compartment that contains the volume
           
```

Delete Volume
```
delete(name)

    Deletes the specified volume. The volume cannot have an active
    connection to an instance.

Warning: All data on the volume will be permanently lost when the volume is deleted.

Required Parameters: 
        name: Name of the volume to be deleted
```

Attach Volume
```
attach(name,vm)
    Attaches the specified volume to the specified VM instance.

Required Parameters: 
        name: Name of the volume to be attached
        vm: Instance name
```

Detach Volume
```
Detach(name,vm)
    Detaches the specified volume from a VM instance

Required Parameters: 
        name: Name of the volume to be detached
        
```

## Documentation on how to move volumes from one provider to the next 

* from Amazon

* from Cloud Storage

  * Migrating from Cloud Storage to Amazon S3

    <https://www.quora.com/How-can-I-migrate-data-from-Google-cloud-storage-into-AWS-S3-buckets>

  * Migrating from Cloud Storage to Azure Blob Storage

    <https://blog.bitscry.com/2019/12/30/data-transfer-google-cloud-storage-to-azure-blob-storage/>

  * Migrating from Cloud Storage to OpenStack

* from Azure Blob Storage

  * Migrating from Azure Blob Storage to Amazon S3

  * Migrating from Azure Blob Storage to Cloud Storage

  * Migrating from Azure Blob Storage to OpenStack

* from OpenStack

## Test cases

Write test cases in the form of reproducable pytests


## <https://cloudmesh.github.io/cloudmesh-manual/>

