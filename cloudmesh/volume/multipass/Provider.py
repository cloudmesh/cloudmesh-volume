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
                      "state",
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

    def create_volume_info(self, NAME, path):
        info = {}
        info['tags'] = []
        info['name'] = NAME
        info['path'] = path
        info['AttachedToVm'] = []
        info['state'] = 'available'
        info['machine_path'] = None
        info['time'] = datetime.datetime.now()
        return info

    def update_volume_after_attached_to_vm(self, info, vms):
        path = info[0]['path']
        path_list = path.split(sep='/')
        machine_path_list = ["~", "Home"]
        machine_path_list.extend(path_list[3:])
        info[0]['machine_path'] = "/".join(machine_path_list)
        info[0]['AttachedToVm'] = vms
        info[0]['state'] = 'in-use'
        info[0]['time'] = datetime.datetime.now()
        return info

    def update_volume_after_detach(self, info,vms):
        info[0]['AttachedToVm'] = vms
        if len(vms)==0:
            info[0]['machine_path'] = None
            info[0]['state'] = 'available'
        info[0]['time'] = datetime.datetime.now()
        return info

    def update_volume_tag(self,info, key, value):
        keys = []
        #tag = {key: value}
        # if given duplicated tag name, update the value to the current tag value
        # can set value="" to delete value of a tag
        for tag in info[0]['tags']:
            if key == list(tag.keys())[0]:
                tag.update({key:value})
            keys.append(list(tag.keys())[0])
        if key not in keys:
            tag = {key: value}
            info[0]['tags'].append(tag)
        info[0]['time'] = datetime.datetime.now()
        return info

    def __init__(self,name):
        """
        TODO: MISSING
        :param name:
        """
        self.cloud = name
        self.cloudtype = "multipass"
        config = Config()
        self.default = config[f"cloudmesh.volume.{self.cloud}.default"]
        self.cm = CmDatabase()

    def update_dict(self, elements, kind=None):
        """
        converts the dict into a list

        :param elements: the list of original dicts. If elements is a single
                         dict a list with a single element is returned.
        :param kind: for some kinds special attributes are added. This includes
                     key, vm, image, flavor.
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
        banner(f"**kwargs,{kwargs}")
        for key in self.default.keys():
            if key not in kwargs.keys():
                kwargs[key] = self.default[key]
            elif kwargs[key] == None:
                kwargs[key] = self.default[key]
        NAME = kwargs['NAME']
        path = kwargs['path']
        result = os.system(f"mkdir {path}/{NAME}")
        if result == 0:
            result = self.create_volume_info(NAME=NAME, path=path)

        result = self.update_dict([result])
        return result

    def delete(self, NAME):
        result = self.cm.find_name(NAME)
        path = result[0]['path']
        try:
            re = os.system(f"rmdir {path}/{NAME}")
            result[0]['state'] = 'deleted'
            result = self.update_dict(result)
            #cmulti = cm.collection("multipass-volume")
            #cmulti.delete_one(f"{'name': {NAME}}")
        except:
            Console.error("volume is either not empty or not exist")
        return result

    def list(self, **kwargs):

        #refresh = kwargs['refresh']
        result = self.cm.find(cloud='multipass', kind='volume')
        return result

    def attach(self,
               NAMES,
               vm,
               device=None,
               dryrun=False):

        results = []
        for name in NAMES:
            volume_info = self.cm.find_name(name)
            print(volume_info)
            if volume_info and volume_info[0]['state'] != "deleted":
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
                print(results)
            else:
                Console.error("volume is not existed or volume had been deleted")
        #results = self.update_dict([results])
        return results[0]

    def mount(self,path=None,vm=None):
        """
        TODO: MISSING

        :param path:
        :param vm:
        :return:
        """
        #banner(f"mount {self.path} {vm}")
        os.system(f"multipass mount {path} {vm}")
        dict_result = self._get_mount_status(vm=vm)

        return dict_result

    def _get_mount_status(self,vm=None):
        """
        TODO: MISSING

        :param name:
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
        #banner(f"unmount {vm}:{path}")
        os.system(f"multipass unmount {vm}:{path}")
        dict_result = self._get_mount_status(vm=vm)

        return dict_result


    def detach(self, NAME):
        #will detach from all vms
        volume_info = self.cm.find_name(NAME)
        if volume_info and volume_info[0]['state'] != "deleted":
            vms = volume_info[0]['AttachedToVm']
            path = volume_info[0]['path']
            if len(vms) == 0:
                Console.error(f"{NAME} does not attach to any vm")
            else:
                removed = []
                for vm in vms:
                    result = self.unmount(path=f"{path}/{NAME}", vm=vm)
                    mounts = result['mounts']
                    if f"{path}/{NAME}" not in mounts.keys():
                        removed.append(vm)
                for vm in removed:
                    vms.remove(vm)
                result = self.update_volume_after_detach(volume_info, vms)
                #result = self.update_dict([result])
                return result[0]
        else:
            Console.error("volume is not existed or volume had been deleted")

    def add_tag(self, NAME, **kwargs):
        key = kwargs['key']
        value = kwargs['value']
        volume_info = self.cm.find_name(name=NAME)
        volume_info = self.update_volume_tag(info=volume_info, key=key, value=value)
        return volume_info[0]

    def status(self, name=None):
        volume_info = self.cm.find_name(name)
        if volume_info:
            status = volume_info[0]['state']
        else:
            Console.error("volume is not existed")
        return volume_info

    def migrate(self, **kwargs):
        """
        Migrate volume from one vm to another vm. "region" is volume path.
        If vm and volume are in the same region, migrate within the same region
        If vm and volume are in different regions, migrate between two regions

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

    def sync(self, NAMES):
        """
        sync contents of one volume to another volume

        :param NAMES (list): list of volume names
        :return: dict
        """
        path1 = f"{self.cm.find_name(name=NAMES[0])[0]['path']}/{NAMES[0]}/"
        path2 = f"{self.cm.find_name(name=NAMES[1])[0]['path']}/{NAMES[1]}/"
        os.system(f"rsync -avzh {path2} {path1}")
        kwargs1={}
        kwargs1['key'] = "sync_with"
        kwargs1['value'] = NAMES[1]
        volume_info1 = self.add_tag(NAMES[0],**kwargs1)
        result = [volume_info1]
        return result

