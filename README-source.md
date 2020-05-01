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

## API documentation 

The complete documentation of volume API is available at
 
* <https://cloudmesh.github.io/cloudmesh-manual/api/cloudmesh.volume.html>

## Installation

### Users

The user can install cloudmesh volume with

```bash
pip install cloudmesh-volume
```

### Developers

Developers want the source code and do the development in the
directory. We use the `cloudmesh-installer` to do this. Make sure you
use a virtual environment such as ~/ENV3. We recommend using python
3.8.2

* See also: <https://github.com/cloudmesh/cloudmesh-installer>

```bash
mkdir cm
cd cm
pip install cloudmesh-installer -U
cloudmesh-installer get volume
```

In case you need to reinstall the venv you can use

cloudmesh-installer new ~/ENV3 storage --python=python3.8

PLease note to use the python program for your system. This may be
different.

## Users Guide

* Create Volume

To create a new volume.
For multipass, creates a directory, volume region means path of the directory, i.e.
    "/Users/username/multipass"
For aws, creates EBS volume in EC2 service, volume region means availability zone.
For azure, creates disk, volume region means location.
For google, creates zonal disks, volume region means zone of volume.
For oracle, creates volume in block-storage service, volume region means availability_domain.
For openstack, creates volume, volume region means zone.

Example 1: To create a volume with default parameters and generated name:

```commandline
cms volume create
```

Example 2: To create a test_volume of 100 GB in us-east-2a:

```commandline
cms volume create test_volume --size=100 --region=us-east-2a
```

* List Volume

To list volumes. 

If volume name or names are not given and refresh is True, return the 
    information of volume through the cloud.
If volume name or names are not given and refresh is False, return the 
    information of volume through database.
If volume name or names are given, return the information of volume through the 
    cloud.
If vm is specified, it will print out all the volumes attached to vm.
If region(zone) is specified, it will print out all the volumes in that zone.

Please check following table about available functions for each cloud service:

|   |List with Refresh|List without Refresh|List One Volume |List Multiple Volumes|List by Region|List by vm|
|---------------|-------|-----|-----|---|---|---|
| AWS | * |* |*|*|*|*|
| Azure |* | |*|*|
| Google |*|*|*|*|*|*|
| Multipass| |*|*|*|*|*|
|Openstack|*|*|*|*|||
|Oracle|*|*|*|*  |

Example 1: To return the information of volume through current cloud provider.

```commandline
cms volume list --refresh
```
Example 2: To return the information of test_volume1 and test_volume2 through 
    openstack cloud provider.

```commandline
cms volume list test_volume1,test_volume2 --cloud=openstack
```

* Delete Volume

To delete volume or volumes from multiple cloud providers permanently and is 
irreversible. Make sure volume is not attached to any vm before running delete command.
The volume will be updated in the database with status set to
'deleted'. All data on the volume will be permanently lost when the volume
is deleted. (Use purge to remove deleted volumes from database) 

Example 1: To delete current volume

```commandline
cms volume delete
``` 

Example 2: To delete test_volume1,test_volume2

```commandline
cms volume delete test_volume1,test_volume2
``` 

* Attach Volume

To attach one or more volumes to a vm. 
The volume being attached needs to be located in the same zone as the vm.
For aws, a vm can have multiple attached volumes.
GCP (google) requires that the instance be stopped when attaching a disk. 
If the instance is running when the attach function is called, the function will 
stop the instance and then restart the instance after attaching the disk.

Please check following table for available functions for each cloud service:

|   |Attach One Volume|Attach Multiple Volumes|
|---------------|-------|-----|
| AWS | * |* |
| Azure |* | |
| Google |*|*|
| Multipass|*|*|
|Openstack|*|
|Oracle|*|

Example 1: To attach test_volume1 to test_vm

```commandline
cms volume attach test_volume1 --vm=test_vm
``` 

* Detach Volume

To detach volume or volumes from all vm.
GCP (google) requires that the instance be stopped when detaching a disk.  
If the instance is running when the detach function is called, 
the function will stop the instance and then restart the instance after 
detaching the disk.

Example 1: To detach current volume from vm

```commandline
cms volume detach
``` 

* Volume Status

To return status of volume, such as "available", "in-use" and etc.

Example 1: To return test_volume information with status.

```commandline
cms volume status test_volume
```

* Migrate Volume

