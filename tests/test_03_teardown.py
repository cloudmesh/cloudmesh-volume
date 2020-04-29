###############################################################
# pytest -v --capture=no tests/test_03_teardown.py
###############################################################

# TODO: start this with cloud init, e.g, empty mongodb
# TODO: assertuons need to be added

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config

Benchmark.debug()

user = Config()["cloudmesh.profile.user"]
variables = Variables()
VERBOSE(variables.dict())

#
# cms set cloud=openstack
#
cloud = variables.parameter('cloud')


@pytest.mark.incremental
class Test_provider_volume:

    def test_cms_terminate(self):
        HEADING()
        if cloud == "multipass":
            cmd = f"multipass delete {variables.__getitem__('vm_name')}"
        else:
            cmd = "cms vm terminate " + variables.__getitem__("vm_name")
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print("result", result)
        if cloud == "multipass":
            assert result == ''
        else:
            assert "vm" in result

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
