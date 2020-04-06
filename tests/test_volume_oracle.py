###############################################################
# pytest -v --capture=no tests/test_volume_oracle.py
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
import sys

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

key = variables['key']

#
# cms set cloud=oracle
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


current_vms = 0


@pytest.mark.incremental
class Test_provider_volume:

    def find_counter(self):
        name = str(Name())
        #print(name)
        vms = provider.list(**params)
        if vms is not None:
            numbers = []
            names = []
            for vm in vms:
                names.append(vm['name'])
                numbers.append(int(vm['name'].rsplit("-", 1)[1]))
            numbers.sort()
            return numbers[-1]

    def test_provider_volume_create(self):
        HEADING()
        os.system(f"cms volume list --cloud={cloud}")
        name_generator.incr()
        Benchmark.Start()
        params = {"NAME": name}
        data = provider.create(**params)
        Benchmark.Stop()
        for v in data:
            status = v['lifecycle_state']
        assert status in ['AVAILABLE','PROVISIONING']

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
        result = provider.attach(NAMES=NAMES, vm=vm)
        Benchmark.Stop()
        status = provider.status(NAME=NAMES[0])
        # TODO: Volume status is not changing in Oracle after attaching
        # a volume to an instance. It is still AVAILABLE
        assert status == "AVAILABLE"

    def test_provider_volume_detach(self):
        # test detach one volume to vm
        # os.system("cms volume detach {name} --vm={vm}")
        HEADING()
        vm = variables['vm']
        Benchmark.Start()
        result = provider.detach(NAME=name)
        Benchmark.Stop()
        status = provider.status(NAME=name)
        # TODO: Volume status is always AVAILABLE
        assert status == "AVAILABLE"

    def test_provider_volume_delete(self):
        HEADING()
        Benchmark.Start()
        provider.delete(NAME=name)
        Benchmark.Stop()
        status = provider.status(NAME=name)
        assert status == "TERMINATED"

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)

