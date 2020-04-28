# Cloudmesh Volume Management

{warning}

{icons}

## Abstract

A simple abstraction layer to manage Cloud Volumes for AWS, Azure,
Google, Openstack, Oracle and Multipass

In this project we will be developing features related to completing and
simplifying the volume management interface to an existing cloud. We
will also benchmark the clouds while comparing the volume management
functions that are deployed on different clouds.

## Manual

{manual}

See also: [Volume man page](https://cloudmesh.github.io/cloudmesh-manual/manual/volume.html)

## Volume Providers

### Multipass

* <https://freshbrewed.science/ubuntu-multipass-part-deux/index.html>

#### Multipass volume management functions

* Create Volume
```
create(**kwargs):

This function create a new volume.
Default parameters from self.default, such as: path="/Users/username/multipass".

Required Parameters:

        name: the name of volume
        path: path of volume
```

* Delete Volume
```
delete(name):

Delete volume.

If name is not given, delete the most recent volume.

Required Parameters:

        name: volume name
```


* List Volume
```
list(**kwargs):

This function list all volumes as following:
If NAME (volume name) is specified, it will print out info of NAME.
If NAME (volume name) is not specified, it will print out info of all
          volumes under current cloud.
If vm is specified, it will print out all the volumes attached to vm.
If region(path) is specified, it will print out
          all the volumes in that region. i.e. /Users/username/multipass

Required Parameters:

        NAME: name of volume
        vm: name of vm
        path: volume path
```


* Attach Volume
```
attach(names, vm):

This function attach one or more volumes to vm. It returns info of
updated volume. The updated dict with "AttachedToVm" showing
the name of vm where the volume attached to.

Required Parameters:

        names (string): names of volumes
        vm (string): name of vm
```


* Detach Volume
```
detach(name):

This function detach a volume from vm. It returns the info of the updated volume.
The vm under "AttachedToVm" will be removed if volume is successfully detached.
Will detach volume from all vms.

Required Parameters:

        name: name of volume to be dettached
```

* Add Tags for Volume
```
add_tag(**kwargs):

This function add tag to a volume.
If volume name is not specified, then tag will be added to the last volume.

Required Parameters:

        NAME: name of volume
        key: name of tag
        value: value of tag
```


* Volume Status
```
status(name=None):

This function get volume status, such as "in-use", "available", "deleted"

Required Parameters:

        name (string): volume name
```


* Migrate Volume
```
migrate(**kwargs):

Migrate volume from one vm to another vm. "region" is volume path.
If vm and volume are in the same region (path), migrate within the same region (path)
If vm and volume are in different regions, migrate between two regions (path)

Required Parameters:

        name (string): the volume name
        vm (string): the vm name
```


* Sync Volumes
```
sync(names):

sync contents of one volume to another volume

Required Parameters:

        names (list): list of volume names
```

### AWS

* AWS CLI:   
  <https://docs.aws.amazon.com/cli/latest/reference/ec2/create-volume.html>
* Amazon EBS:   
  <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-creating-volume.html>
* Amazon python boto3:   
  <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>
* REST api:   
  <https://docs.aws.amazon.com/apigateway/api-reference/>
* Documentation about volume cost:   
  <https://aws.amazon.com/ebs/pricing/>  
  <https://medium.com/@stefanroman/calculate-price-of-ebs-volumes-with-python-76687bb24530>
* manual:   
  <https://docs.aws.amazon.com/>

#### AWS volume management functions

* Create Volume
```
create(**kwargs):

This function create a new volume, with defalt parameters in self.default.

Optional Parameters:

        NAME (string): the name of volume
        size (int): the size of volume (GB)
        volume_type: volume type, gp2 for General Purpose SSD
        region (string): availability zone of volume
        snapshot (string): snapshot id
        encrypted (boolean): True|False
```

* Delete Volume
```
delete(name):

This function delete one volume. 
It will return the info of volume with "state" updated as "deleted" 
and will show in Database.

Required Parameters:
 
        name (string): names of volume
```

* List Volume
```
list(**kwargs):

This function list all volumes as following:
If NAME (volume name) is specified, it will print out info of NAME.
        If NAME (volume name) is not specified, it will print out info of all
          volumes under current cloud.
        If vm is specified, it will print out all the volumes attached to vm.
        If region(availability zone) is specified, it will print out
          all the volumes in that region.

Optional Parameters:

        NAME: name of volume
        vm: name of vm
        region: name of availability zone
```

* Attach Volume
```
attach(names,vm,dryrun=False):

This function attach one or more volumes to vm.  It returns self.list()
        to list the updated volume. The updated dict with "AttachedToVm" showing
        the name of vm where the volume attached to.

Required Parameters:
 
        names (string): names of volumes

        vm (string): name of vm
```

* Detach Volume
```
detach(name):

This function detach a volume from vm. It returns self.list() to list
the updated volume. The vm under "AttachedToVm" will be removed if
volume is successfully detached.

Required Parameters:
        name: name of volume to dettach
```

* Add Tags for Volume
```
add_tag(**kwargs):

This function add tag to a volume.
In aws Boto3, key for volume name is "Name". For example,
key="Name", value="user-volume-1".
It could also be used to rename or name a volume.
If NAME is not specified, then tag will be added to the last volume.

Required Parameters:

        NAME: name of volume
        key: name of tag
        value: value of tag
```

* Volume Status
```
status(name):

This function get volume status, such as "in-use", "available", "deleted"

Required Parameters:

        name (string): volume name
```

* Migrate Volume
```
migrate(**kwargs):

Migrate volume from one vm to another vm.

Required Parameters:

        NAME (string): the volume name

        vm (string): the vm name

        region (string): the availability zone
```

* Sync Volumes
```
sync(names):

sync contents of one volume to another volume

Required Parameters:

        names (list): list of volume names
```

### Google

* python api:   
  <http://googleapis.github.io/google-api-python-client/docs/dyn/compute_v1.html>
* REST api for compute disks documentation:   
  <https://cloud.google.com/compute/docs/reference/rest/v1/disks?hl=en_US>
* Documentation about volume cost:   
  <https://cloud.google.com/compute/disks-image-pricing>
* manual:   
  <https://cloud.google.com/docs>

#### Google volume management functions

In Google Cloud Platform (GCP), volumes are referred to as 'disks'.  There are 
regional disks, which replicate data between two zones in the same region, and 
zonal disks, which only store data in a single zone.  Currently, only management
functions for zonal disks are supported.

Also, the GCP project ID is required to be set in the configuration file.  In 
order to use multiple projects, copy the google section in the configuration 
file under each of the cloud, storage, and volume sections and create 
additional google sections named google2, google3, ... for each of the 
additional GCP projects.    

* Create volume

    ```
    create(self, **kwargs)
    
    Creates a persistent disk in the specified project using the data in the 
    request.
    
    Required Parameters for API function::
      project: project ID for the project in which the volume is being created
      zone: the zone in which the volume is being created
      body: a dictionary in which several parameters for the disk can be set 
            such as size, name, type, and description
    ```            

* List volumes

    Note: Even though only zonal disks are currently supported, it is possible 
    to get a list of disks in a specific zone by setting the argument 
    --region=zone
    
    ```
    cms volume list --region=us-central1-a
    ```  
   
    ```
    list(self, **kwargs)
    
    Retrieves an aggregated list of persistent disks with most recently created 
    disks listed first.
    
    Required Parameters for API function(vary by argument):
      For no arguments, NAMES, --vm, --cloud: 
        project: project ID for the project being worked in
      For argument --region:
        project: project ID for the project being worked in
        zone: zone from which to get list of disks
    ```   
 
* Delete volumes
  
  ```
  delete(self, name=None)
  
    Deletes the specified persistent disk.
    Deleting a disk removes its data permanently and is irreversible.
    
    Required Parameters for API function:
      project: project ID for the project in which the volume is located
      zone: the zone in which the volume is located
      disk: name of the disk to be deleted
    ```

* Attach volumes

  The disk being attached needs to located in the same zone as the virtual 
  machine.
  
  ```
  attach(self, names, vm=None)

    Attach one or more disks to an instance.  GCP requires that the
    instance be stopped when attaching a disk.  If the instance is running when 
    the attach function is called, the function will stop the instance and then 
    restart the instance after attaching the disk.
    
    Required Parameters for API function:
      project: project ID for the project in which the instance is located
      zone: the zone in which the instance is located
      instance: the name of the instance to attach the volume to
      body: a dictionary in which several parameters for the attahment can be 
            set such as the source of the disk to be attached and the 
            'deviceName' given to identify the disk once attached.  Keep the 
            'deviceName' the same as the name of the volume (this is important 
            for detach).
    ```
  
* Detach volumes
  
  ```
  detach(self, name=None)

    Detach a disk from all instances.  GCP requires that the instance be stopped
    when detaching a disk.  If the instance is running when the detach function 
    is called, the function will stop the instance and then restart the instance
    after detaching the disk.
    
    Required Parameters for API function:
      project: project ID for the project in which the instance is located
      zone: the zone in which the instance is located
      instance: the name of the instance to attach the volume to
      deviceName: name given to identify the disk when attached to the instance.
    ```

* Add a tag to a volume

  ```
  add_tag(self, **kwargs)
  
    Add a key:value label to the disk
    Unable to change the name of a disk in Google Cloud
  
    Required Parameters for API function:
      project: project ID for the project in which the volume is located
      zone: zone in which the volume is located
      resource: name of the volume
      body: dictionary containing the the keys 'labelFingerprint' and 'labels'.
            'labels' is the key:value pair to be added to the disk, while 
            an up-to-date 'labelFingerprint' hash is required to update the 
            labels
  ```

* Status of volume

  ```
  status(self, name=None)
  
    Get status of specified disk, such as 'READY'
    Calls self.list() to get disk info
  
    Required Parameters for API function:
      project: project ID for the project being worked in
  ```
  

### Azure

* Azure CLI:   
  <https://docs.microsoft.com/en-us/cli/azure/netappfiles/volume?view=azure-cli-latest#az-netappfiles-volume-create>
* REST:   
  <https://docs.microsoft.com/en-us/rest/api/netapp/volumes>

#### Azure volume management functions


Create Volume
```
create(**kwargs)

    Creates a disk in the specified location and resource group.

Required Parameters: 

        GROUP_NAME: The name of the resource group.
        LOCATION: The region in which to place the disk.
        DISK_NAME: The name of the disk.
        disk_size_gb: The size of the disk.
        creation_data: Information about the disk, including the create
        option. For this project, a create option of 'Empty' was used.

```

Delete Volume
```
delete(NAME)

    Deletes the specified disk. The volume cannot have be attached to a
    virtual machine.

    Warning: All data on the volume will be permanently lost when the volume is 
    deleted.

Required Parameters: 
        GROUP_NAME: The name of the resource group.
        LOCATION: The region in which to place the disk.
        DISK_NAME: The name of the disk.
```

List Volumes
```
list(**kwargs):
    Lists the disks in the specified resource group.

Required Parameters: 
        GROUP_NAME: The name of the resource group.       
```

Attach Volume
```
attach(NAMES,vm)
    Attaches the specified disk to the specified VM instance.

Required Parameters: 
        GROUP_NAME: The name of the resource group.
        LOCATION: The region in which to place the disk.
        DISK_NAME: The name of the disk.
        VM_NAME: The name of the vm to attach the disk to.
        lun: Logical unit number used to attach the disk to the vm. Any lun
        can only be used for one disk being attached to any given vm. All
        disks attached to any given vm must have a unique lun.
        create_option: Set to 'Attach'.
        id: ID of the disk.
```

Detach Volume
```
Detach(NAME)
    Detaches the specified disk from a VM instance.

Required Parameters: 
        GROUP_NAME: The name of the resource group.
        LOCATION: The region in which to place the disk.
        DISK_NAME: The name of the disk.
        VM_NAME: The name of the vm to attach the disk to.
        
```

Get Volume Status
```
Status(NAME)
    Gets the status of a disk, either attached or unattached.

Required Parameters: 
        GROUP_NAME: The name of the resource group.
        LOCATION: The region in which to place the disk.
        DISK_NAME: The name of the disk.
        
```

Get Volume Info
```
Info(NAME)
    Gets information about a disk.

Required Parameters: 
        GROUP_NAME: The name of the resource group.
        LOCATION: The region in which to place the disk.
        DISK_NAME: The name of the disk.
        
```

Add Tag to Volume
```
Add_tag(**kwargs)
    Tags a disk.

Required Parameters: 
        GROUP_NAME: The name of the resource group.
        LOCATION: The region in which to place the disk.
        DISK_NAME: The name of the disk.
        disk_size_gb: The size of the disk.
        creation_data: Information about the disk, including the create
        option. For this project, a create option of 'Empty' was used.
        tags: Tags to be added to the disk.
        
```


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
  
```
### Oracle

* API:   
  <https://docs.cloud.oracle.com/en-us/iaas/api/#/en/iaas/20160918/Volume/>
* OCI API:   
  <https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/core/client/oci.core.BlockstorageClient.html>

#### Oracle volume management functions

see:

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

* from Amazon EBS volume
 
    create a copy of EBS volume content into Amazon S3, and then migration could be done as follows:

  * Migrating from Amazon S3 to Google Cloud Storage

    <https://cloud.google.com/storage/docs/migrating#storage-list-buckets-s3-python>

    <https://github.com/adzerk/s3-to-google-cloud-storage-connector>

  * Migrating from Amazon S3 to Azure Blob Storage

    <https://github.com/Azure-for-Startups/Amazon-S3-to-Azure-Storage-demo/blob/master/README.md>

  * Migrating from Amazon S3 to OpenStack
  
  * Migrating from Amazon S3 to Oracle

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

{tests}


