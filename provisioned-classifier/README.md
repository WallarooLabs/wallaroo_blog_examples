# Provisioning and running a multi-node Pandas-based Classification Batch Job with Wallaroo

Please see [the corresponding blog
post](https://blog.wallaroolabs.com/2018/10/spinning-up-a-wallaroo-cluster-is-easy/)
for a quick run-down of this project.

## How to run this code

0. Sign up for [Pulumi] and get an access token configured on you dev machine
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
provisioning and deployment process for a Wallaroo batch job process. In this
section we'll break down some of the tools required and their roles in this
process.

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

### Amazon EC2

[Amazon EC2] provides resizable compute capacity in the cloud and is our choice
for cloud infrastructure. We use a custom built Amazon Machine Image (AMI) with
Wallaroo and needed tools pre-installed to reduce configuration time.

### Amazon CloudWatch

[Amazon CloudWatch] is a monitoring and management service that provides data
and actionable insights to our Amazon EC2 cluster. It is specfically used to
setup a CPU monitoring dashboard for each Wallaroo worker and also to alert
"on-call" developers via SMS when an EC2 instance fails a system check.

### Pulumi

[Pulumi] is a tool to create, deploy, and manage cloud
native applications and infrastructure. We use Pulumi to startup a defined set
of machines for our Wallaroo batch job using Amazon EC2. Pulumi is also used to
setup a few monitoring tools we use as part of Amazon's CloudWatch.

[Amazon CloudWatch]: https://aws.amazon.com/cloudwatch/
[Amazon EC2]: https://aws.amazon.com/ec2/
[Ansible]: https://www.ansible.com/
[Pulumi]: https://pulumi.io/
