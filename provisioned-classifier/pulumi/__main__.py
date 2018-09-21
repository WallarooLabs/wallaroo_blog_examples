from os import getenv, path
import pulumi
from pulumi_aws import s3,ec2
from subprocess import check_output

instance_type = "c5.4xlarge"

with open("./latest.ami") as f:
    ami = f.readline().strip()

with open("./cluster_size") as f:
    wallaroo_instance_count = int(f.readline().strip())

key_pair = ec2.KeyPair("ClassifierKey",
    public_key=check_output(
        ["ssh-keygen", "-y", "-f", "../ssh_key.pem"]).strip())

security_group = ec2.SecurityGroup("ClassifierSecGrp",
    ingress=[{ "protocol": "tcp", "fromPort": 22,
	       "toPort": 22, "cidrBlocks": ["0.0.0.0/0"] },
             { "protocol": "tcp", "fromPort": 4000,
	       "toPort": 4000, "cidrBlocks": ["0.0.0.0/0"] },
	     { "protocol": "tcp", "fromPort": 3999,
	       "toPort": 65535, "cidrBlocks": ["172.16.0.0/12"]}
    ],
    egress=[{ "protocol": "tcp", "fromPort": 0,
	      "toPort": 65535, "cidrBlocks": ["0.0.0.0/0"] }
    ])

def instance(name):
    return ec2.Instance(name,
                        associate_public_ip_address=True,
                        instance_type=instance_type,
                        security_groups=[security_group.name],
                        ami=ami,
                        tags={"Name": name},
                        key_name=key_pair.key_name)
def worker_name(n):
    return "classifier-%s"%(i+1)

coordinator = instance("classifier-coordinator")
initializer = instance("classifier-initializer")
workers = [instance(worker_name(i)) for i in range(0,wallaroo_instance_count-1)]

pulumi.output('coordinator',
              [{  "name": coordinator.tags["Name"],
                  "public_dns": coordinator.public_dns,
                  "private_ip": coordinator.private_ip}])

pulumi.output('initializer',
              [{  "name": initializer.tags["Name"],
                  "public_dns": initializer.public_dns,
                  "private_ip": initializer.private_ip}])

pulumi.output('workers',
              [ { "name": s.tags["Name"],
                  "public_dns": s.public_dns,
                  "private_ip": s.private_ip}
                for s in workers ])
