###############################################################
# pytest -v --capture=no tests/test_volume_add_tag.py
###############################################################

import os
from time import sleep

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.volume.Provider import Provider

from cloudmesh.management.configuration.name import Name

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

key = variables['key']

#
# cms set cloud=aws
#
cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not not set")

name_generator = Name()
name_generator.set(f"test-{user}-volume-" + "{counter}")
name = str(name_generator)
provider = Provider(name=cloud)


@pytest.mark.incremental
class Test_provider_volume:
    def test_provider_volume_create(self):
        HEADING()
        os.system(f"cms volume list --cloud={cloud}")
        name_generator.incr()
        Benchmark.Start()
        params = {"NAME": name, 'size': None, 'volume_type': None,
                  'description': None, 'region': None, 'path': None}
        data = provider.create(**params)
        Benchmark.Stop()
        status = None
        if cloud == "openstack" or cloud == "google":
            for v in data:
                status = v['status']
        elif cloud == "oracle":
            for v in data:
                status = v['lifecycle_state']
        elif cloud == "aws" or cloud == "multipass":
            start_timeout = 360
            time = 0
            while time <= start_timeout:
                sleep(15)
                time += 15
                status = provider.status(name=name)[0]['State']
                if status == "available":
                    break
        elif cloud == "azure":
            status = provider.status(name=name)[0]['disk_state']
        assert status in ['available', 'AVAILABLE','PROVISIONING', 'READY', 'Unattached']

    def test_provider_volume_add_tag(self):
        HEADING()
        key = "key"
        key_value = "value"
        params = {"key": key, "value": key_value, 'NAME': name}
        Benchmark.Start()
        data = provider.add_tag(**params)
        Benchmark.Stop()
        for entry in data:
            if cloud == 'aws':
                tags = entry['cm']['tags']
                assert tags == [{'Key': key, 'Value': key_value}]
            elif cloud == 'multipass':
                tags = entry['tags']
                assert tags == [{key: key_value}]
