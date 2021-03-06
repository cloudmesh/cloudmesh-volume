###############################################################
# pytest -v --capture=no tests/test_02_volume_provider.py
###############################################################

# TODO: assertuons need to be added

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
# cms set cloud=openstack
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
        assert status in ['available', 'AVAILABLE', 'PROVISIONING', 'READY',
                          'Unattached']

    def test_provider_volume_list(self):
        HEADING()
        Benchmark.Start()
        params = {}
        data = provider.list(**params)
        assert len(data) > 0
        Benchmark.Stop()

    def test_provider_volume_attach(self):
        # test attach one volume to vm
        # os.system("cms volume attach {name} --vm={vm}")
        HEADING()
        Benchmark.Start()
        names = []
        names.append(name)
        provider.attach(names=names, vm=variables.__getitem__("vm_name"))
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            if cloud == "oracle":
                status = provider.status(name=names[0])[0]['lifecycle_state']
            if cloud == "openstack":
                status = provider.status(name=names[0])[0]['status']
            elif cloud == "aws" or cloud == "multipass":
                status = provider.status(name=name)[0]['State']
            elif cloud == "azure":
                status = provider.status(name=name)[0]["disk_state"]
            elif cloud == "google":
                status = provider.status(name=name)[0]['status']
            # In case of Oracle, status is AVAILABLE after attach
            if status in ['in-use', 'AVAILABLE', 'READY', "Attached"]:
                break
        assert status in ['in-use', 'AVAILABLE', 'READY', "Attached"]

    def test_provider_volume_detach(self):
        # test detach one volume
        # os.system("cms volume detach {name} ")
        HEADING()
        Benchmark.Start()
        provider.detach(name=name)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            if cloud == "oracle":
                status = provider.status(name=name)[0]['lifecycle_state']
            if cloud == "openstack":
                status = provider.status(name=name)[0]['status']
            elif cloud == "aws" or cloud == "multipass":
                status = provider.status(name=name)[0]['State']
            elif cloud == "azure":
                status = provider.status(name=name)[0]["disk_state"]
            elif cloud == "google":
                status = provider.status(name=name)[0]['status']
            if status in ['available', 'AVAILABLE', 'READY', "Unattached"]:
                break
        assert status in ['available', 'AVAILABLE', 'READY', "Unattached"]

    def test_provider_volume_delete(self):
        HEADING()
        Benchmark.Start()
        provider.delete(name=name)
        Benchmark.Stop()
        result = provider.info(name=name)
        if cloud == 'oracle':
            status = result['lifecycle_state']
            assert status in ['TERMINATED']
        elif cloud == 'multipass':
            status = result['State']
            assert status in ['deleted']
        else:
            assert result is None

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
