from requests import get
from time import sleep
import boto3

session = boto3.session.Session()
print('Session is in region %s' % session.region_name)

if __name__ == '__main__':
    ecs = session.client('ecs')
    print('Watching for ECS tasks')

    cluster = get("http://localhost:51678/v1/metadata").json()['Cluster']
    containerInstanceArn = get("http://localhost:51678/v1/metadata").json()['ContainerInstanceArn']
    print('ECS Cluster name: %', cluster)
    print('ECS ContainerInstance arn: %', containerInstanceArn)

    counter = 0
    while(True):
        response = ecs.describe_container_instances(
            cluster=cluster,
            containerInstances=[containerInstanceArn]
        )
        registeredResources = response['containerInstances'][0]['registeredResources']
        remainingResources = response['containerInstances'][0]['remainingResources']
        CPUregisteredResources = next(item for item in registeredResources if item["name"] == "CPU")
        CPUremainingResources = next(item for item in remainingResources if item["name"] == "CPU")

        if CPUregisteredResources == CPUremainingResources:
            print('No instance tasks')
            counter += 1
        else:
            counter = 0

        if counter >= 60:
            print('Instance idle detected')
            print('Draining node: %s on cluster: %s' % (containerInstanceArn, cluster))
            ecs.update_container_instances_state(
                cluster=cluster,
                containerInstances=[
                    containerInstanceArn,
                ],
                status='DRAINING'
            )
            print('Node Drain successful')
            break
        else:
            sleep(10)
