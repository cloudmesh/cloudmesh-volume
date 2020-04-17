import json
import os

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import banner
from cloudmesh.volume.VolumeABC import VolumeABC
from cloudmesh.configuration.Config import Config
from cloudmesh.common.console import Console
import subprocess
import glob
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
                      "AttachedToVm"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "State",
                       "Path",
                       'Machine Path',
                       "AttachedToVm"
                       ]
        }
    }

    def update_volume_info(self, NAME, path, mount=[]):
        info = {}
        info['name'] = NAME
        info['path'] = path
        path_list = path.split(sep='/')
        machine_path_list = ["~", "Home"]
        machine_path_list.extend(path_list[3:])
        info['machine_path'] = "/".join(machine_path_list)
        info['AttachedToVm'] = mount
        if len(mount) != 0:
            info['state'] = 'In-Use'
        else:
            info['state'] = 'available'

        return info

    #def find_volume_path(self, NAME):


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
        print(path)
        result = os.system(f"mkdir {path}/{NAME}")
        if result == 0:
            result = self.update_volume_info(NAME=NAME, path=path)

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
            if volume_info and volume_info['state'] != "deleted":
                vms = volume_info[0]['AttachedToVm']
                path = volume_info[0]['path']
                if vm in vms:
                    Console.error(f"{name} already attached to {vm}")
                else:
                    result = self.mount(path=f"{path}/{name}", vm=vm)
                    mounts = result['mounts']
                    if f"{path}/{name}" in mounts.keys():
                        vms.append(vm)
                result = self.update_volume_info(NAME=name, path=path, mount=vms)
                results.append(result)
            else:
                Console.error("volume is not existed or volume had been deleted")
        results = self.update_dict(results)
        return results

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
                    print(vm)
                    result = self.unmount(path=f"{path}/{NAME}", vm=vm)
                    mounts = result['mounts']
                    print("mounts",mounts)
                    if f"{path}/{NAME}" not in mounts.keys():
                        removed.append(vm)
                for vm in removed:
                    vms.remove(vm)
                result = self.update_volume_info(NAME=NAME, path=path, mount=vms)
                result = self.update_dict([result])
                return result[0]
        else:
            Console.error("volume is not existed or volume had been deleted")

    def add_tag(self, **kwargs):

        raise NotImplementedError

    def status(self, name=None):
        volume_info = self.cm.find_name(name)
        if volume_info:
            status = volume_info[0]['state']
        else:
            Console.error("volume is not existed")
        return print(status)

    def migrate(self,
                name=None,
                from_vm=None,
                to_vm=None):

        """
        Migrate volume from one vm to another vm.

        :param name: name of volume
        :param from_vm: name of vm where volume will be moved from
        :param to_vm: name of vm where volume will be moved to
        :return: dict
        """
        raise NotImplementedError

    def sync(self,
             from_volume=None,
             to_volume=None):
        """
        Sync contents of one volume to another volume. It is  a copy of all
        changed content from one volume to the other.

        :param from_volume: name of the from volume
        :param to_volume: name of the to volume

        :return: str
        """
        raise NotImplementedError

