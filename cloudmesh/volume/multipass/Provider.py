import json
import os

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import banner
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.configuration.Config import Config
from cloudmesh.common.console import Console
import datetime
from cloudmesh.mongo.CmDatabase import CmDatabase

class Provider(VolumeABC):
    kind = "volume"

    sample = """
    cloudmesh:
      volume:
        multipass:
              cm:
                active: '1'
                heading: multipass
                host: TBD
                kind: multipass
                version: TBD
                service: volume
              default:
                path: /Volumes/multipass
    """

    output = {
        "volume": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "cm.kind",
                      "State",
                      "path",
                      'machine_path',
                      "AttachedToVm",
                      "tags",
                      "time"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "State",
                       "Path",
                       'Machine Path',
                       "AttachedToVm",
                       "Tags",
                       "Update Time"
                       ]
        }
    }

    def generate_volume_info(self, NAME, path):
        """
        generate volume info dict.
        info['AttachedToVm'] is a list of vm names where the volume is attached to. (volume can attach to multiple vm and vm
        can have multiple attachments)
        info['machine_path'] is the volume path in vm
        info['time"] is the created time, will be updated as updated time

        :param NAME: volume name
        :param path: volume path
        :return: dict
        """
        info = {}
        info['tags'] = []
        info['name'] = NAME
        info['path'] = path
        info['AttachedToVm'] = []
        info['State'] = 'available'
        info['machine_path'] = None
        info['time'] = datetime.datetime.now()
        return info

    def update_volume_after_attached_to_vm(self, info, vms):
        """
        Update volume info after attached to a vm.
        info['AttachedToVm'] is a list of vm names where the volume is attached to.
        info['machine_path'] is the volume path in vm
        info['time"] is the updated as updated time

        :param info: volume info got from MongoDB database
        :param vms: attached to vms
        :return: list of one dict
        """
        path = info[0]['path']
        path_list = path.split(sep='/')
        machine_path_list = ["~", "Home"]
        machine_path_list.extend(path_list[3:])
        info[0]['machine_path'] = "/".join(machine_path_list)
        info[0]['AttachedToVm'] = vms
        info[0]['State'] = 'in-use'
        info[0]['time'] = datetime.datetime.now()
        return info

    def update_volume_after_detach(self, info,vms):
        """
        update volume info after detaching from a vm
        info['AttachedToVm'] is a list of vm names where the volume is attached to.
        info['time"] is the updated time

        :param info: volume info
        :param vms: attached to vms
        :return: list of one dict
        """
        info[0]['AttachedToVm'] = vms
        if len(vms)==0:
            info[0]['machine_path'] = None
            info[0]['State'] = 'available'
        info[0]['time'] = datetime.datetime.now()
        return info

    def update_volume_tag(self,info, key, value):
        """
        Update volume tag.
        Tags is a key-value pair, with key as tag name and value as tag value, tag = {key: value}.
        A volume can have multipale tags.
        If given duplicated tag name, update the value to the current tag value.

        :param info: volume info
        :param vms: attached to vms
        :return: list of one dict
        """
        keys = []
        for tag in info[0]['tags']:
            if key == list(tag.keys())[0]:
                if len(value)==0:
                    print("here1")
                    info[0]['tags'].remove(tag)
                    print(info[0]['tags'])
                    keys.append(list(tag.keys())[0])
                else:
                    tag.update({key:value})
                    keys.append(list(tag.keys())[0])
        print("keys",keys)
        if key not in keys:
            tag = {key: value}
            info[0]['tags'].append(tag)
        info[0]['time'] = datetime.datetime.now()
        return info

    def __init__(self,name):
        """
        Initialize provider.
        set cloudtype to "multipass", get the default dict, create a cloudmesh database object.

        :param name: name of cloud
        """
        self.cloud = name
        self.cloudtype = "multipass"
        config = Config()
        self.default = config[f"cloudmesh.volume.{self.cloud}.default"]
        self.cm = CmDatabase()

    def update_dict(self, elements, kind=None):
        """
        converts the dict into a list.

        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :param kind: "multipass"
        :return: The list with the modified dicts
        """

        if elements is None:
            return None

        d = []
        for element in elements:
            if "cm" not in element.keys():
                element['cm'] = {}
            element["cm"].update({
                        "kind": "volume",
                        "cloud": self.cloud,
                        "name": element['name'],
                    })
            d.append(element)
        return d

    def create(self,**kwargs):
        """
        This function create a new volume.
        Default parameters from self.default, such as: path="/Users/username/multipass".

        :param NAME (string): the name of volume
        :param path (string): path of volume
        :return: dict
        """

        for key in self.default.keys():
            if key not in kwargs.keys():
                kwargs[key] = self.default[key]
            elif kwargs[key] == None:
                kwargs[key] = self.default[key]
        NAME = kwargs['NAME']
        path = kwargs['path']
        result = os.system(f"mkdir {path}/{NAME}")
        if result == 0:
            result = self.generate_volume_info(NAME=NAME, path=path)

        result = self.update_dict([result])
        return result

    def delete(self, name):
        """
        Delete volumes.
        If name is not given, delete the most recent volume.

        :param name: volume name
        :return:
        """
        result = self.cm.find_name(name)
        path = result[0]['path']
        try:
            re = os.system(f"rmdir {path}/{name}")
            result[0]['State'] = 'deleted'
            result = self.update_dict(result)
        except:
            Console.error("volume is either not empty or not exist")
        return result

    def list(self, **kwargs):

        """
        This function list all volumes as following:
        If NAME (volume name) is specified, it will print out info of NAME.
        If NAME (volume name) is not specified, it will print out info of all
          volumes under current cloud.
        If vm is specified, it will print out all the volumes attached to vm.
        If region(path) is specified, it will print out
          all the volumes in that region. i.e. /Users/username/multipass

        :param NAME: name of volume
        :param vm: name of vm
        :param region: for multipass, it is the same with "path"
        :return: dict
        """

        if kwargs:
            result = self.cm.find(cloud='multipass', kind='volume')
            for key in kwargs:
                if key == 'NAME' and kwargs['NAME']:
                    result = self.cm.find_name(name=kwargs['NAME'])
                elif key=='NAMES' and kwargs['NAMES']:
                    result = self.cm.find_names(names=kwargs['NAMES'])
                elif key =='vm' and kwargs['vm']:
                    result = self.cm.find(collection=f"{self.cloud}-volume", query={'AttachedToVm': kwargs['vm']})
                    # result = []
                    # response = self._get_mount_status(vm=kwargs['vm'])
                    # mounts = response['mounts']
                    # for key in mounts.keys():
                    #     volume_name = key.split(sep="/")[-1]
                    #     r = self.cm.find_name(name=volume_name)
                    #     result.append(r)
                elif key =='region' and kwargs['region']:
                    result = self.cm.find(collection=f"{self.cloud}-volume", query={'path': kwargs['region']})
        else:
            result = self.cm.find(cloud='multipass', kind='volume')
        return result

    def _get_vm_status(self, name=None) -> dict:

        """
        Get vm status.

        :param name (string): vm name
        :return: dict
        """

        dict_result = {}
        result = Shell.run(f"multipass info {name} --format=json")

        if f'instance "{name}" does not exist' in result:
            dict_result = {
                'name': name,
                'status': "instance does not exist"
            }
        else:
            result = json.loads(result)
            dict_result = {
                'name': name,
                'status': result["info"][name]['State']
            }

        return dict_result

    def attach(self,
               names,
               vm):
        """
        This function attach one or more volumes to vm. It returns info of
        updated volume. The updated dict with "AttachedToVm" showing
        the name of vm where the volume attached to.

        :param names (string): names of volumes
        :param vm (string): name of vm
        :return: dict
        """

        results = []
        for name in names:
            volume_info = self.cm.find_name(name)
            if volume_info and volume_info[0]['State'] != "deleted":
                vms = volume_info[0]['AttachedToVm']
                path = volume_info[0]['path']
                if vm in vms:
                    Console.error(f"{name} already attached to {vm}")
                else:
                    result = self.mount(path=f"{path}/{name}", vm=vm)
                    mounts = result['mounts']
                    if f"{path}/{name}" in mounts.keys():
                        vms.append(vm)
                result = self.update_volume_after_attached_to_vm(info=volume_info, vms=vms)
                results.append(result)
            else:
                Console.error("volume is not existed or volume had been deleted")
        #results = self.update_dict([results])
        return results[0]

    def mount(self,path=None,vm=None):
        """
        mount volume to vm

        :param path (string): path of volume
        :param vm (string): name of vm
        :return: dict
        """

        os.system(f"multipass mount {path} {vm}")
        dict_result = self._get_mount_status(vm=vm)

        return dict_result

    def _get_mount_status(self,vm=None):
        """
        Get mount status of vm

        :param vm (string): name of vm
        :return:
        """
        result = Shell.run(f"multipass info {vm} --format=json")

        if f'instance "{vm}" does not exist' in result:
            dict_result = {
                'name': vm,
                'status': "instance does not exist"
            }
        else:
            result = json.loads(result)
            dict_result = {
                'name': vm,
                'status': result["info"][vm]['state'],
                'mounts': result["info"][vm]['mounts']
            }
        return dict_result

    def unmount(self, path=None, vm=None):
        """
        Unmount volume from vm

        :param path (string): path of volume
        :param vm (string): name of vm
        :return:
        """

        os.system(f"multipass unmount {vm}:{path}")
        dict_result = self._get_mount_status(vm=vm)

        return dict_result


    def detach(self, name):
        """
        This function detach a volume from vm. It returns the info of
        the updated volume.
        The vm under "AttachedToVm" will be removed if
        volume is successfully detached.
        Will detach volume from all vms.

        :param name: name of volume to be dettached
        :return: dict
        """

        volume_info = self.cm.find_name(name)
        if volume_info and volume_info[0]['State'] != "deleted":
            vms = volume_info[0]['AttachedToVm']
            path = volume_info[0]['path']
            if len(vms) == 0:
                Console.error(f"{name} does not attach to any vm")
            else:
                removed = []
                for vm in vms:
                    result = self.unmount(path=f"{path}/{name}", vm=vm)
                    mounts = result['mounts']
                    if f"{path}/{name}" not in mounts.keys():
                        removed.append(vm)
                for vm in removed:
                    vms.remove(vm)
                result = self.update_volume_after_detach(volume_info, vms)
                return result[0]
        else:
            Console.error("volume is not existed or volume had been deleted")

    def add_tag(self, **kwargs):
        """
        This function add tag to a volume.
        If volume name is not specified, then tag will be added to the last volume.

        :param NAME: name of volume
        :param kwargs:
                    key: name of tag
                    value: value of tag
        :return: dict
        """
        key = kwargs['key']
        value = kwargs['value']
        volume_info = self.cm.find_name(name=NAME)
        volume_info = self.update_volume_tag(info=volume_info, key=key, value=value)
        return volume_info[0]

    def status(self, name=None):
        """
        This function get volume status, such as "in-use", "available", "deleted"

        :param name (string): volume name
        :return: dict
        """
        volume_info = self.cm.find_name(name)
        if volume_info:
            status = volume_info[0]['State']
        else:
            Console.error("volume is not existed")
        return volume_info

    def migrate(self, **kwargs):
        """
        Migrate volume from one vm to another vm. "region" is volume path.
        If vm and volume are in the same region (path), migrate within the same region (path)
        If vm and volume are in different regions, migrate between two regions (path)

        :param NAME (string): the volume name
        :param vm (string): the vm name
        :return: dict
        """
        volume_name = kwargs['NAME']
        vm = kwargs['vm']

        volume_info = self.cm.find_name(name=volume_name)
        volume_attached_vm = volume_info[0]['AttachedToVm']

        vm_info = Shell.run(f"multipass info {vm} --format=json")
        vm_info = json.loads(vm_info)
        vm_status = vm_info["info"][vm]['state']

        if vm_status == 'running':
            self.detach(NAME=volume_name)
            self.attach(NAMES=[volume_name],vm=vm)
        try:
            for old_vm in volume_attached_vm:
                volume_info[0]['AttachedToVm'].remove(old_vm)
        except:
            pass
        volume_info[0]['AttachedToVm'].append(vm)

        return volume_info

    def sync(self, names):
        """
        sync contents of one volume to another volume

        :param names (list): list of volume names
        :return: list of dict
        """
        path1 = f"{self.cm.find_name(name=names[0])[0]['path']}/{names[0]}/"
        path2 = f"{self.cm.find_name(name=names[1])[0]['path']}/{names[1]}/"
        os.system(f"rsync -avzh {path2} {path1}")
        kwargs1={}
        kwargs1['key'] = "sync_with"
        kwargs1['value'] = names[1]
        volume_info1 = self.add_tag(names[0],**kwargs1)
        result = [volume_info1]
        return result

