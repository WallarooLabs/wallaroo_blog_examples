# Provisioning and running a multi-node Pandas-based Classification Batch Job with Wallaroo

Please see [the corresponding blog
post](https://blog.wallaroolabs.com/2018/10/spinning-up-a-wallaroo-cluster-is-easy/)
for a quick run-down of this project.

## How to run this code

0. Sign up for pulumi & get an access token configured on you dev machine
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
