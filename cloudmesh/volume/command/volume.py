import oyaml as yaml
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.volume.Provider import Provider
from cloudmesh.common.util import banner
from cloudmesh.management.configuration.name import Name as VolumeName



class VolumeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_volume(self, args, arguments):
        """
        ::

          Usage:
            volume register which
            volume register [NAME] [--cloud=CLOUD] [ARGUMENTS...]
            volume list [NAMES]
                        [--vm=VM]
                        [--region=REGION]
                        [--cloud=CLOUD]
                        [--refresh]
                        [--dryrun]
                        [--output=FORMAT]
            volume create [NAME]
                      [--size=SIZE]
                      [--volume_type=TYPE]
                      [--description=DESCRIPTION]
                      [--dryrun]
                      [ARGUMENTS...]
            volume status [NAMES]
                      [--cloud=CLOUD]
            volume attach [NAMES] [--vm=VM]
            volume detach [NAMES]
            volume delete [NAMES]
            volume migrate NAME FROM_VM TO_VM
            volume sync FROM_VOLUME TO_VOLUME

          This command manages volumes accross different clouds

          Arguments:
              NAME   the name of the volume
              vm     the name of the vm

          Options:
              --vm=VMNAME        The name of the virtual machine
              --region=REGION    The name of the region
              --cloud=CLOUD      The name of the cloud
              --refresh          If refresh the information is taken from the cloud
              --volume_type=TYPE  The type of the volume
              --output=FORMAT    Output format [default: table]

          Description:

             TBD
        """

        VERBOSE(arguments)
        variables = Variables()

        def get_last_volume():
            config = Config()

            n = VolumeName(
                user=config["cloudmesh.profile.user"],
                kind="volume",
                path=f"{config.location}/volume.yaml",
                schema="{user}-volume-{counter}"
            )
            last_volume_name = n

            return last_volume_name

        def create_name():

            config = Config()

            n = VolumeName(
                    user=config["cloudmesh.profile.user"],
                    kind="volume",
                    path=f"{config.location}/volume.yaml",
                    schema="{user}-volume-{counter}"
                )
            n.incr()
            return n

        map_parameters(arguments,
                       "cloud",
                       "vm",
                       "region",
                       "refresh",
                       "dryrun",
                       "output",
                       "size",
                       "volume_type",
                       "description",
                       )

        arguments.output = Parameter.find("output",
                                          arguments,
                                          variables,
                                          )

        #arguments.NAME = arguments.NAME or variables["volume"] #or get_last_volume()
        #path = arguments.PATH
        cloud = variables['cloud']

        if arguments.list:
            if arguments.NAMES:
                raise NotImplementedError
                names = Parameter.expand(arguments.NAMES)

                for name in names:
                    # kind = cm.kind
                    provider = Provider(name=name)
                    # result = provider.list(???)
                    result = provider.list()
            elif arguments.cloud:
                # banner(f'get in arguments.cloud {arguments.cloud}')
                #print (arguments.cloud)
                provider = Provider(name=arguments.cloud)

                result = provider.list(**arguments)
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))

                #from pprint import pprint
                #pprint (result)
            return ""

        elif arguments.create:
            #parameters = Parameter.arguments_to_dict(arguments.ARGUMENTS)
            #print("parameters",parameters)

            if arguments.cloud == None:
                arguments['cloud'] = cloud #cloud from variable['volume']
            if arguments.NAME ==None:
                arguments.NAME = str(create_name())
            provider = Provider(name=arguments.cloud)
            result = provider.create(**arguments)
            print(provider.Print(result, kind='volume', output=arguments.output))

        elif arguments.delete:
            names = Parameter.expand(arguments["NAMES"])
            '''
            volume delete NAMES
            '''
            config = Config()
            clouds = list(config["cloudmesh.volume"].keys())
            for cloud in clouds:
                active = config[f"cloudmesh.volume.{cloud}.cm.active"]
                if active:
                    provider = Provider(name=cloud)
                    deleted = []
                    for name in names:
                        volume = provider.search(name=name)
                        if volume:
                            result = provider.delete(name)
                            deleted.append(name)
                    if len(deleted) > 0:
                        #delete all deleted volumes in names
                        for name in deleted:
                            names.remove(name)


        elif arguments.attach:

            arguments.cloud = arguments.cloud or cloud

            names = arguments.NAMES or variables["volume"]
            vm = arguments.vm or variables["vm"]

            if names is None:
                Console.error("No Volume specified or found")
                return ""


            if vm is None:
                Console.error("No vm specified or found")
                return ""

            names = Parameter.expand(names)

            banner(f"Attaching {names} to {arguments.vm}")
            provider = Provider(name=arguments.cloud)

            for name in names:
                print(name)
                result = provider.attach(name, vm)
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))

        elif arguments.detach:

            config = Config()
            clouds = list(config["cloudmesh.volume"].keys())
            volumes = arguments.NAMES or variables["volume"]

            if volumes is None:
                Console.error ("No volumes specified or found")
                return ""

            volumes = Parameter.expand(volumes)

            for cloud in clouds:
                if len(volumes) != 0:
                    banner(f"Detaching volumes from {cloud}")
                else:
                    banner("End of Dataching Volumes")
                    break
                active = config[f"cloudmesh.volume.{cloud}.cm.active"]
                if active:
                    detached = []
                    provider = Provider(name=cloud)
                    for name in volumes:
                        # returns volume name if found in the cloud, None if it is not in the cloud
                        volume = provider.search(name=name)
                        if volume:
                            banner(f"Detaching {name} from {cloud}")
                            result = provider.detach(NAME=name)
                            detached.append(name)
                    if len(detached) > 0:
                        # delete all detached volumes in volumes
                        for name in detached:
                            volumes.remove(name)




