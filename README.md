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

volume migrate - xin
```
by professor's notes:
There could be multiple meanings of migrate, e.g. between regions, between volumes, between clouds
we also want to have a sync. Lets assume i have a volume on a and b I like some mechanism to syncthe volumes.
Also the cost function is done by everyone.
there could also be migrate between services on the same cloud. AWS has a flood of storage solutions which we may need to evaluate.
```

volume set - ashley

volume show - ashley

We all can look into these two methods

volume unset

Multicloud enhanced function including cost estimates and the actual cost accured

4. Write test cases for all above methods

5. distribution of work

     Azure - Ashok and Xin
     
     AWS - Ashley and Xin
     
     Google - Ashley and Xin
     
     Openstack - Ashok and Ashley
     
     Multipass - Ashok and Ashley (edited) 
     
* <https://cloudmesh.github.io/cloudmesh-manual/>

This command implements volume management for clouds

