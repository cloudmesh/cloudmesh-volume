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

## Test cases

Write test cases in the form of reproducable pytests

## Distribution of clouds between team memebers

* Azure - Ashok and Xin
* AWS - Ashley and Xin
* Google - Ashley and Xin
* Openstack - Ashok and Ashley

  * python: <https://docs.openstack.org/python-cinderclient/latest/>
  * REST: <https://docs.openstack.org/api-ref/block-storage/>
  
* Multipass - Ashok and Ashley 
     
## <https://cloudmesh.github.io/cloudmesh-manual/>

