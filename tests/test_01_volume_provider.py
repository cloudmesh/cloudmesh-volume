###############################################################
# pytest -v --capture=no tests/test_01_volume_provider.py
###############################################################

# TODO: start this with cloud init, e.g, empty mongodb
# TODO: assertuons need to be added
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
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.Shell import Shell
import sys

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

key = variables['key']
# cms set key=

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

def Print(data):
    print(provider.Print(data=data, output='table', kind='vm'))

@pytest.mark.incremental
class Test_provider_volume:

    def test_cms_init(self):
        HEADING()
        Benchmark.Start()
        result = os.system(f"cms init")
        Benchmark.Stop()

    def test_cms_vm(self):
        HEADING()
        cmd = "cms vm boot"+" --name="+name
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "vm" in result

    def test_provider_volume_create(self):
        HEADING()
        os.system(f"cms volume list --cloud={cloud}")
        name_generator.incr()
        Benchmark.Start()
        params = {"NAME":name}
        data = provider.create(**params)
        Benchmark.Stop()
        if cloud =='aws1':
            start_timeout = 360
            time = 0
            while time <= start_timeout:
                sleep(5)
                time += 5
                status = provider.status(NAME=name)[0]['State']
                if status == "available":
                    break
        elif cloud == 'openstack' or cloud =='oracle':
            for v in data:
                print("v: ", v)
                status = v['status']
            assert status in ['available','STARTING', 'RUNNING','ACTIVE']

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
        vm = variables['vm']
        Benchmark.Start()
        NAMES = []
        NAMES.append(name)
        provider.attach(NAMES=NAMES,vm=name)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            status = provider.status(NAME=NAMES[0])[0]['status']
            #In case of Oracle, status is AVAILABLE after attach
            if status in ['in-use','AVAILABLE']:
                break
        assert status in ['in-use','AVAILABLE']

    def test_provider_volume_detach(self):
        # test detach one volume
        # os.system("cms volume detach {name} ")
        HEADING()
        Benchmark.Start()
        provider.detach(NAME=name)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            status = provider.status(NAME=name)[0]['status']
            if status in ['available','AVAILABLE']:
                break
        assert status in ['available','AVAILABLE']

    def test_provider_volume_delete(self):
        HEADING()
        Benchmark.Start()
        provider.delete(NAME=name)
        Benchmark.Stop()
        result = provider.info(name=name)
        assert result is None

    def test_cms_terminate(self):
        HEADING()
        cmd = "cms vm terminate"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "vm" in result

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)

