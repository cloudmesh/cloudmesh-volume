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
                volume list
                              [--vm=VM NAME]
                              [--region=REGION]
                              [--cloud=CLOUD]
                              [--refresh]
                              [--dryrun]
                volume migrate NAME
                              [--fregion=FROM REGION]
                              [--tregion=TO REGION]
                              [--fservice=FROM SERVICE]
                              [--tservice=TO SERVICE]
                              [--fcloud=FROM CLOUD]
                              [--tcloud=TO CLOUD]
                              [--cloud=CLOUD]
                              [--region=REGION]
                              [--service=SERVICE]
                              [--dryrun]

          A simple abstraction layer to manage Cloud Volumes for AWS, Azure, Google, Openstack and Multipass

          Arguments:
              NAME   volume name

          Options:
              --size=SIZE                specify size of volume
              --type=VOLUME-TYPE         specify type of volume
              --image=IMAGE              specify source
              --description=DESCRIPTION  specify description
              --vm=VM NAME               specify the name of vm
              --region=REGION            specify the region
              --cloud=CLOUD              specify the provider
              --refresh                  refresh
              --fregion=FROM REGION      specify the region where the volume is moving from
              --tregion=TO REGION        specify the region where the volume is moving to
              --fservice=FROM SERVICE    specify the service where the volume is moving from
              --tservice=TO SERVICE      specify the service where the volume is moving to
              --fcloud=FROM CLOUD        specify the provider where the volume is moving from
              --tcloud=TO CLOUD          specify the provider where the volume is moving to
              --cloud=CLOUD              specify the provider where the volume is moving within
              --region=REGION            specify the region where the volume is moving within
              --service=SERVICE          specify the service where the volume is moving within

          Commands:
            Create volume
              cms volume create NAME
              Optionally you can provide size, volume type, image or description
            Delete volume NAME
            List volume
              cms volume list
              Optionally you can provide vm name, region, provider, refresh
            Migrate volume
              cms volume migrate NAME
              Optionally you can provide fregion, tregion, fservice, tservice, fcloud, tcloud, cloud, region, service


        """

        name = arguments.NAME

        map_parameters(arguments,
                       "dryrun",
                       "size",
                       "type",
                       "image",
                       "descripton",
                       "vm",
                       "region"
                       "cloud",
                       "refresh",
                       "fregion",
                       "tregion",
                       "fservice",
                       "tservice",
                       "fcloud",
                       "tcloud",
                       "service"
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

        elif arguments.list:
            if arguments.dryrun:
                banner("dryrun list")
            else:
                # provider = Provider()
                # provider.list(vm=vm, region=region, cloud=cloud, refresh=TRUE)
                print("list volume is not yet implemented!")

        elif arguments.migrate:
            if arguments.dryrun:
                banner("dryrun list")
            else:
                # provider = Provider()
                # provider.list(name=name, fregion=fregion, tregion=tregion, fservice=fservice, tservice=tservice,
                # fcloud=fcloud, tcloud=tcloud, cloud=cloud, region=region, service=service)
                print("migrate volume is not yet implemented!")

        Console.error("This is just a sample")
        return ""
