# Provisioning and running a multi-node Pandas-based Classification Batch Job with Wallaroo

Please see [the corresponding blog post](http://example.com) for a quick run-down of this project.

## How to run this code

0. Sign up for pulumi & get token
1. `make setup`  -- set up local virtualenv & pulumi stack definition
2. `make up CLUSTER_SIZE=2`     -- spin up cluster
3. `make run-cluster INPUT_SIZE=1000000`
4. `make get-results` -- fetch zipped results file
5. `make down` -- shut down cluster

## Prerequisites

On ubuntu:

```
sudo apt-get install -y python virtualenv python-pip make nodejs npm jq zip
sudo pip install awscli
curl -fsSL https://get.pulumi.com | sh
```