To migrate volume to vm in the same cloud service, 
if no given volume, migrate the current volume. Implemented in aws and 
multipass.

Example 1: To migrate test_volume volume to test_vm in the aws cloud service

```commandline
cms volume migrate test_volume --vm=test_vm --cloud=aws
```

* Sync Volume

To sync first volume with second volume in the same cloud service.
When len(NAMES)==2, sync volume (NAMES[0]) with volume (NAMES[1])
When len(NAMES)==1, sync current volume with volume(NAMES[0])
Implemented in aws and multipass.

Example 1: To sync test_volume1 with test_volume2 in aws cloud provider.

```commandline
cms volume sync test_volume1,test_volume2 --cloud=aws
```

* Add Tags to Volume

Add tag to a volume.
If name is not specified, then tag will be added to the current volume.
For aws, can use add_tag command to rename a volume.

Example 1: To add tag {key:value} to test_volume.

```commandline
cms volume add_tag test_volume --key=key --value=value
```

Example 2: To rename aws test_volume into new_name.

```commandline
cms volume add_tag test_volume --key=Name --value=new_name
```

## Volume Providers

### Multipass

* <https://freshbrewed.science/ubuntu-multipass-part-deux/index.html>

### AWS

In AWS, volume is EBS volume in EC2 services.

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

### Google

In Google Cloud Platform (GCP), volumes are referred to as 'disks'.  There are 
regional disks, which replicate data between two zones in the same region, and 
zonal disks, which only store data in a single zone.  Currently, only management
functions for zonal disks are supported.

Also, the GCP project ID is required to be set in the configuration file.  In 
order to use multiple projects, copy the google section in the configuration 
file under each of the cloud, storage, and volume sections and create 
additional google sections named google2, google3, ... for each of the 
additional GCP projects.

* python api:   
  <http://googleapis.github.io/google-api-python-client/docs/dyn/compute_v1.html>
* REST api for compute disks documentation:   
  <https://cloud.google.com/compute/docs/reference/rest/v1/disks?hl=en_US>
* Documentation about volume cost:   
  <https://cloud.google.com/compute/disks-image-pricing>
* manual:   
  <https://cloud.google.com/docs>  

### Azure

Similar to Google, in Azure, volumes are referred to as 'disks'.

* Disk Operations:
  <https://docs.microsoft.com/en-us/python/api/azure-mgmt-compute/azure.mgmt
   .compute.v2019_11_01.operations.disksoperations?view=azure-python>
* Azure CLI:   
  <https://docs.microsoft.com/en-us/cli/azure/netappfiles/volume?view=azure-cli-latest#az-netappfiles-volume-create>
* REST:   
  <https://docs.microsoft.com/en-us/rest/api/netapp/volumes>

### OpenStack

* python:   
  <https://docs.openstack.org/python-cinderclient/latest/>
* REST:   
  <https://docs.openstack.org/api-ref/block-storage/>
* <https://docs.openstack.org/python-openstackclient/pike/cli/command-objects/volume.html>

### Oracle

* API:   
  <https://docs.cloud.oracle.com/en-us/iaas/api/#/en/iaas/20160918/Volume/>
* OCI API:   
  <https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/core/client/oci.core.
  BlockstorageClient.html>

## Documentation about migration between cloud providers 

* from Amazon EBS volume
 
    Create a copy of EBS volume content into Amazon S3, and then migration could 
    be done by cloudmesh storage service, please refer to
     <https://cloudmesh.github.io/cloudmesh-manual/api/cloudmesh.storage.html>.
     
     Here are some documentation about migrating Amazon S3 to other cloud services:

  * Migrating from Amazon S3 to Google Cloud Storage

    <https://cloud.google.com/storage/docs/migrating#storage-list-buckets-s3-python>

    <https://github.com/adzerk/s3-to-google-cloud-storage-connector>

  * Migrating from Amazon S3 to Azure Blob Storage

    <https://github.com/Azure-for-Startups/Amazon-S3-to-Azure-Storage-demo/blob/master/README.md>

* from Cloud Storage

  * Migrating from Cloud Storage to Amazon S3

    <https://www.quora.com/How-can-I-migrate-data-from-Google-cloud-storage-into-AWS-S3-buckets>

  * Migrating from Cloud Storage to Azure Blob Storage

    <https://blog.bitscry.com/2019/12/30/data-transfer-google-cloud-storage-to-azure-blob-storage/>

## Test cases

{tests}


