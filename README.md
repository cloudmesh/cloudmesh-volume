# Cloudmesh Volume Management



[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-volume.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-volume)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume)

[![image](https://img.shields.io/pypi/v/cloudmesh-volume.svg)](https://pypi.org/project/cloudmesh-volume/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-volume.svg)](https://github.com/TankerHQ/python-cloudmesh-volume/blob/master/LICENSE)

1. Project proposal file name and location:

     name: volume-management.md
     
     location: https://github.com/cloudmesh/cloudmesh-volume/blob/master/README.md
     
2. Create complete manual page ( may be this is readme file in git?)

3. Methods to implement: Write brief summary of each method and arguments it can take

volume create - ashok

volume delete - ashok

volume list - xin

* list volumes for a virtural machine

        --name of vm

* list volumes in the same region

        --name of region

* list volumes in the same cloud

        --name of cloud

volume migrate - xin

* volume migrate between regions
        
        --region name A
        
        --region name B
        
        --volume name

* volume migrate between vms

        --vm name A
        
        --vm name B
        
        --volume name

* volume migrate between clouds
        
        --cloud name of A
        
        --cloud name of B
        
        --volume name
        
* volume migrate between services on the same cloud
        
        --cloud name
        
        --service name of A
        
        --service name of B
        
        --volume name

volume sync

* volume sync between volumes 
        
        --volume name of A
        
        --volume name of B

volume set - ashley

volume show - ashley

We all can look into these two methods

volume unset

volume cost

* Multicloud enhanced function including cost estimates and the actual cost accured

4. Write test cases for all above methods

5. distribution of work

     Azure - Ashok and Xin
     
     AWS - Ashley and Xin
     
     Google - Ashley and Xin
     
     Openstack - Ashok and Ashley
     
     Multipass - Ashok and Ashley (edited) 
     
* <https://cloudmesh.github.io/cloudmesh-manual/>

This command implements volume management for clouds

