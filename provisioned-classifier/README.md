# Provisioning and running a multi-node Pandas-based Classification Batch Job with Wallaroo

Please see [the corresponding blog
post](https://blog.wallaroolabs.com/2018/10/spinning-up-a-wallaroo-cluster-is-easy/)
for a quick run-down of this project.

## How to run this code

0. Sign up for [Pulumi] and get an access token configured on your dev machine
1. `make setup`  -- set up local virtualenv & pulumi stack definition
2. `make up CLUSTER_SIZE=2`     -- spin up infrastructure
3. `make run-cluster INPUT_SIZE=1000000`  -- feed 1000000 lines of CVS data into cluster
4. `make get-results` -- fetch zipped results file into output/results.tgz
5. `make down` -- shut down cluster


## Prerequisites

To installed required software on an ubuntu system, run the following commands:

```
sudo apt-get install -y python virtualenv python-pip make nodejs npm jq zip
sudo pip install awscli
curl -fsSL https://get.pulumi.com | sh
```

## Opinionated Wallaroo Provisioning and Deployment

As part of the creation of this application, we've developed an opioninated
provisioning and deployment process for a Wallaroo batch job process. This
opinionated process assumes you have an AWS account, and that you sign up for
[Pulumi] access.


### How it works:

### `make setup`

This command sets up the [Pulumi stack] definition and installs a [Virtualenv]
environment, which includes the libraries needed to run the `classifier`
application.

The Pulumi stack definition is written in Javascript, and can be found under
`pulumi/index.js`. This file is version-controlled, and can be modified and
checked in as the requirements for your project's infrastructure change.


### `make up CLUSTER_SIZE=<N>`

This command executes `pulumi up` to ensure that the infractructure defined in
`pulumi/index.js` is created in AWS. There are several pieces of
meta-information that are required for the stack to come up successfully:


#### `ONCALL.json`

This file contains a JSON array of strings, each containing a phone nubmer in
[E.164] format. Each of the phone numbers listed in this array will be
subscribed for a CloudWatch SMS Alarm if any of the machines in the stack
become unresponsive to [EC2 status checks]. By default, it is empty, which
means no one will get notified.


#### `ssh_key.pem` and `ssh_pubkey_in_ec2_format.pub`

These two files represent one [SSH keypair], stored in two different formats. They
are generated with `ssh-keygen` if they don't already exist in the project root
directory. The first file is a standard SSH private/public key bundle that is
used by Ansible and plain ssh (with `ssh THE_HOST -i ./ssh_key.pem`), while the
second one represents only the public key, and is used by Pulumi to ensure
access to fresh EC2 instances.

If you delete `ssh_key.pem`, you will lose SSH access (and Ansible access) to
the currently provisioned stack.


#### `pulumi/cluster_size`

This file holds the last value of the environment variable CLUSTER_SIZE that
was passed in to `make up`. It is expected to be an integer, and represents the
number of worker processes that you want to provision to perform the
classification job.

When `make up CLUSTER_SIZE=<N>` completes its execution:

  1) The three files mentioned above will be present on your machine

  2) N worker instances and 1 metrics host will exist in EC2, accessible with
  `ssh_key.pem`. The first of these instances will be called `initializer`, due
  to the special role it plays during cluster startup.

  3) If you specified any phone numbers in `ONCALL.json`, SMS alerts will have
  been set up for the given numbers.

  4) The file `urls.txt` will contain an http URL for the Monitoring Hub, and
  an https url for the CloudWatch dashboard that was generated for this stack.


At this stage, the cluster is ready to receive data at the [TCP Source] on the
`initializer` instance. If you would like to make any changes to the stack
definition, the number of instances, or the list of on-call numbers, you may
make them now, and then simply re-run `make up`. Unless you're changing the
number of provisioned instances, you do not need to provide the `CLUSTER_SIZE`
environment variable again.



### `make run-cluster INPUT_LINES=NNNNNN`

This invocation uses [Ansible] to compress and upload the `classifier`
application to the provisioned infrastructure, and then start up and wire all
the components of this particular batch job:

