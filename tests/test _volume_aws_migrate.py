###############################################################
# pytest -v --capture=no tests/test_volume_aws_migrate.py
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

name1 = str(name_generator)
variables.__setitem__("vm_name1", name1)

name_generator.incr()
name2 = str(name_generator)
variables.__setitem__("vm_name2", name2)

provider = Provider(name=cloud)
current_vms = 0


# TODO:
# 1.start two vm in two different zone, one in default zone (us-east-2a), one in other zone (us-east-2c)
# 2.create 1 new volume in default zone
# 3. run migrate given --vm and --cloud (volume name will be the latest created volume)

def test_cms_vm(self):
    HEADING()
    if cloud == "multipass":
        cmd = f"multipass launch -n={name1}"
        Benchmark.Start()
        result = os.system(cmd)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(10)
            time += 10
            response = Shell.run(f"multipass info {name1} --format=json")
            response = json.loads(response)
            status = response["info"][name1]['state']
            if status == "Running":
                break
        assert status == 'Running'
        cmd = f"multipass launch -n={name2}"
        Benchmark.Start()
        result = os.system(cmd)
        Benchmark.Stop()
        start_timeout = 360
        time = 0
        while time <= start_timeout:
            sleep(10)
            time += 10
            response = Shell.run(f"multipass info {name2} --format=json")
            response = json.loads(response)
            status = response["info"][name2]['state']
            if status == "Running":
                break
        assert status == 'Running'
    else:
        cmd = "cms vm boot --name=" + name1
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "vm" in result
        cmd = "cms vm boot --name=" + name2
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "vm" in result
