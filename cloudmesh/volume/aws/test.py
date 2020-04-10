{'Reservations':
  [
   {'Groups': [],
    'Instances':
     [
      {'AmiLaunchIndex': 0,
       'ImageId': 'ami-0fc20dd1da406780b',
       'InstanceId': 'i-019849c08eff6fbf7',
       'InstanceType': 't2.micro',
       'KeyName': 'aws_ec2_cert',
       'LaunchTime': datetime.datetime(2020, 4, 9, 19, 33, 1, tzinfo=tzutc()),
       'Monitoring': {'State': 'disabled'},
       'Placement': {
        'AvailabilityZone': 'us-east-2a',
        'GroupName': '',
        'Tenancy': 'default'
       },
       'PrivateDnsName': 'ip-172-31-14-177.us-east-2.compute.internal',
       'PrivateIpAddress': '172.31.14.177',
       'ProductCodes': [],
       'PublicDnsName': 'ec2-3-135-219-125.us-east-2.compute.amazonaws.com',
       'PublicIpAddress': '3.135.219.125',
       'State':
        {'Code': 16, 'Name': 'running'},
       'StateTransitionReason': '',
       'SubnetId': 'subnet-bd46b6d6',
       'VpcId': 'vpc-e334fc88',
       'Architecture': 'x86_64', 'BlockDeviceMappings': [{'DeviceName': '/dev/sda1', 'Ebs': {'AttachTime': datetime.datetime(2020, 4, 7, 1, 12, 9, tzinfo=tzutc()), 'DeleteOnTermination': True, 'Status': 'attached', 'VolumeId': 'vol-02e87792ec8f8a66c'}}, {'DeviceName': '/dev/sdb', 'Ebs': {'AttachTime': datetime.datetime(2020, 4, 9, 21, 14, 27, tzinfo=tzutc()), 'DeleteOnTermination': False, 'Status': 'attached', 'VolumeId': 'vol-089b308665849a6ee'}}], 'ClientToken': '', 'EbsOptimized': False, 'EnaSupport': True, 'Hypervisor': 'xen', 'NetworkInterfaces': [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-3-135-219-125.us-east-2.compute.amazonaws.com', 'PublicIp': '3.135.219.125'}, 'Attachment': {'AttachTime': datetime.datetime(2020, 4, 7, 1, 12, 8, tzinfo=tzutc()), 'AttachmentId': 'eni-attach-0c7ece4f3451fd4d0', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'}, 'Description': 'Primary network interface', 'Groups': [{'GroupName': 'launch-wizard-11', 'GroupId': 'sg-0c35bddbcdb96de92'}], 'Ipv6Addresses': [], 'MacAddress': '02:f4:30:fc:dd:0c', 'NetworkInterfaceId': 'eni-074dddcfecaeed048', 'OwnerId': '998726019676', 'PrivateDnsName': 'ip-172-31-14-177.us-east-2.compute.internal', 'PrivateIpAddress': '172.31.14.177', 'PrivateIpAddresses': [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-3-135-219-125.us-east-2.compute.amazonaws.com', 'PublicIp': '3.135.219.125'}, 'Primary': True, 'PrivateDnsName': 'ip-172-31-14-177.us-east-2.compute.internal', 'PrivateIpAddress': '172.31.14.177'}], 'SourceDestCheck': True, 'Status': 'in-use', 'SubnetId': 'subnet-bd46b6d6', 'VpcId': 'vpc-e334fc88', 'InterfaceType': 'interface'}], 'RootDeviceName': '/dev/sda1', 'RootDeviceType': 'ebs', 'SecurityGroups': [{'GroupName': 'launch-wizard-11', 'GroupId': 'sg-0c35bddbcdb96de92'}], 'SourceDestCheck': True, 'Tags': [{'Key': 'Name', 'Value': 'xin-vm-1'}], 'VirtualizationType': 'hvm', 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}, 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}, 'HibernationOptions': {'Configured': False}, 'MetadataOptions': {'State': 'applied', 'HttpTokens': 'optional', 'HttpPutResponseHopLimit': 1, 'HttpEndpoint': 'enabled'}}], 'OwnerId': '998726019676', 'ReservationId': 'r-00496db3279c892e1'}], 'ResponseMetadata': {'RequestId': 'faa02c6e-970f-4249-9082-3fa623aac03a', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'faa02c6e-970f-4249-9082-3fa623aac03a', 'content-type': 'text/xml;charset=UTF-8', 'content-length': '7735', 'vary': 'accept-encoding', 'date': 'Thu, 09 Apr 2020 21:37:59 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}
