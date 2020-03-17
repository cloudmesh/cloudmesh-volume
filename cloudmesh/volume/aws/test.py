from cloudmesh.mongo.CmDatabase import CmDatabase
import yaml
from cloudmesh.management.configuration.name import Name

def get_last_volume():
    cm = CmDatabase()
    cloud = arguments['--cloud'] or variables["cloud"]
    # how to get updated cloud names? or only search the last volume in --cloud?
    last_entry = cm.find(cloud=cloud, kind='volume')[-1]
    for tag in last_entry['Tags']:
        if tag['key'] == 'Name':
            name = tag['Value']
        else:
            raise ("Please name the volume!")
    return name


def create_name():

    with open(r"/Users/xingu/.cloudmesh/names.yaml") as file:
        list = yaml.load(file, Loader=yaml.FullLoader)
    counter = list["counter"]
    generated_name = Name(
        cloud='aws1',
        user="xin",
        kind="volume",
        schema='{user}-{cloud}-{counter}',
        counter=counter)
    list["counter"] += 1
    with open("/Users/xingu/.cloudmesh/names.yaml", 'w') as file:
        documents = yaml.dump(list, file)
    return print(generated_name)


if __name__ == '__main__':
    #print(get_last_volume())
    create_name()
