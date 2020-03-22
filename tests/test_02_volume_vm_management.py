###############################################################
# pytest -v --capture=no tests/cloud/test_01_volume_provider.py
# pytest -v  tests/cloud/test_01_volume_provider.py
# pytest -v --capture=no  tests/cloud/test_01_volume_provider..py::Test_provider_volume.METHODNAME
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
# cms set volume=aws
#
cloud = variables.parameter('volume')

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
        print(name)
        vms = provider.list()
        print(f'VM is {vms}')
        if vms is not None:
            numbers = []
            names = []
            for vm in vms:
                names.append(vm['name'])
                numbers.append(int(vm['name'].rsplit("-", 1)[1]))
            numbers.sort()
            return numbers[-1]

    def test_find_largest_id(self):
        name = Name()
        counter = 1
        if self.find_counter() is not None:
            counter = {"counter": self.find_counter()}
            name.assign(counter)
        else:
            name.assign(counter)

    def test_provider_volume_create(self):
        HEADING()
        os.system(f"cms volume list --cloud={cloud}")
        name_generator.incr()

        Benchmark.Start()
        data = provider.create(key=key)
        Benchmark.Stop()

        # print(data)
        VERBOSE(data)
        name = str(Name())
        status = provider.status(name=name)[0]
        print(f'status: {str(status)}')
        if cloud == 'oracle':
            assert status["cm.status"] in ['STARTING', 'RUNNING', 'STOPPING',
                                           'STOPPED']
        else:
            assert status["cm.status"] in ['ACTIVE', 'BOOTING', 'TERMINATED',
                                           'STOPPED']

    def test_provider_volumeprovider_volume_list(self):
        # list should be after create() since it would return empty and
        # len(data) would be 0
        HEADING()
        Benchmark.Start()
        data = provider.list()
        assert len(data) > 0
        Benchmark.Stop()
        Print(data)


    def test_provider_volume_info(self):
        # This is just a dry run, status test actually uses info() in all
        # provider
        HEADING()
        Benchmark.Start()
        name = str(Name())
        data = provider.info(name=name)
        print("dry run info():")
        pprint(data)
        Benchmark.Stop()

    def test_volume_status(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.status(name=name)
        if type(data) == list:
            data = data[0]
        print(data)
        Benchmark.Stop()
        if cloud == 'oracle':
            assert data["cm.status"] in ['STARTING', 'RUNNING', 'STOPPING',
                                         'STOPPED']
        else:
            assert data["cm.status"] in ['ACTIVE', 'BOOTING', 'TERMINATED',
                                         'STOPPED']


    def test_provider_volume_destroy(self):
        HEADING()
        name = str(Name())
        Benchmark.Start()
        data = provider.destroy(name=name)
        Benchmark.Stop()

        pprint(data)

        result = provider.info(name=name)
        assert result is None

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
