# service-discovery
On 3/18/18 the Elastic Container Service (ECS) added support for service discovery.  To register an ECS service with the Service Discovery Service, you first need to create a namespace.  A namespace is a Route 53 private hosted zone that your ECS services can use to discover other ECS services, e.g. acme.local.  After creating a namespace, you register your service with the Service Discovery Service.  This returns a registry ARN which you add to your ECS service's service definition.  A walk-through of the Service Discovery Service is available [here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html).  As you'll see, there are a lot of steps  involved if you use the AWS CLI.  This is a simple CLI to create service discovery namespaces and register services under those namespaces. You can download the executable from the [/dist](https://github.com/jicowan/service-discovery/tree/master/dist) folder.  This CLI only creates A records and only works in us-east-1 at the moment. 

## Usage
### Create
Creates a namespace and registers a service with a namespace. 
```
sd create [--vpc <vpc-id>] [--namespace <namespace-name>] [--service <service-name>]

Sample output: 
+---------------------+----------------------+---------------------------------+
|    Namespace-Id     |      Service-Id      |           Service-Arn           |
+=====================+======================+=================================+
| ns-jkazzonvbupl7unu | srv-sjjhzf7xwwhvhkdw | arn:aws:servicediscovery:us-    |
|                     |                      | east-1:012345678901:service     |
|                     |                      | /srv-sjjhzf7xwwhvhkdw           |
+---------------------+----------------------+---------------------------------+
```
To register an ECS service with the service discovery service, add the service ARN to the service's service definition. For example: 
```
{
    cluster='fargate',
    serviceName=service_name + '-svc',
    taskDefinition=task_name,
    serviceRegistries=[
        {
            'registryArn': service_arn
        }
    ],
    desiredCount=1,
    platformVersion='1.1.0',
    launchType='FARGATE',
    networkConfiguration={
        'awsvpcConfiguration': {
            'subnets': [
                'subnet-f8bc52a2',
            ],
            'securityGroups': [
                'sg-592a062c',
            ],
            'assignPublicIp': 'ENABLED'
        }
    }
}
```
### Delete
Deletes a service or namespace
```
sd delete [--namespace-id <namespace-id>] [--service-id <service-id>]
```
### List
Ouputs the services and namespaces in a region
```
sd list [--services] [--namespaces]

Sample output: 
+----------------------+------------------------------------------+------------+
|          Id          |                   Arn                    |    Name    |
+======================+==========================================+============+
| srv-sjjhzf7xwwhvhkdw | arn:aws:servicediscovery:us-             | ya         |
|                      | east-1:012345678901:service/srv-         |            |
|                      | sjjhzf7xwwhvhkdw                         |            |
+----------------------+------------------------------------------+------------+

+-------------+---------------------+-----------------------------+------------+
|    Type     |         Id          |             Arn             |    Name    |
+=============+=====================+=============================+============+
| DNS_PRIVATE | ns-jkazzonvbupl7unu | arn:aws:servicediscovery    | yada.local |
|             |                     | :us-east-1:012345678901:nam |            |
|             |                     | espace/ns-jkazzonvbupl7unu  |            |
+-------------+---------------------+-----------------------------+------------+
```
### Describe
Outputs the IP addresses of services registered with the namespace
```
sd describe [--namespace-id <namespace-id>]

Sample output: 
[
    {
        "ResourceRecords": [
            {
                "Value": "ns-1536.awsdns-00.co.uk."
            },
            {
                "Value": "ns-0.awsdns-00.com."
            },
            {
                "Value": "ns-1024.awsdns-00.org."
            },
            {
                "Value": "ns-512.awsdns-00.net."
            }
        ],
        "Type": "NS",
        "Name": "yada.local.",
        "TTL": 172800
    },
    {
        "ResourceRecords": [
            {
                "Value": "ns-1536.awsdns-00.co.uk. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"
            }
        ],
        "Type": "SOA",
        "Name": "yada.local.",
        "TTL": 900
    }
]
```