1) A cluster of 7 × `CLUSTER_SIZE` Wallaroo processes, where the first process
is started on the `initializer` EC2 instance, and it's control port is used by
all the other workers to connect and form a complete cluster. Once all workers
have joined, the initializer node begins listening for CSV data on TCP port
`8888`.

2) A `data_receiver` process on the metrics host. This process listens for
framed data on TCP port `9999` and writes it to a local file, `results.log`.

3) The `send.py` process, on the metrics host, which generates `INPUT_LINES` of
fake CSV data and sends it to the TCP source on port `8888` of the
`initializer` instance. After all the lines have been sent and accepted, it
sends out a `\EOF` byte and shuts down.

4) The Wallaroo Monitoring Hub, which accepts metrics data from all the workers
and displays it in real-time.

When all of these components have started working, Ansible will wait for the
`results.log` file to grow up to `INPUT_LINES` lines, then shut down the
cluster processes, zip the file, and download it to the developer's machine.


### `make down`

This command de-provisions all the infrastructure provisioned by `make
up`. This includes the metrics host, the CloudWatch dashboard, and the Alarms.




## Tools and components used

### Ansible

[Ansible] is a tool that automates software
provisioning, configuration management, and application deployment. As part of
our deployment process, we use Ansible to automate the following:

  - Upload the Wallaroo application to any running machines we have provisioned
  - Run our Wallaroo application and the Wallaroo Metrics UI. the Wallaroo
    application is started on any machine that is specified as a "worker" or
    "initializer"
  - Await results of our batch process and when complete, compresses them to a file
  - Shutdown our Wallaroo cluster once the batch job is complete

Ansible playbooks are found in `ansible/*yml`, and our invocations of Ansible
itself rely on the SSH keys described above.

If at any point you'd like to access the provisioned hosts directly, you can
examine their public DNS names in `ansible/inventory.yml`, and use
`ssh_key.pem` to log in.

```
$ tail -n3 ansible/inventory.yml
ec2-34-214-235-85.us-west-2.compute.amazonaws.com ansible_user=ubuntu private_ip=172.31.16.147
ec2-54-202-83-168.us-west-2.compute.amazonaws.com ansible_user=ubuntu private_ip=172.31.27.250
ec2-18-236-154-202.us-west-2.compute.amazonaws.com ansible_user=ubuntu private_ip=172.31.27.147

$ ssh ubuntu@ec2-18-236-154-202.us-west-2.compute.amazonaws.com -i ssh_key.pem 'echo $(hostname)'
Warning: Permanently added the ECDSA host key for IP address '172.31.27.147' to the list of known hosts.
ip-172-31-27-147

````


### Amazon EC2

[Amazon EC2] provides resizable compute capacity in the cloud and is our choice
for cloud infrastructure. We use a custom built Amazon Machine Image (AMI) with
Wallaroo and needed tools pre-installed to reduce configuration time.

<!-- TODO: EC2 screenshot -->


### Amazon CloudWatch

[Amazon CloudWatch] is a monitoring and management service that provides data
and actionable insights to our Amazon EC2 cluster. It is specfically used to
setup a CPU monitoring dashboard for each Wallaroo worker and also to alert
"on-call" developers via SMS when an EC2 instance fails a system check.

<!-- TODO: Cloudwatch screenshot -->


### Pulumi

[Pulumi] is a tool to create, deploy, and manage cloud
native applications and infrastructure. We use Pulumi to startup a defined set
of machines for our Wallaroo batch job using Amazon EC2. Pulumi is also used to
setup a few monitoring tools we use as part of Amazon's CloudWatch.

[Amazon CloudWatch]: https://aws.amazon.com/cloudwatch/
[Amazon EC2]: https://aws.amazon.com/ec2/
[Ansible]: https://www.ansible.com/
[Pulumi]: https://pulumi.io/
[Pulumi stack]: https://pulumi.io/reference/stack.html
[Virtualenv]: https://docs.python-guide.org/dev/virtualenvs/
[E.164]: https://www.twilio.com/docs/glossary/what-e164
[EC2 status checks]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-system-instance-status-check.html
[SSH keypair]: https://help.github.com/articles/connecting-to-github-with-ssh/
[TCP Source]: https://docs.wallaroolabs.com/book/appendix/tcp-decoders-and-encoders.html
