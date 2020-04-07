import oyaml as yaml
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.volume.Provider import Provider


#from cloudmesh.management.configuration.Name import Name as VolumeName



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
            volume delete NAMES
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

            volume register which
                TODO: describe

            volume register [NAME] [--cloud=CLOUD] [ARGUMENTS...]
                TODO: describe

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
                      [ARGUMENTS...]
                Creates a volume

            volume status [NAMES]
                      [--cloud=CLOUD]
            volume attach [NAMES] [--vm=VM]
                Attatch volume to a vm

            volume detach [NAMES]
                Dettatch volume from a vm

            volume delete NAMES
                Delete the named volumes

            volume migrate NAME FROM_VM TO_VM
                 TODO: not yet implemented
                 Migrate volume from one vm to another vm between different
                 regions, services or providers. `

            volume sync FROM_VOLUME TO_VOLUME
                TODO: not yet implemented
                Volume sync alows for data to shared bewteen two volumes.

        """

        VERBOSE(arguments)
        variables = Variables()

        def get_last_volume():
            cm = CmDatabase()
            cloud = arguments['--cloud'] or variables["cloud"]
             #how to get updated cloud names? or only search the last volume in --cloud?
            last_entry = cm.find(cloud=cloud, kind='volume')[-1]
            cm.close_client()
            for tag in last_entry['Tags']:
                if tag['key'] == 'Name':
                    name = tag['Value']
                else:
                    raise ("Please name the volume!")
            return name

        def create_name():

            """
            Gregor suggests to use

            from cloudmesh.management.configuration.Name import Name as VolumeName

            config = Config()

            n = VolumeName(
                    user=config["cloudmesh.profile.username"],
                    kind="volume",
                    path=f"{config.location}/volume.yaml",
                    schema="{user}-volume-{counter}"
                    counter=1)
            n.incr()
            counter = n.get()

            :return:
            """

            # please edit ~ /.cloudmesh / volume.yaml as following:
            # counter: 1
            # kind: volume

            config = Config()
            directory = f"{config.location}"
            volume_yaml = path_expand(f"{directory}/volume.yaml")


            try:
                with open(volume_yaml) as file:
                    dic = yaml.load(file, Loader=yaml.FullLoader)
                counter = dic["counter"]
                user = dic["user"]
                created_name = f"{user}-{cloud}-{counter}"
                dic["counter"] += 1
                with open(volume_yaml, 'w') as file:
                    documents = yaml.dump(dic, file)
            except:
                Console.error("the volume.yaml file does not exist."
                              "You need to implement "
                              "the case so it gets autogenerated")
                raise NotImplementedError

            return created_name

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

        arguments.NAME = arguments.NAME or variables["volume"] #or get_last_volume()
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

            config = Config()
            clouds = list(config["cloudmesh.volume"].keys())
            for cloud in clouds:
                active = config[f"cloudmesh.volume.{cloud}.cm.active"]
                if active:
                    p = Provider(name=cloud)
                    deleted = []
                    for name in names:
                        result = p.delete(name) # returns None if it is not in the cloud
                        if result:
                            deleted.append(name)
                        if len(deleted) > 0:
                            for name in deleted:
                                del names[name]

            """
            2 spaces not fout !

            cloudmesh:
                volume:
                    aws1:                    
                        cm:
                            active: cloudmesh.cloud.aws.cm.active

            names = Parametrs.expnad(arguments.NAMES)



            config = Config()
            clouds = list(config["cloudmesh.volume"].keys())

            for cloud in clouds : 
                active = config[f"cloudmesh.volume.{cloud}.cm.active"]

                if active:
                    found = []
                    # from cloudmesh.volume.Provider import Provider
                    p = Provider(name=cloud)
                    for name in names:
                        volume = p.list(name=name)
                            found = found.append(name)
                    p.destroy(','.join(found)
                    # delete all found volumes in the cloud
            """

        elif arguments.attach:

            # cloud from variable['volume']
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

            banner(f"Attach {arguments.NAMES} to {arguments.vm}")
            provider = Provider(name=arguments.cloud)
            for name in names:
                result = provider.attach(name, vm)
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))

        elif arguments.detach:
            #
            # this has a bug as the general provider needs a serach that finds
            # the vm given a volume name to find the vm it is attached to
            # this way you can write just a loop such as
            #
            # for volume in volumes:
            #    v = provider.serach(volume)
            #    if v['vm'] and v['cm.cloud'] == v['cm.cloud']:
            #        result = provider.detach(name)
            #
            # or something similar dependent on how you defined the datastructure
            # cm. for a volume
            #

            volumes = arguments.NAMES or variables["volume"]
            if volumes is None:
                Console.error ("No volumes specified or found")
                return ""

            volumes = Parameter.expand(volumes)

            banner(f"Detach {volumes}")

            for name in volumes:
                volume = Provider.search(name=name)
                cloud = volume["cm"]["cloud"]
                provider = Provider(name=cloud)
                result = provider.detach(name=name)

                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))












'''
        elif arguments.status:
            cm = CmDatabase()
            banner(arguments)
            if arguments.NAMES:
                variables['volume'] = arguments.NAMES
                print("arguments.NAMES",arguments.NAMES)
            if arguments['--cloud']:
                variables['cloud'] = arguments['--cloud']
            #clouds, names = Arguments.get_cloud_and_names("status", arguments,
            #                                              variables)
            # gets status from database
            #provider = Provider(name=cloud)
            cursor = cm.db[f'{cloud}-volume']
            print(cloud)
            status = []
            for name in arguments.NAMES:
                for node in cursor.find({'Name': name}):
                    status.append(node)
            print(status)
            #provider.Print(status, output=arguments.output, kind="status")
            return ""
'''




'''
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
        
        elif arguments.list:
            if arguments.NAMES:
                raise NotImplementedError
                names = Parameter.expand(arguments.NAMES)
                for name in names:
                    # kind = cm.kind
                    provider = Provider(name=name)
                    # result = provider.list(???)
                    result = provider.list()
            elif arguments.cloud:
                provider = Provider(name=arguments.cloud)
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
    
        
'''


'''    
        cm = CmDatabase()

        if arguments.list and arguments.refresh:
            banner(f'get in if arguments.list, arguments.list={arguments.list}')
            print("arguments.NAMES",arguments)

            if arguments.NAMES:
                arguments.NAMES = list(arguments.NAMES.split(","))
                #find record in mondoDB through volume names

                for name in arguments.NAMES:
                    entry = cm.find_name(name)[0]['cm']
                    name = entry['cloud']
                    provider = Provider(name=name)
                    result = provider.list(**arguments)
                    print(provider.Print(result,
                                         kind='volume',
                                         output=arguments.output))


            elif arguments.cloud:
                banner(f'get in arguments.cloud, arguments.cloud = {arguments.cloud}')
                provider = Provider(name=arguments.cloud)
                result = provider.list(**arguments)
                print(provider.Print(result,
                                      kind='volume',
                                      output=arguments.output))

            elif arguments.vm:
                #need to add vm name to volume when doing volume add
                #get record from mongoDB through vm name --> get cloud --> Provider(name=cloud)
                raise NotImplementedError


            elif arguments.region:
                #find mongoDB record through region --> get cloud --> Provider(name=cloud)

                raise NotImplementedError


        elif arguments.list and arguments.refresh == None:
            
            #print out results in mongoDB
            if arguments.NAMES:

                arguments.NAMES = list(arguments.NAMES.split(","))
                # find record in mondoDB through volume names

                for name in arguments.NAMES:
                    result = cm.find_name(name)
                    print(provider.Print(result,
                                         kind='volume',
                                         output=arguments.output))

            elif arguments.cloud:
                result = cm.find(cloud=arguments.cloud, kind="volume")
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))

            elif arguments.vm:
                #need to add vm name to volume when doing volume add
                raise NotImplementedError
                result = cm.find(vm=arguments.vm, kind='volume')
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))

            elif arguments.region:
                raise NotImplementedError
                result = cm.find(region=arguments.region, kind='volume')
                print(provider.Print(result,
                                     kind='volume',
                                     output=arguments.output))

        return ""

'''


