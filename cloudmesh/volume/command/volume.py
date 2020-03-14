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
            volume list [--vm=VMNAME]
                        [--region=REGION]
                        [--cloud=CLOUD]
                        [--refresh]
                        [--dryrun]
            volume create NAME
                      [--size=SIZE]
                      [--volumetype=VOLUME_TYPE]
                      [--description=DESCRIPTION]
                      [--dryrun]
                      [ARGUMENTS...]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              --vm=VMNAME                      specify the name of vm
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

            #
            # this is not what the command needs as you implemented something different
            #
            name = arguments.NAME or variables['volume']

            if name is None:
                Console.error("No volume specified")
            else:
                provider = Provider(name=name)
                # result = provider.list(???)
                result = provider.list()
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))
            return ""

        elif arguments.create:

            params = arguments.ARGUMENTS
            print (params)

            parameters = {}
            for p in params:
                key, value = p.split("=", 1)
                parameters[key] = value

            print (parameters)

        Console.error("This is just a sample")
        return ""
