###############################################################
# Consolidated shell script to run pytests
#   ./tests/test_volume.sh
###############################################################


#!/bin/bash

cms debug on

#echo "### Running tests for openstack"
#cms set cloud=openstack
#echo openstack > ../volume_openstack.log
#echo "### Starting vm"
#pytest --capture=no -v tests/test_01_setup.py >> ../volume_openstack.log
#echo "### Running volume testes"
#pytest --capture=no -v tests/test_02_volume_provider.py >> ../volume_openstack.log
#echo "### Terminating vm"
#pytest --capture=no -v tests/test_03_teardown.py >> ../volume_openstack.log
#
#echo "### Running tests for oracle"
#cms set cloud=oracle
#echo oracle > ../volume_oracle.log
#echo "### Starting vm"
#pytest --capture=no -v tests/test_01_setup.py >> ../volume_oracle.log
#echo "### Running volume testes"
#pytest --capture=no -v tests/test_02_volume_provider.py >> ../volume_oracle.log
#echo "### Terminating vm"
#pytest --capture=no -v tests/test_03_teardown.py >> ../volume_oracle.log

echo "### Running tests for aws"
cms set cloud=aws
echo aws > ../volume_aws.log
echo "### Starting vm"
pytest --capture=no -v tests/test_01_setup.py >> ../volume_aws.log
echo "### Running volume testes"
pytest --capture=no -v tests/test_02_volume_provider.py >> ../volume_aws.log
echo "### Terminating vm"
pytest --capture=no -v tests/test_03_teardown.py >> ../volume_aws.log

#echo "### Running tests for multipass"
#cms set cloud=multipass
#echo multipass > ../volume_multipass.log
#echo "### Starting vm"
#pytest --capture=no -v tests/test_01_setup.py >> ../volume_multipass.log
#echo "### Running volume testes"
#pytest --capture=no -v tests/test_02_volume_provider.py >> ../volume_multipass.log
#echo "### Terminating vm"
#pytest --capture=no -v tests/test_03_teardown.py >> ../volume_multipass.log
#
#echo "### Running tests for azure"
#cms set cloud=azure
#echo oracle > ../volume_azure.log
#echo "### Starting vm"
#pytest --capture=no -v tests/test_01_setup.py >> ../volume_azure.log
#echo "### Running volume testes"
#pytest --capture=no -v tests/test_02_volume_provider.py >> ../volume_azure.log
#echo "### Terminating vm"
#pytest --capture=no -v tests/test_03_teardown.py >> ../volume_azure.log