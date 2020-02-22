from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import banner

# from cloudmesh.volume.openstack.Provider import Provider

class VolumeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_volume(self, args, arguments):
        """
        ::

          Usage:
                volume create NAME
                              [--size=SIZE]
                              [--type=VOLUME-TYPE]
                              [--image=IMAGE | --snapshot=SNAPSHOT | --source =VOLUME]
                              [--description=DESCRIPTION]
                              [--dryrun]
                volume delete NAME [--dryrun]

          A simple abstraction layer to manage Cloud Volumes for AWS, Azure, Google, Openstack and Multipass

          Arguments:
              NAME   volume name

          Options:
              --size=SIZE                specify size of volume
              --type=VOLUME-TYPE         specify type of volume
              --image=IMAGE              specify source
              --description=DESCRIPTION  specify description

          Commands:
            Create volume
              cms volume create NAME
              Optionally you can provide size, volume type, image or description
            Delete volume NAME

        """

        name = arguments.NAME

        map_parameters(arguments,
                       "dryrun",
                       "size",
                       "type",
                       "image",
                       "descripton",
                       )

        VERBOSE(arguments)

        if arguments.create:
            if arguments.dryrun:
                banner("dryrun create")
            else:
                size = arguments["--size"]
                volumetype = arguments["--type"]
                #provider = Provider()
                #provider.create(name=name, size=size, voltype=voltype, image=image, snapshot=snapshot, source=source, description=description)
                print("create volume is not yet implemented!")
        elif arguments.delete:
            if arguments.dryrun:
                banner("dryrun delete")
            else:
                # provider = Provider()
                # provider.delete(name=name)
                print("delete volume is not yet implemented!")

        Console.error("This is just a sample")
        return ""
