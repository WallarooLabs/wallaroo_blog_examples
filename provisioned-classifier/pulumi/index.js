"use strict";
const pulumi = require("@pulumi/pulumi");
const aws = require("@pulumi/aws");
const fs = require("fs");

let instanceType = "c5.4xlarge";
let ami = fs.readFileSync("latest.ami").toString();
let clusterSize = parseInt(fs.readFileSync("cluster_size").toString(), 10);
let pubKey = fs.readFileSync("../ssh_pubkey_in_ec2_format.pub").toString();
let keyPair = new aws.ec2.KeyPair("ClassifierKey", {publicKey: pubKey});
let secGrp = new aws.ec2.SecurityGroup(
  "ClassifierSecGrp",
  {ingress: [{ "protocol": "tcp", "fromPort": 22,
	       "toPort": 22, "cidrBlocks": ["0.0.0.0/0"] },
             { "protocol": "tcp", "fromPort": 4000,
	       "toPort": 4000, "cidrBlocks": ["0.0.0.0/0"] },
	     { "protocol": "tcp", "fromPort": 3999,
	       "toPort": 65535, "cidrBlocks": ["172.16.0.0/12"]}
	     ],
   egress: [{ "protocol": "tcp", "fromPort": 0,
	      "toPort": 65535, "cidrBlocks": ["0.0.0.0/0"] }
	   ]});

function instance(name) {
  return new aws.ec2.Instance(
    name,
    {associatePublicIpAddress: true,
     instanceType: instanceType,
     securityGroups: [secGrp.name],
     ami: ami,
     tags: {"Name": name},
     keyName: keyPair.keyName})
}

let coordinator = instance("classifier-coordinator");
let initializer = instance("classifier-initializer");
let workers = [];
for(var i=0; i<clusterSize-1; i++){
  workers.push(instance("classifier-"+(i+1).toString()));
}

exports.coordinator = [
  {"name": coordinator.tags["Name"],
   "publicDns": coordinator.publicDns,
   "privateIp": coordinator.privateIp}];

exports.initializer = [
  {"name": initializer.tags["Name"],
   "publicDns": initializer.publicDns,
   "privateIp": initializer.privateIp}];

exports.workers =
  workers.map(function(s){
    return { "name": s.tags["Name"],
	     "publicDns": s.publicDns,
	     "privateIp": s.privateIp}
  });



