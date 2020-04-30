###############################################################
# pytest -v --capture=no tests/test_volume_migrate_sync.py
###############################################################

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
# cms set cloud=aws
#
cloud = variables.parameter('cloud')

print(f"Test run for {cloud}")

if cloud is None:
    raise ValueError("cloud is not set")

name_generator = Name()
name_generator.set(f"test-{user}-vm-" + "{counter}")
vm_name1 = str(name_generator)
name_generator.incr()
vm_name2 = str(name_generator)

volume_name_generator = Name()
volume_name_generator.set(f"test-{user}-volume-" + "{counter}")
volume_name1 = str(volume_name_generator)
volume_name_generator.incr()
volume_name2 = str(volume_name_generator)

provider = Provider(name=cloud)
current_vms = 0


@pytest.mark.incremental
class Test_provider_volume:

    def test_cms_vm_setup(self):
        HEADING()
        if cloud == "multipass":
            os.system(f"multipass launch -n={vm_name1}")
            os.system(f"multipass launch -n={vm_name2}")
        else:
            os.system(f"cms vm boot --name={vm_name1}")
            os.system(f"cms vm boot --name={vm_name2}")

    def test_provider_volume_migrate(self):
        HEADING()
        os.system(f"cms volume create {volume_name1}")
        # attach volume_name1 to vm_name1
        os.system(f"cms volume attach --vm={vm_name1}")
        # "cms volume migrate NAME --vm=vm_name2 --cloud=aws"
        params = {"NAME": volume_name1, "vm": vm_name2, "cloud": cloud}
        Benchmark.Start()
        data = provider.migrate(**params)
        Benchmark.Stop()
        sleep(10)
        assert data[0]['AttachedToVm'][0] == vm_name2

    def test_provider_volume_sync(self):
        HEADING()
        os.system(f"cms volume detach {volume_name1}")
        os.system(f"cms volume create {volume_name2}")
        if cloud == 'aws':
            # "cms volume sync volume_name1,volume_name2"
            params = {"NAMES": [volume_name1, volume_name2], "cloud": cloud}
            Benchmark.Start()
            data = provider.sync(**params)
            Benchmark.Stop()
            assert data

        elif cloud == 'multipass':
            volume2_path = provider.list(NAME=volume_name2)[0]['path']
            os.system(f"mkdir {volume2_path}/{volume_name2}/test")
            params = {"NAMES": [volume_name1, volume_name2], "cloud": cloud}
            Benchmark.Start()
            data = provider.sync(**params)
            Benchmark.Stop()
            assert data[0]['tags'][0]["sync_with"] == volume_name2

    # clean up
    def test_provider_volume_cleanup(self):
        HEADING()
        if cloud == "multipass":
            os.system(f"cms volume delete {volume_name1},{volume_name2}")
            os.system(f"multipass delete {vm_name1}")
            os.system(f"multipass delete {vm_name1}")
            os.system("multipass purge")
        elif cloud == 'aws':
            os.system("cms volume detach")
            os.system(f"cms volume delete {volume_name1},{volume_name2}")
            os.system(f"cms vm terminate {vm_name1}")
            os.system(f"cms vm terminate {vm_name2}")

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
