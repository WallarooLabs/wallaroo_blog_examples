# Provisioning and running a multi-node Pandas-based Classification Batch Job with Wallaroo

Please see [the corresponding blog
post](https://blog.wallaroolabs.com/2018/10/spinning-up-a-wallaroo-cluster-is-easy/)
for a quick run-down of this project.

## Prerequisites

### To install the required software on an Ubuntu system, run the following commands:

```
sudo apt-get install -y python virtualenv python-pip make nodejs npm jq zip ansible
sudo pip install awscli
curl -fsSL https://get.pulumi.com | sh
```

### To ensure Pulumi can run successfully:

Sign up for [Pulumi](https://www.pulumi.com/) & get an [access token](https://app.pulumi.com/account/tokens) configured on your dev machine.

### To ensure your AWS CLI is configured correctly:

Visit [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html). You'll want to make sure your keys have access to the `us-west-2` region.


## How to run this code

1. `make setup`  -- set up local virtualenv & pulumi stack definition
2. `make up CLUSTER_SIZE=2`     -- spin up infrastructure
3. `make run-cluster INPUT_LINES=1000000`  -- feed 1000000 lines of CVS data into cluster
4. `make get-results` -- fetch zipped results file into output/results.tgz
5. `make down` -- shut down cluster

