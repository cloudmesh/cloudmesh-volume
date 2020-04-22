###############################################################
# pytest -v --capture=no tests/test_01_setup.py
###############################################################

# TODO: start this with cloud init, e.g, empty mongodb
# TODO: assertuons need to be added

import pytest
import json
import os
from time import sleep
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
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
    raise ValueError("cloud is not set")

name_generator = Name()
name_generator.set(f"test-{user}-volume-" + "{counter}")

name = str(name_generator)
variables.__setitem__("vm_name", name)

provider = Provider(name=cloud)
current_vms = 0




@pytest.mark.incremental
class Test_provider_volume:

    # def test_cms_init(self):
    #     HEADING()
    #     Benchmark.Start()
    #     result = os.system(f"cms init")
    #     Benchmark.Stop()

    def test_cms_vm(self):
        HEADING()
        if cloud=="multipass":
            cmd = f"multipass launch -n={name}"
            Benchmark.Start()
            result = os.system(cmd)
            Benchmark.Stop()
            start_timeout = 360
            time = 0
            while time <= start_timeout:
                sleep(10)
                time += 10
                response = Shell.run(f"multipass info {name} --format=json")
                response = json.loads(response)
                status = response["info"][name]['state']
                if status == "running":
                    break
        else:
            cmd = "cms vm boot --name=" + name
            Benchmark.Start()
            result = Shell.run(cmd)
            Benchmark.Stop()

        print(result)
        assert "vm" in result

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
