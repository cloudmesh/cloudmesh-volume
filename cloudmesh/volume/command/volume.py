from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.name import Name as VolumeName
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.volume.Provider import Provider


class VolumeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_volume(self, args, arguments):
        """
        ::

          Usage:
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
                        [--region=REGION]
                        [--path=PATH]
            volume attach [NAMES] [--vm=VM]
            volume detach [NAMES]
            volume delete [NAMES]
            volume add_tag [NAME]
                        [--key=KEY]
                        [--value=VALUE]
            volume status [NAME]
            volume migrate [NAME]
                        [--vm=VM]
                        [--cloud=CLOUD]
            volume sync [NAMES]
                        [--cloud=CLOUD]
            volume purge [--cloud=CLOUD]

          This command manages volumes across different clouds

          Arguments:
              NAME   the name of the volume
              NAMES  the names of multiple volumes

          Options:
              --vm=VMNAME          The name of the virtual machine
              --region=REGION      The name of the region
              --cloud=CLOUD        The name of the cloud
              --refresh            If refresh the info is taken from the cloud
              --volume_type=TYPE   The type of the volume
              --output=FORMAT      Output format [default: table]
              --key=KEY            The tag key
              --value=VALUE        The value of tag key
              --snapshot           The snapshot of volume
              --path=PATH          The path of local volume

          Description:

            volume list [NAMES]
                        [--vm=VM]
                        [--region=REGION]
                        [--cloud=CLOUD]
                        [--refresh]
                        [--dryrun]
                        [--output=FORMAT]
                List all the volumes for certain vm, region, or cloud.

            volume create [NAME]
                          [--size=SIZE]
                          [--volume_type=TYPE]
                          [--description=DESCRIPTION]
                          [--dryrun]
                          [--snapshot=SNAPSHOT]
                          [--region=REGION]
                Creates a volume

            volume status [NAMES]
                          [--cloud=CLOUD]
            volume attach [NAMES]
                          [--vm=VM]
                Attach volume to a vm

            volume detach [NAMES]
                Detach volume from a vm

            volume delete [NAMES]
                Delete the named volumes

            volume migrate [NAME]
                           [--vm=VM]
                           [--cloud=CLOUD]
                 Migrate volume from one vm to another vm in the same provider.

            volume sync [NAMES]
                        [--cloud=CLOUD]
                Volume sync allows for data to shared between two volumes.

            volume purge [--cloud=CLOUD]
                Volume purge delete all the "deleted" volumes in MongoDB database

        """

        VERBOSE(arguments)
        variables = Variables()

        def get_last_volume():
            """
            get the last volume name

            :return: string
            """
            config = Config()

            n = VolumeName(
                user=config["cloudmesh.profile.user"],
                kind="volume",
                path=f"{config.location}/volume.yaml",
                schema="{user}-volume-{counter}"
            )
            last_volume_name = n

            return str(last_volume_name)

        def create_name():
            """
            Create volume name if name is not specified

            :return: string
            """

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
                       "key",
                       "value",
                       "snapshot",
                       "path"
                       )

        arguments.output = Parameter.find("output",
                                          arguments,
                                          variables,
                                          )

        cloud = variables['cloud']

        if arguments.list:
            if arguments.NAMES:
                names = Parameter.expand(arguments["NAMES"])
                if arguments.cloud:
                    # "cms volume list NAMES --cloud=aws1"
                    provider = Provider(name=arguments.cloud)

                    result = provider.list(**arguments)
                    print(provider.Print(result,
                                         kind='volume',
                                         output=arguments.output))
                else:
                    # if "cms volume list NAMES"
                    config = Config()
                    clouds = list(config["cloudmesh.volume"].keys())
                    for cloud in clouds:
                        if len(names) != 0:
                            banner(f"listing volume info from {cloud}")
                        else:
                            banner("End of listing Volumes")
                            break
                        active = config[f"cloudmesh.volume.{cloud}.cm.active"]
                        if active:
                            provider = Provider(name=cloud)
                            listed = []
                            for name in names:
                                volume = provider.search(name=name)
                                if volume:
                                    arguments.NAME = name
                                    result = provider.list(**arguments)
                                    print(provider.Print(result,
                                                         kind='volume',
                                                         output=arguments.output
                                                         ))
                                    listed.append(name)
                            if len(listed) > 0:
                                # delete all listed volumes in names
                                for name in listed:
                                    names.remove(name)

            else:
                if arguments.cloud:
                    # "cms volume list --cloud=aws1"
                    provider = Provider(name=arguments.cloud)

                    result = provider.list(**arguments)
                    print(provider.Print(result,
                                         kind='volume',
                                         output=arguments.output))
                else:
                    # "cms volume list"
                    arguments['cloud'] = cloud
                    provider = Provider(name=arguments.cloud)

                    result = provider.list(**arguments)
                    print(provider.Print(result,
                                         kind='volume',
                                         output=arguments.output))

            return ""

        elif arguments.create:
            if arguments.cloud is None:
                arguments['cloud'] = cloud
            if arguments.NAME is None:
                arguments.NAME = str(create_name())
            provider = Provider(name=arguments.cloud)
            result = provider.create(**arguments)
            print(provider.Print(result, kind='volume', output=arguments.output
                                 ))

        elif arguments.delete:
            names = arguments.NAMES or variables["volume"]
            names = Parameter.expand(names)
            if names is None:
                Console.error("No volume specified or found")
                return ""
            config = Config()
            clouds = list(config["cloudmesh.volume"].keys())
            for cloud in clouds:
                # if len(names) != 0:
                #     banner(f"Deleting volumes from {cloud}")
                # else:
                #     banner("End of Deleting Volumes")
                active = config[f"cloudmesh.volume.{cloud}.cm.active"]
                if active:
                    provider = Provider(name=cloud)
                    deleted = []
                    for name in names:
                        volume = provider.search(name=name)
                        if volume:
                            result = provider.delete(name=name)
                            deleted.append(name)
                    if len(deleted) > 0:
                        # delete all deleted volumes in names
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
            #banner(f"Attaching {names} to {arguments.vm}")
            provider = Provider(name=arguments.cloud)
            result = provider.attach(names, vm)
            print(provider.Print(result, kind='volume', output=arguments.output)
                  )

        elif arguments.detach:
            config = Config()
            clouds = list(config["cloudmesh.volume"].keys())
            volumes = arguments.NAMES or variables["volume"]
            if volumes is None:
                Console.error("No volume specified or found")
                return ""
            volumes = Parameter.expand(volumes)
            for cloud in clouds:
                # if len(volumes) != 0:
                #     banner(f"Detaching volumes from {cloud}")
                # else:
                #     banner("End of Detaching Volumes")
                #     break
                active = config[f"cloudmesh.volume.{cloud}.cm.active"]
                if active:
                    detached = []
                    provider = Provider(name=cloud)
                    for name in volumes:
                        # returns volume name if found in the cloud,
                        # None if it is not in the cloud
                        volume = provider.search(name=name)
                        if volume:
                            #banner(f"Detaching {name} from {cloud}")
                            result = provider.detach(NAME=name)
                            detached.append(name)
                            print(provider.Print(result, kind='volume',
                                                 output=arguments.output))
                    if len(detached) > 0:
                        # delete all detached volumes in volumes
                        for name in detached:
                            volumes.remove(name)

        elif arguments.add_tag:
            arguments.cloud = arguments.cloud or cloud
            name = arguments.NAME or variables["volume"] or get_last_volume()
            arguments.NAME = name
            provider = Provider(name=arguments.cloud)
            result = provider.add_tag(**arguments)
            print(provider.Print(result, kind='volume', output=arguments.output)
                  )

        elif arguments.status:
            arguments.cloud = arguments.cloud or cloud
            name = arguments.NAME or variables["volume"] or get_last_volume()
            arguments.NAME = name
            provider = Provider(name=arguments.cloud)
            result = provider.status(NAME=name)
            print(provider.Print(result, kind='volume', output=arguments.output)
                  )

        elif arguments.migrate:
            if arguments.cloud:
                # "cms volume migrate NAME --vm=VM --cloud=aws1"
                # if no given volume, get the current volume
                # or get the last volume,
                name = arguments.NAME or variables["volume"] \
                       or get_last_volume()
                arguments.NAME = name
                provider = Provider(name=arguments.cloud)
                result = provider.migrate(**arguments)
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))
            else:
                raise NotImplementedError

        elif arguments.sync:
            # "cms volume sync NAMES"
            # when len(NAMES)==2, sync volume (NAMES[0]) with volume (NAMES[1])
            # when len(NAMES)==1, sync current volume with volume(NAMES[0])
            # what it actually does is copy second volume and overwrite
            # the other (current volume or first volume in NAMES)

            if len([arguments.NAMES]) == 1:
                volumes = [variables["volume"] or get_last_volume(),
                           arguments.NAMES]
                arguments.NAMES = volumes
            elif len([arguments.NAMES]) == 2:
                volumes = arguments.NAMES
            else:
                Console.error("Two volumes should be specified")
            #if arguments.cloud:
            arguments.cloud = cloud
            provider = Provider(name=arguments.cloud)
            result = provider.sync(NAMES=arguments.NAMES)
            print(provider.Print(result,
                                 kind='volume',
                                 output=arguments.output))
            # else:
            #     raise NotImplementedError

        elif arguments.purge:
            arguments.cloud = arguments.cloud or cloud
            provider = Provider(name=arguments.cloud)
            provider.purge(**arguments)
            result = provider.list()
            print(provider.Print(result, kind='volume', output=arguments.output))

