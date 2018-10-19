"use strict";
const pulumi = require("@pulumi/pulumi");
const aws = require("@pulumi/aws");

module.exports.mkDash = function(name, instances) {
  let dashBody = pulumi.all(instances.map(i => i.id)).apply(
    (iids) => {
      let x = defineMetrics(iids);
      return JSON.stringify({
      widgets: [
        {type: "metric",
         properties: {
	   metrics: x,
           period: 300,
           stat: "Average",
           region: "us-west-2",
           title: "EC2 Instance CPU"
         }
        }
      ]
      })
    })
  return new aws.cloudwatch.Dashboard(name, {
	dashboardName: name,
	dashboardBody: dashBody
  })
};

module.exports.mkStatusAlarmsForInstances = function(prefix,topic,instances) {
  let alarms = pulumi.all(instances.map(i => i.id))
      .apply(iids => iids.map(id => defineAlarm(prefix,topic,id)));
  return alarms
}

module.exports.mkTopic = function(name) {
  return new aws.sns.Topic(name)
}

function defineMetrics(instanceIds) {
  return instanceIds.map(id => ["AWS/EC2", "CPUUtilization", "InstanceId", id])
}

function defineAlarm(prefix, topic, instanceId) {
  var metrics = ["StatusCheckFailed",
		 "StatusCheckFailed_Instance",
		 "StatusCheckFailed_System"];
  return metrics.map(function(metricName){
    return new aws.cloudwatch.MetricAlarm(
      prefix + "-" + metricName + "-alarm-" + instanceId, {
	comparisonOperator: "GreaterThanOrEqualToThreshold",
	evaluationPeriods: 2,
	metricName: metricName,
	namespace: "AWS/EC2",
	dimensions: {"InstanceId": instanceId },
	period: 60,
	statistic: "Maximum",
	threshold: 1,
	alarmDescription: "Alerts on " + metricName + "failure.",
	alarmActions: [topic.arn.apply(x => x)]
      })
  })
}
