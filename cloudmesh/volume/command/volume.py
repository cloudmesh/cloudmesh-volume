from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.volume.api.manager import Manager
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE

class VolumeCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_volume(self, args, arguments):
        """
        ::

          Usage:
                volume create [name]
                  [--size SIZE]
                  [--type <volume-type>]
                  [--image <image> | --snapshot <snapshot> | --source <volume>]
                  [--description <description>]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """
 

        VERBOSE(arguments)

        if arguments.create:
            #volume create [name]
                  #[--size SIZE]
                  #[--type VOLUME-TYPE]
                  #[--image IMAGE | --snapshot SNAPSHOT | --source VOLUME]
                  #[--description DESCRIPTION]
            print("create volume")
            p = ?
            size = arguments["--size"]
            p.create(name=name, size=size, voltype=voltype, image=image, snapshot=snapshot, source=source, description=description)
            
        elif arguments.list:
            print("option b")

        Console.error("This is just a sample")
        return ""
