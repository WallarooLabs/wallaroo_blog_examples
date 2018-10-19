"use strict";
const pulumi = require("@pulumi/pulumi");
const aws = require("@pulumi/aws");
const fs = require("fs");
const cw = require("./cloudwatch");

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

function outputs(instance) {
  return { "name": instance.tags["Name"],
	   "instanceId": instance.id,
	   "publicDns": instance.publicDns,
	   "privateIp": instance.privateIp }
}

function dashboardUrl(name) {
  return name.apply(function(n){
    return ("https://us-west-2.console.aws.amazon.com/" +
	    "cloudwatch/home?region=us-west-2#dashboards:name=" +
	    n)
  })
}


let metrics_host = instance("classifier-metrics_host");
let initializer = instance("classifier-initializer");
let workers = [];
for(var i=0; i<clusterSize-1; i++){
  workers.push(instance("classifier-"+(i+1).toString()));
}
let allInstances = [metrics_host, initializer].concat(workers);
let dashboard = cw.mkDash("classifier-dashboard", allInstances);
let alarmTopic = cw.mkTopic("classifier-alarms");
let alarms = cw.mkStatusAlarmsForInstances("classifier", alarmTopic, allInstances);

exports.metrics_host = [outputs(metrics_host)];
exports.initializer = [outputs(initializer)];
exports.workers = workers.map(outputs);
exports.dashboard = dashboardUrl(dashboard.dashboardName);
exports.alarmTopic = alarmTopic.displayName.apply(n => n)
//exports.alerts = alerts.map(a => a.urn.apply(n => n))
