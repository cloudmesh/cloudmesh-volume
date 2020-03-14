from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.variables import Variables
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.volume.Provider import Provider
from cloudmesh.common.parameter import Parameter
import textwrap


class VolumeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_volume(self, args, arguments):
        """
        ::

          Usage:
            volume register which
            volume register [NAME] [--cloud=CLOUD] [ARGUMENTS...]
            volume list [--vm=VM]
                        [--region=REGION]
                        [--cloud=CLOUD]
                        [--refresh]
                        [--dryrun]
            volume create [NAME]
                      [--size=SIZE]
                      [--volumetype=TYPE]
                      [--description=DESCRIPTION]
                      [--dryrun]
                      [ARGUMENTS...]
            volume delete [NAME]
            volume migrate NAME FROM_VM TO_VM
            volume sync FROM_VOLUME TO_VOLUME

          This command manages volumes accross different clouds

          Arguments:
              NAME   the name of the volume

          Options:
              --vm=VMNAME        The name of the virtual machine
              --region=REGION    The name of the region
              --cloud=CLOUD      The name of the cloud
              --refresh          If refresh the information is taken from the cloud
              --volumetype=TYPE  The type of the volume

          Description:

             TBD
        """

        def get_last_volume():
            Console.error("Get last volume not yet implemented")
            raise NotImplementedError

        VERBOSE(arguments)

        variables = Variables()
        name = arguments.NAME or variables["volume"] or get_last_volume()

        path = arguments.PATH

        map_parameters(arguments,
                       "volumetype",
                       "cloud",
                       "vm",
                       "region"
                       "cloud",
                       "refresh"
                       )

        if arguments.register and arguments.which:

            providers = Provider.get_kind()

            Console.info("Available Volume Cloud Providers")
            print()
            print("    " + "\n    ".join(providers))
            print()

        elif arguments.register:

            Console.info("Registering a volume to cloudmesh yaml")

            parameters = Parameter.arguments_to_dict(arguments.ARGUMENTS)

            print()
            print("    Name:", name)
            print("    Cloud:", arguments.cloud)
            print("    Arguments:", parameters)
            print()

            raise NotImplementedError

        elif arguments.list:

            provider = Provider(name=name)
            # result = provider.list(???)
            result = provider.list()
            print(provider.Print(result,
                                 kind='volume',
                                 output=arguments.output))
            return ""

        elif arguments.create:

            parameters = Parameter.arguments_to_dict(arguments.ARGUMENTS)

            print(parameters)

        elif arguments.delete:

            name = arguments.NAME

            if name is None:
                # get name form last created volume
                raise NotImplementedError

            provider = Provider(name=name)
            provider.delete(name=name)

        elif arguments.migrate:

            print(arguments.name)
            print(arguments.FROM_VM)
            print(arguments.TO_VM)

            raise NotImplementedError

        elif arguments.sync:

            print(arguments.FROM_VOLUME)
            print(arguments.TO_VOLUME)

            raise NotImplementedError

        return ""
