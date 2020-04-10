import json
import os

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import banner
from cloudmesh.volume.VolumeABC import VolumeABC

class Provider(VolumeABC):
    kind = "multipass"

    sample = """
    cloudmesh:
      volume:
        {name}:
          cm:
            active: true
            heading: {name}
            host: TBD
            label: {name}
            kind: multipass
            version: TBD
            service: volume
          credentials:
            auth:
              username: $USER
            key_path: ~/.ssh/id_rsa.pub
          default:
            size: m1.medium
            image: lts
    """

    output = {
            "status": {
                "sort_keys": ["cm.name"],
                "order": ["cm.name",
                          "cm.cloud",
                          "vm_state",
                          "status",
                          "task_state"],
                "header": ["Name",
                           "Cloud",
                           "State",
                           "Status",
                           "Task"]
            },
            "volume": {
                "sort_keys": ["cm.name"],
                "order": ["cm.name",
                          "cm.cloud",
                          "vm_state",
                          "status",
                          "task_state",
                          "metadata.image",
                          "metadata.flavor",
                          "ip_public",
                          "ip_private",
                          "cm.create",
                          "launched_at"],
                "header": ["Name",
                           "Cloud",
                           "State",
                           "Status",
                           "Task",
                           "Image",
                           "Flavor",
                           "Public IPs",
                           "Private IPs",
                           "Creation time",
                           "Started at"],
                "humanize": ["launched_at"]
            }
    }


    def __init__(self, name):
        """
        TODO: MISSING

        :param name:
        """
        self.cloud = name
        config = Config()
        default = config[f"cloudmesh.volume.{cloud}.default"]
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
        for key, entry in elements.items():

            entry['name'] = key

            if "cm" not in entry:
                entry['cm'] = {}

            # if kind == 'ip':
            #    entry['name'] = entry['floating_ip_address']

            entry["cm"].update({
                "kind": kind,
                "driver": self.cloudtype,
                "cloud": self.cloud,
                "name": key
            })

            if kind == 'vm':

                entry["cm"]["updated"] = str(DateTime.now())

                # if 'public_v4' in entry:
                #    entry['ip_public'] = entry['public_v4']

                # if "created_at" in entry:
                #    entry["cm"]["created"] = str(entry["created_at"])
                # del entry["created_at"]
                #    if 'status' in entry:
                #        entry["cm"]["status"] = str(entry["status"])
                # else:
                #    entry["cm"]["created"] = entry["modified"]

            elif kind == 'image':

                entry["cm"]["created"] = entry["updated"] = str(
                    DateTime.now())

            # elif kind == 'version':

            #    entry["cm"]["created"] = str(DateTime.now())

            d.append(entry)
        return d


    def list(self,
             **kwargs
             ):
        os.system(f"ls {path}")


    def mount(self, path=None, name=None):
        """
        TODO: MISSING

        :param path:
        :param name:
        :return:
        """
        banner(f"mount {path} {name}")
        os.system(f"multipass mount {path}  {name}")
        dict_result = self._get_mount_status(name)
        print(dict_result)
        return dict_result


    def _get_mount_status(self, name=None):
        """
        TODO: MISSING

        :param name:
        :return:
        """
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
                'status': result["info"][name]['state'],
                'mounts': result["info"][name]['mounts']
            }
        return dict_result