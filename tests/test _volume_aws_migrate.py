###############################################################
# pytest -v --capture=no tests/test_volume_aws_migrate.py
###############################################################

from pprint import pprint

import pytest
import os
from time import sleep
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.volume.Provider import Provider
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

#
# cms set cloud=aws1
#

cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")

name_generator = Name()
name_generator.set(f"test-{user}-volume-" + "{counter}")

name = str(name_generator)
names = []
provider = Provider(name=cloud)


def Print(data):
    print(provider.Print(data=data, output='table', kind='volume'))

# TODO:
# 1.start two vm in two different zone, one in default zone (us-east-2a), one
#       in other zone (us-east-2c)
# 2.create 1 new volume in default zone
# 3. run migrate given --vm and --cloud (volume name will be the latest created
#       volume)
