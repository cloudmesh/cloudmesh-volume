# Cloudmesh Volume Management



[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-volume.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-volume)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume)

[![image](https://img.shields.io/pypi/v/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-volume.svg)](https://github.com/TankerHQ/python-cloudmesh-volume/blob/master/LICENSE)

A simple abstraction layer to manage Cloud Volumes for AWS, Azure, Google, Openstack and Multipass

In this project we will be developing features related to completing and simplifying the volume management interface to an existing cloud. We will also benchmark the clouds while comparing the volume management functions that are deployed on different clouds.

## Team memebers

* Xin Gu sp20-516-227
* Ashley Tomton sp20-516-230
* Ashok Singam sp20-516-232


## Volume Management functions

* Volume create - Create new volume - Ashok
* Volume delete - Delete volumes - Ashok
* Volume list - List volumes - Xin
* Volume migrate - Migrate volume to a new host - Xin
* Volume migrate - xin
```
Professor's notes:
There could be multiple meanings of migrate, e.g. between regions, between volumes, between clouds
we also want to have a sync. Lets assume i have a volume on a and b I like some mechanism to syncthe volumes.
Also the cost function is done by everyone. There could also be migrate between services on the same cloud. AWS has a flood of storage solutions which we may need to evaluate.
```
* Volume set - Set volume properties - Ashley
* Volume show - Show volume details - Ashley
* Volume unset - Unset volume properties - Ashley
* Multicloud enhanced function including cost estimates and the actual cost accured - All

## Write test cases for all above methods

Write test cases in the form of reproducable pytests

## Distribution of clouds between team memebers

* Azure - Ashok and Xin
* AWS - Ashley and Xin
* Google - Ashley and Xin
* Openstack - Ashok and Ashley
* Multipass - Ashok and Ashley 
     
## <https://cloudmesh.github.io/cloudmesh-manual/>

