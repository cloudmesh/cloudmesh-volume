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
                        [--type=VOLUME_TYPE]
                        [--image=IMAGE | --snapshot=SNAPSHOT | --source =VOLUME]
                        [--description=DESCRIPTION]
                        [--dryrun]
                volume delete NAME [--dryrun]
                volume list
                        [--vm=VM_NAME]
                        [--region=REGION]
                        [--cloud=CLOUD]
                        [--refresh]
                        [--dryrun]
                volume migrate NAME FVM TVM
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
                volume set NAME
                        [--size=SIZE]
                        [--description=DESCRIPTION]
                        [--state=STATE]
                        [--type=VOLUME-TYPE]
                        [--retype_policy=RETYPE_POLICY]
                        [--bootable | --non-bootable]
                        [--read_only | --read_write]
                        [--dryrun]
                volume show NAME [--dryrun]
                volume sync VOLA VOLB
                        [--region=REGION]
                        [--cloud=CLOUD]
                        [--dryrun]
                volume unset NAME
                        [--property=PROPERTY]
                        [--image_property=IMAGE_PROPERTY]
                        [--dryrun]

          A simple abstraction layer to manage Cloud Volumes for
            AWS, Azure, Google, Oracle, OpenStack and Multipass

          Arguments:
              NAME  volume name
              FVM   name of vm where volume will be moved from
              TVM   name of vm where volume will be moved to
              VOLA  volume name to sync from
              VOLB  volume name to sync to

          Options:
              --size=SIZE                       specify size of volume
              --type=VOLUME_TYPE                specify type of volume
              --image=IMAGE                     specify source
              --description=DESCRIPTION         specify description
              --vm=VM NAME                      specify the name of vm
              --region=REGION                   specify the region
              --cloud=CLOUD                     specify the provider
              --refresh                         refresh
              --fregion=FROM REGION             specify the region where the
                                                    volume will be moved from
              --tregion=TO REGION               specify the region where the
                                                    volume will be moved to
              --fservice=FROM SERVICE           specify the service where the
                                                    volume will be moved from
              --tservice=TO SERVICE             specify the service where the
                                                    volume will be moved to
              --fcloud=FROM CLOUD               specify the provider where the
                                                    volume will be moved from
              --tcloud=TO CLOUD                 specify the provider where the
                                                    volume will be moved to
              --cloud=CLOUD                     specify the provider where the
                                                    volume will be moved within
              --service=SERVICE                 specify the service where the
                                                    volume will be moved within
              --state=STATE                     specify the state of the volume
              --retype_policy=RETYPE_POLICY     specify the retype-policy
              --property=PROPERTY               specify key for volume
              --image_property=IMAGE_PROPERTY   specify image of compute
                                                    instance in volume


          Commands:
            Create volume
              cms volume create NAME
              Optionally you can provide size, volume type, image or description
            Delete volume NAME
            List volume
              cms volume list
              Optionally you can provide vm name, region, provider, refresh
            Migrate volume
              cms volume migrate NAME FVM TVM
              Optionally you can provide fregion, tregion, fservice, tservice,
                fcloud, tcloud, cloud, region, service
            Set volume
              cms volume set NAME
              Optionally you can provide size, description, state, type,
                retype policy
            Show volume
              cms volume show NAME
            Volume sync
              cms volume sync VOLA VOLB
              Optionally you can provide region, cloud
            Unset volume
              cms volume unset NAME
              Optionally you can provide property, image-property


        """

        name = arguments.NAME
        fvm = arguments.FVM
        tvm = arguments.TVM
        vola = arguments.VOLA
        volb = arguments.VOLB

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
                       "service",
                       "state",
                       "retype_policy",
                       "property",
                       "image_property"
                       )

        VERBOSE(arguments)

        if arguments.create:



            if arguments.dryrun:
                banner("dryrun create")
            else:
                size = arguments["--size"]
                volumetype = arguments["--type"]
                #provider = Provider()
                #provider.create(name=name, size=size, voltype=voltype,
                #   image=image, snapshot=snapshot, source=source,
                #   description=description)
                print("create volume is not yet implemented!")


                #volume create NAME
                #       [--size=SIZE]
                #       [--type=VOLUME-TYPE]
                #       [--image=IMAGE | --snapshot=SNAPSHOT | --source =VOLUME]
                #       [--description=DESCRIPTION]
                #       [--dryrun]

                # top: from ??? import Provider
                # volume = Provider()
                # r = volume.create( name = arguments.name,
                #   size=argument.size, ???????? )
                #
                # do something with the r
                # print (r) # is typically json

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
                # provider.migrate(name=name, fvm=fvm, tvm=tvm, fregion=fregion, tregion=tregion,
                #   fservice=fservice, tservice=tservice, fcloud=fcloud,
                #   tcloud=tcloud, cloud=cloud, region=region, service=service)
                print("migrate volume is not yet implemented!")
                
        elif arguments.set:
            if arguments.dryrun:
                banner("dryrun set")
            else:
                # provider = Provider()
                # provider.set(name=name, size=size, description=description,
                #   state=state, voltype=voltype, retype=policy=retype=policy)
                print("set volume is not yet implemented!")
                
        elif arguments.show:
            if arguments.dryrun:
                banner("dryrun show")
            else:
                # provider = Provider()
                # provider.show(name=name)                
                print("show volume is not yet implemented!")

        elif arguments.sync:
            if arguments.dryrun:
                banner("dryrun sync")
            else:
                # provider = Provider()
                # provider.sync(vola=vola, volb=volb,
                #   region=region, cloud=cloud)
                print("volume sync is not yet implemented!")

        elif arguments.unset:
            if arguments.dryrun:
                banner("dryrun unset")
            else:
                # provider = Provider()
                # provider.unset(name=name, property=property,
                #   image-property=image-property)
                print("unset is not yet implemented!")

        Console.error("This is just a sample")
        return ""
