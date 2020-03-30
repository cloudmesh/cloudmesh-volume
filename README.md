# Cloudmesh Volume Management



[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-volume.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-volume)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume)

[![image](https://img.shields.io/pypi/v/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-volume.svg)](https://github.com/TankerHQ/python-cloudmesh-volume/blob/master/LICENSE)

## Abstract

A simple abstraction layer to manage Cloud Volumes for AWS, Azure, Google, Openstack, Oracle and Multipass

In this project we will be developing features related to completing and simplifying the volume management interface to an existing cloud. We will also benchmark the clouds while comparing the volume management functions that are deployed on different clouds.

## Team members

* Peter McCandless sp20-516-222
* Xin Gu sp20-516-227
* Ashley Thornton sp20-516-230
* Ashok Singam sp20-516-232

## Distribution of clouds between team memebers

* Azure - Ashley & Xin
* AWS - Ashley & Xin
* Google - Peter & Xin
* Oracle - Ashok & Peter
* Openstack - Peter & Ashok
* Multipass - Ashok & Ashley

## Volume Management functions

* volume list
  
  List all the volumes for certain vm, region, or cloud. 
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
```
    volume create [NAME]
                  [--size=SIZE]
                  [--volume_type=TYPE]
                  [--description=DESCRIPTION]
                  [--dryrun]
```

* volume attach

    attatch volume to a vm
```
    volume attach [NAME]
                  [--vm=VM]

```

* volume detach

    detatch volumes from vms
``` 
    volume detach [NAME]  
```

* volume delete

    delete volumes
```
    volume delete [NAMES] 
```
    
* volume migrate
  
  Migrate volume from one vm to another vm between different regions, services or providers.
```
    volume migrate NAME FROM_VM TO_VM
```

* volume sync
  
  Volume sync alows for data to shared bewteen two volumes.
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

transfer(self, name="cloudmesh", source=None, destination=None, recursive=True):
```
Copies files or entire directories into the vm

Required Parameters: 

        source --
    
            The name of source (volume?)

        destination --

            The name of vm???
```

:o2: Add functions from provider with descriptions of required parameters

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

create_volume(**kwargs)
```
Creates an EBS volume that can be attached to an instance in the same Availability Zone. 

Required Parameters: 

        AvailabilityZone (string) -- 

            The Availability Zone in which to create the volume.
```

describe_volumes(**kwargs)
```
Describes the specified EBS volumes or all of your EBS volumes.
```

delete_volume(**kwargs)
```
Deletes the specified EBS volume. The volume must be in the available state (not attached to an instance).

Required Parameters: 

        VolumeId (string) --

            The ID of the volume.
```

attach_volume(**kwargs)
```
Attaches an EBS volume to a running or stopped instance and exposes it to the instance with the specified device name.

Required Parameters:

        Device (string) --

            The device name (for example, /dev/sdh or xvdh ).

        InstanceId (string) --

            The ID of the instance.

        VolumeId (string) --

            The ID of the volume.
```

detach_volume(**kwargs)
```
Detaches an EBS volume from an instance.

Required Parameters:

        VolumeId (string) --

            The ID of the volume.
```

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
    Create Volume Creates a new volume in the specified compartment. Volumes can
be created in sizes ranging from 50GB to 32 TB, in 1 GB (1024 MB) increments. 
By default, volumes are 50GB.

Required Parameters: 
        availability_domain: The availability domain of the volume
                             Example: Uocm:PHX-AD-1
        compartment_id: The OCID of the compartment that contains the volume
           
```

Delete Volume
```
delete(name)
    Deletes the specified volume. The volume cannot have an active connection to an instance.
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

* from Amazon S3

  * Migrating from Amazon S3 to Cloud Storage

    <https://cloud.google.com/storage/docs/migrating#storage-list-buckets-s3-python>

    <https://github.com/adzerk/s3-to-google-cloud-storage-connector>

  * Migrating from Amazon S3 to Azure Blob Storage

    <https://github.com/Azure-for-Startups/Amazon-S3-to-Azure-Storage-demo/blob/master/README.md>

  * Migrating from Amazon S3 to OpenStack

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

