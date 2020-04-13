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
    kind = "multipass"

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
                      "AttachedToVm"
                      ],
            "header": ["Name",
                       "Cloud",
                       "Kind",
                       "State",
                       "Path",
                       "AttachedToVm"
                       ]
        }
    }

    def update_volume_info(self, NAME, mount=[]):
        info = {}
        info['name'] = NAME
        info['path'] = self.path
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
        default = config[f"cloudmesh.volume.{self.cloud}.default"]
        self.path = default['path']

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
                        "kind": "multipass",
                        "cloud": self.cloud,
                        "name": element['name'],
                    })
            d.append(element)
        return d

    def create(self,**kwargs):
        NAME = kwargs['NAME']
        print("kwargs.....", kwargs)
        result = os.system(f"mkdir {self.path}/{NAME}")
        if result == 0:
            result = self.update_volume_info(NAME=NAME)

        result = self.update_dict([result])
        return result

    def delete(self, **kwargs):
        raise NotImplementedError

    def list(self, **kwargs):
        #raise NotImplementedError
        #refresh = kwargs['refresh']
        cm = CmDatabase()
        result = glob.glob(f'{self.path}/*')

        list = []
        volumes =[]
        for i in range(len(result)):
            result[i][19:]
            list.append(result[i][23:])

        for j in range(len(list)):
            volume = cm.find_name(list[j])

            volumes.append(volume[0])

        result = self.update_dict(volumes)
        return result

    def attach(self,
               NAMES,
               vm,
               device=None,
               dryrun=False):
        cm = CmDatabase()
        results = []
        for name in NAMES:
            vms = cm.find_name(name)[0]['AttachedToVm']

            result = self.mount(path=f"{self.path}/{name}", vm=vm)
            mounts = result['mounts']
            if f"{self.path}/{name}" in mounts.keys():
                vms.append(vm)

            result = self.update_volume_info(NAME=name, mount=vms)
            results.append(result)
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

        cm = CmDatabase()
        vms = cm.find_name(NAME)[0]['AttachedToVm']
        if len(vms) == 0:
            Console.error(f"{NAME} does not attach to any vm")
        else:
            for vm in vms:
                result = self.unmount(path=f"{self.path}/{NAME}", vm=vm)
                mounts = result['mounts']
                if f"{self.path}/{NAME}" not in mounts.keys():
                    vms.remove(vm)
        result = self.update_volume_info(NAME=NAME, mount=vms)
        result = self.update_dict([result])
        return result[0]

        raise NotImplementedError


    def add_tag(self, **kwargs):

        raise NotImplementedError

    def status(self, name=None):

        raise NotImplementedError

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

