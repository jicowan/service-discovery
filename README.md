# service-discovery
A CLI to create service discovery namespaces and register services under those namespaces. You can download the executable from the [/dist](https://github.com/jicowan/service-discovery/tree/master/dist)

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
### Delete
Deletes a service or namespace
```
sd delete [--namespace-id <namespace-id> --service-id <service-id>]
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
