from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.debug import VERBOSE

# from cloudmesh.volume.openstack.Provider import Provider

class VolumeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_volume(self, args, arguments):
        """
        ::

          Usage:
                volume create [NAME]
                  [--size=SIZE]
                  [--type=VOLUME-TYPE]
                  [--image=IMAGE | --snapshot=SNAPSHOT | --source =VOLUME]
                  [--description=DESCRIPTION]

          This command does some useful things.

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

        """

        name = arguments.NAME

        map_parameters(arguments,
                       "dryrun",
                       "size",
                       "type",
                       "image",
                       "descripton",
                       "mem"
                       )

        VERBOSE(arguments)

        if arguments.create:
            #volume create [name]
                  #[--size SIZE]
                  #[--type VOLUME-TYPE]
                  #[--image IMAGE | --snapshot SNAPSHOT | --source VOLUME]
                  #[--description DESCRIPTION]
            print("create volume")
            # provider = Provider()
            size = arguments["--size"]
            volumetype = arguments["--type"]
            #provider.create(name=name, size=size, voltype=voltype, image=image, snapshot=snapshot, source=source, description=description)
            
        elif arguments.list:
            print("option b")

        Console.error("This is just a sample")
        return ""
