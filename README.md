# Cloudmesh Volume Management



[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-volume.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-volume)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume)

[![image](https://img.shields.io/pypi/v/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-volume.svg)](https://github.com/TankerHQ/python-cloudmesh-volume/blob/master/LICENSE)

## Abstract

A simple abstraction layer to manage Cloud Volumes for AWS, Azure, Google, Openstack and Multipass

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

* volume register which
```
    volume register which
```

* volume register
```
    volume register [NAME]
                    [--cloud=CLOUD]
```

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
* volume status

    Retrieves status of last volume created on cloud and displays it.
```
    volume status [NAMES]
                  [--cloud=CLOUD]
```
* volume add
```
    volume add VM NAME
```

* volume remove
``` 
    volume remove VM NAME
```

* volume delete
```
    volume delete [NAME] 
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

* volume cost
    * Multicloud enhanced function including cost estimates and the actual cost accured

## Volume Providers

### Multipass

* <https://freshbrewed.science/ubuntu-multipass-part-deux/index.html>

#### Multipass volume management functions

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

### Oracle

* API:   
  <https://docs.cloud.oracle.com/en-us/iaas/api/#/en/iaas/20160918/Volume/>
* OCI CLI:   
  <https://docs.cloud.oracle.com/en-us/iaas/tools/oci-cli/2.9.3/oci_cli_docs/cmdref/bv/volume.html>

#### Oracle volume management functions

:o2: Add functions from provider with descriptions of required parameters


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

