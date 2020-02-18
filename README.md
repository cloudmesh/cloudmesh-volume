# Cloudmesh Volume Management



[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-volume.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-volume)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume)

[![image](https://img.shields.io/pypi/v/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-volume.svg)](https://github.com/TankerHQ/python-cloudmesh-volume/blob/master/LICENSE)

## Abstract

A simple abstraction layer to manage Cloud Volumes for AWS, Azure, Google, Openstack and Multipass

In this project we will be developing features related to completing and simplifying the volume management interface to an existing cloud. We will also benchmark the clouds while comparing the volume management functions that are deployed on different clouds.

## Team memebers

* Xin Gu sp20-516-227
* Ashley Thornton sp20-516-230
* Ashok Singam sp20-516-232

## Volume Management functions

* Volume create - Create new volume - Ashok
* Volume delete - Delete volumes - Ashok

* Volume list - List volumes - Xin
```
    volume list [VM NAME]
                [--region=REGION]
                [--cloud=CLOUD]
                [--refresh]
```
    
* Volume migrate - Migrate volume to a new host - Xin
```
    volume migrate [VOLUME NAME]
                    [--fregion=FROM REGION]
                    [--tregion=TO REGION]
                    [--fservice=FROM SERVICE]
                    [--tservice=TO SERVICE]
                    [--fcloud=FROM CLOUD]
                    [--tcloud=TO CLOUD]
                    [--cloud=CLOUD]
                    [--region=REGION]
                    [--service=SERVICE] 
```

* volume sync
```
    volume sync [VOLUME NAME A] [VOLUME NAME B]
                    [--region=REGION]
                    [--cloud=CLOUD]
```
                  
* Volume set - Set volume properties - Ashley
* Volume show - Show volume details - Ashley
* Volume unset - Unset volume properties - Ashley
* volume cost
    * Multicloud enhanced function including cost estimates and the actual cost accured - All

Volume Providers:

* AWS:

    python api: 
    
    <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>
    
    REST api: 
    
    <https://docs.aws.amazon.com/apigateway/api-reference/>
    
    Documentation about volume cost: 
    
    <https://aws.amazon.com/ebs/pricing/>
    
    <https://medium.com/@stefanroman/calculate-price-of-ebs-volumes-with-python-76687bb24530>
    
    manual: 
    
    <https://docs.aws.amazon.com/>

* Google:

    python api: 
    
    <https://cloud.google.com/sdk>
    
    REST api: 
    
    <https://cloud.google.com/apis/docs/overview>
    
    Documentation about volume cost: 
    
    <https://cloud.google.com/compute/disks-image-pricing>
    
    manual: 
    
    <https://cloud.google.com/docs>

* Azure:

* OpenStack

* Documentation on how to move volumes from one provider to the next: 

    * from Amazon S3
    
        * Migrating from Amazon S3 to Cloud Storage
        
        https://cloud.google.com/storage/docs/migrating#storage-list-buckets-s3-python
        
        https://github.com/adzerk/s3-to-google-cloud-storage-connector
        
        * Migrating from Amazon S3 to Azure Blob Storage
        
        https://github.com/Azure-for-Startups/Amazon-S3-to-Azure-Storage-demo/blob/master/README.md
        
        * Migrating from Amazon S3 to OpenStack
        
    * from Cloud Storage
    
        * Migrating from Cloud Storage to Amazon S3
        
        https://www.quora.com/How-can-I-migrate-data-from-Google-cloud-storage-into-AWS-S3-buckets
        
        * Migrating from Cloud Storage to Azure Blob Storage
        
        https://blog.bitscry.com/2019/12/30/data-transfer-google-cloud-storage-to-azure-blob-storage/
        
        * Migrating from Cloud Storage to OpenStack
        
    * from Azure Blob Storage
        
        * Migrating from Azure Blob Storage to Amazon S3
        
        * Migrating from Azure Blob Storage to Cloud Storage
        
        * Migrating from Azure Blob Storage to OpenStack
        
    * from OpenStack

## Test cases

Write test cases in the form of reproducable pytests

## Distribution of clouds between team memebers

* Azure - Ashok and Xin
* AWS - Ashley and Xin
* Google - Ashley and Xin
* Openstack - Ashok and Ashley
* Multipass - Ashok and Ashley 
     
## <https://cloudmesh.github.io/cloudmesh-manual/>

