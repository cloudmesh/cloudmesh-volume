###############################################################
# pytest -v --capture=no tests/test_volume_aws.py
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


# current_vms = 0


@pytest.mark.incremental
class Test_provider_volume:

    def find_counter(self):
        name = str(Name())
        # print(name)
        volumes = provider.list()
        # print(f'Volumes is {volumes}')
        if volumes is not None:
            numbers = []
            names = []
            for volume in volumes:
                names.append(volume['cm']['name'])
                numbers.append(int(volume['cm']['name'].rsplit("-", 1)[1]))
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
        name = str(name_generator)
        os.system(f"cms volume create {name}")
        name_generator.incr()
        name2 = str(name_generator)
        names.append(name2)
        params = {"cloud": cloud, "NAME": name2}
        Benchmark.Start()
        data = provider.create(**params)
        Benchmark.Stop()
        VERBOSE(data)
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            status = provider.status(NAME=name)[0]['State']
            if status == "available":
                break
        # for entry in data:
        #     status = entry['State']
        assert status =='available'

    def test_provider_volume_addtag(self):
        HEADING()
        name_generator.incr()
        name3 = str(name_generator)
        key = "Name"
        key_value = name3
        #os.system(f"cms volume add_tag {name} --key={key} --value={key_value}")
        params = {"key": key, "value": key_value}
        Benchmark.Start()
        data = provider.add_tag(NAME=name, **params)
        Benchmark.Stop()
        names.append(name3)
        VERBOSE(data)
        for entry in data:
            value_name = entry['cm']['name']
        assert value_name == key_value

    def test_provider_volume_list(self):
        HEADING()
        # os.system("cms volume list")
        # os.system("cms volume list --cloud=aws1")
        params = {"cloud": cloud,}
        Benchmark.Start()
        data = provider.list(**params)
        Benchmark.Stop()
        Print(data)
        assert len(data) >= 0

    def test_provider_volume_list_names(self):
        HEADING()
        # os.system("cms volume list NAMES")
        # os.system("cms volume list NAMES --cloud=aws1")
        params = {"cloud": cloud, "NAMES": names}
        Benchmark.Start()
        data = provider.list(**params)
        Benchmark.Stop()
        Print(data)
        assert len(data) >= 2

    #
    # start a vm, save vm in variables
    #

    def test_provider_volume_attach(self):
        # test attach one volume to vm
        # os.system("cms volume attach {name} --vm={vm}")
        HEADING()
        vm = variables['vm']
        name = str(name_generator)
        Benchmark.Start()
        data = provider.attach(NAMES=[name], vm=vm)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            status = provider.status(NAME=name)[0]['State']
            if status == "in-use":
                break
            # for entry in data:
            #     attached = entry["AttachedToVm"]
            #     if vm in attached:
            #         break
        VERBOSE(data)
        #assert vm in attached
        assert status == "in-use"

    def test_provider_volume_detach(self):
        # test detach the most recent volume
        HEADING()
        vm = variables['vm']
        name = str(Name())
        print("name: ", name)
        Benchmark.Start()
        data = provider.detach(NAME=name)
        Benchmark.Stop()
        stop_timeout = 360
        time = 0
        while time <= stop_timeout:
            sleep(5)
            time += 5
            status = provider.status(NAME=name)[0]['State']
            if status == "available":
                break
            # for entry in data:
            #     attached = entry["AttachedToVm"]
            #     if vm not in attached:
            #         break
        VERBOSE(data)
        assert status == "available"

    def test_provider_volume_attach_multi(self):
        # test attach multiple volumes to vm
        HEADING()
        # os.system("cms volume attach {names} --vm={vm}")
        vm = variables['vm']
        Benchmark.Start()
        data = provider.attach(names, vm)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        count = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            if count >= len(names):
                break
            for name in names:
                for entry in data:
                    if entry['cm']['name'] == name and entry["AttachedToVm"] == [vm]:
                        count += 1
        VERBOSE(data)
        assert count >= len(names)

    def test_provider_volume_list_vm(self):
        HEADING()
        vm = variables['vm']
        # os.system(f"cms volume list --vm={vm}")
        params = {"cloud": cloud, "vm": vm}
        Benchmark.Start()
        data = provider.list(**params)
        Benchmark.Stop()
        Print(data)
        assert len(data) >= 0


    def test_provider_volume_delete(self):
        # test delete given one volume name and cloud
        #os.system(f"cms volume delete {name}")
        name = str(Name())
        provider.detach(NAME=name)
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(5)
            time += 5
            status = provider.status(NAME=name)[0]['State']
            if status == "available":
                break

        HEADING()
        params = {"NAME": name}
        Benchmark.Start()
        provider.delete(NAME=name)
        Benchmark.Stop()
        assert provider.list(**params) == []

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)

