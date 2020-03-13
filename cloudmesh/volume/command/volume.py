from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.variables import Variables
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
            volume list [--vm=VM NAME]
                        [--region=REGION]
                        [--cloud=CLOUD]
                        [--refresh]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              --vm=VM_NAME                      specify the name of vm
              --region=REGION                   specify the region
              --cloud=CLOUD                     specify cloud name
              --refresh                         refresh

        """

        VERBOSE(arguments)

        name = arguments.NAME
        path = arguments.PATH

        map_parameters(arguments,
                       "cloud",
                       "vm",
                       "region"
                       "cloud",
                       "refresh"
                       )


        if arguments.list:

            variables = Variables()

            name = arguments.NAME or variables['volume']

            if name is None:
                Console.error("No volume specified")
            else:
                provider = Provider(name=name)

                print(provider.Print(list,
                                     kind='volume',
                                     output=arguments.output))
            return ""

        Console.error("This is just a sample")
        return ""
