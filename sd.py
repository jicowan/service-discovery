import boto3
import json
import argparse
from texttable import Texttable

sd_client = boto3.client('servicediscovery', region_name='us-east-1')
ecs_client = boto3.client('ecs', region_name='us-east-1')
ec2_resource = boto3.resource('ec2', region_name='us-east-1')
r53_client = boto3.client('route53', region_name='us-east-1')

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser('create')
    parser_create.add_argument("--vpc", help="the VPC ID you want to associate with the namespace", required=True)
    parser_create.add_argument("--namespace", help="the DNS namespace for the service", required=True)
    parser_create.add_argument("--service", help="the name of your service", required=True)
    #parser_create.add_argument("--task", help="the task definition family name")
    parser_create.set_defaults(func=handler_create)

    parser_delete = subparsers.add_parser('delete')
    parser_delete.add_argument("--namespace-id", help="the DNS namespace ID")
    parser_delete.add_argument("--service-id", help="the ID of the service")
    parser_delete.set_defaults(func=handler_delete)

    parser_describe = subparsers.add_parser('describe')
    parser_describe.add_argument("--namespace-id", help="the DNS namespace ID")
    parser_describe.set_defaults(func=handler_describe)

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument("--namespaces", action='store_true')
    parser_list.add_argument("--services", action='store_true')
    parser_list.set_defaults(func=handler_list)

    args = parser.parse_args()
    args.func(args)


def handler_create(args):
    vpc_id = args.vpc
    service_name = args.service
    #task_name = args.task
    namespace_name = args.namespace
    validate_vpcid(vpc_id)
    #validate_task_name(task_name)
    namespace_id = create_namespace(namespace_name, vpc_id)
    service = create_service(service_name, namespace_id)
    header = ['Namespace-Id', 'Service-Id', 'Service-Arn']
    values = [[namespace_id, service['Id'], service['Arn']]]
    print print_table(header, values)
    # print json.dumps(sd_client.list_services().pop('Services'), indent=4)
    # create_ecs_service(service_name, service['Arn'], task_name)

def handler_delete(args):
    service_id = args.service_id
    namespace_id = args.namespace_id
    if service_id != None:
        delete_service(service_id)
    if namespace_id != None:
        delete_namespace(namespace_id)

def handler_describe(args):
    namespace_id = args.namespace_id
    zone_id = get_zone_id(namespace_id)
    print json.dumps(list_resource_records(zone_id), indent=4)

def handler_list(args):
    namespaces = args.namespaces
    services = args.services
    if namespaces:
        get_namespaces()
    if services:
        get_services()

def get_zone_id(namespace_id):
    try:
        zone_id = sd_client.get_namespace(Id=namespace_id)['Namespace']['Properties']['DnsProperties']['HostedZoneId']
    except Exception as e:
        print e
    return zone_id

def delete_service(service_id):
    try:
        sd_client.delete_service(Id=service_id)
    except Exception as e:
        print e
        exit()

def delete_namespace(namespace_id):
    try:
        sd_client.delete_namespace(Id=namespace_id)
    except Exception as e:
        print e
        exit()

def validate_vpcid(vpcid):
    try:
        vpc = ec2_resource.Vpc(vpcid)
        vpc.load()
    except Exception as e:
        print "VPC %s could not be found" % vpcid
        exit()
    return True

def validate_task_name(task_name):
    try:
        ecs_client.describe_task_definition(taskDefinition=task_name)
    except Exception as e:
        print "Task %s could not be found" % task_name
        exit()
    return True

def create_task_definition():
    # Register a FARGATE task definition
    ecs_client.register_task_definition(
        family='first-run-task-definition',
        networkMode='awsvpc',
        containerDefinitions=[
            {
                "name": "sample-app",
                "image": "httpd:2.4",
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80,
                        "protocol": "tcp"
                    }
                ],
                "essential": True,
                "entryPoint": [
                    "sh",
                    "-c"
                ],
                "command": [
                    "/bin/sh -c \"echo '<html> <head> <title>Amazon ECS Sample App</title> <style>body {margin-top: 40px; background-color: #333;} </style> </head><body> <div style=color:white;text-align:center> <h1>Amazon ECS Sample App</h1> <h2>Congratulations!</h2> <p>Your application is now running on a container in Amazon ECS.</p> </div></body></html>' >  /usr/local/apache2/htdocs/index.html && httpd-foreground\""
                ]
            },
        ],
        requiresCompatibilities=[
            'FARGATE',
        ],
        cpu='256',
        memory='512'
    )

def create_ecs_service(service_name, service_arn, task_name):
    # Create a service using the service discovery service name
    ecs_client.create_service(
        #TODO create cluster if 'Fargate' cluster doesn't exist
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
    )

def create_namespace(namespace_name, vpc_id):
    '''Create DNS namespace for service'''
    namespaces = sd_client.list_namespaces()['Namespaces']
    for name in namespaces:
        if namespace_name == name['Name']:
            return name['Id']
    operation_id = sd_client.create_private_dns_namespace(Name=namespace_name, Vpc=vpc_id)['OperationId']
    namespace_id = sd_client.get_operation(OperationId=operation_id)['Operation']['Targets']['NAMESPACE']
    while True:
        #TODO handle when status equals FAIL
        #print sd_client.get_operation(OperationId=operation_id)
        if sd_client.get_operation(OperationId=operation_id)['Operation']['Status'] == 'SUCCESS':
            break
    return namespace_id


def create_service(service_name, namespace_id):
    '''Create service registry name and save Arn'''
    response = sd_client.create_service(Name=service_name, DnsConfig={
            'NamespaceId': namespace_id,
            'DnsRecords': [
                {
                    'Type': 'A',
                    'TTL': 300
                }
            ]
        },
        HealthCheckCustomConfig={
            'FailureThreshold': 1
        }
    )
    service = {
        'Arn': response['Service']['Arn'],
        'Id': response['Service']['Id']
    }
    return service

def list_resource_records(zone_id):
    response = r53_client.list_resource_record_sets(HostedZoneId=zone_id).pop('ResourceRecordSets')
    return response

def get_namespaces():
    namespaces = sd_client.list_namespaces()['Namespaces']
    namespace_keys = list(namespaces[0].viewkeys())
    namespace_values = []
    for name in namespaces:
        namespace_values.append(list(name.viewvalues()))
    print print_table(namespace_keys, namespace_values)

def get_services():
    services = sd_client.list_services()['Services']
    service_keys = list(services[0].viewkeys())
    service_values = []
    for service in services:
        service_values.append(list(service.viewvalues()))
    print print_table(service_keys, service_values)

def print_table(header, rows):
    table = Texttable()
    table.header(header)
    table.add_rows(rows, header=False)
    return table.draw() + "\n"

main()