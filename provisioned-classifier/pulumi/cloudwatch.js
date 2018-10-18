"use strict";
const aws = require("@pulumi/aws")

module.exports.dashboard = function(name, instances) {
  return new aws.cloudwatch.Dashboard(name, {
    dashboardName: name,
    dashboardBody: JSON.stringify({
        widgets: [
            {type: "metric",
             properties: {
	       metrics: defineMetrics(instances),
               period: 300,
               stat: "Average",
               region: "us-west-2",
               title: "EC2 Instance CPU"
             }
            }
        ]
      })
  })
};

function identity(x) { return x };

function defineMetrics(instances) {
  return instances.map(function(i) {
    return ["AWS/EC2", "CPUUtilization", "InstanceId", x]
  })
}

/*
module.exports.mkTopic = function(name) {
  return new aws.sns.Topic(name)
}

module.exports.mkStatusAlarmForInstance = function(prefix,topic,instance) {
  var metrics = ["StatusCheckFailed",
		 "StatusCheckFailed_Instance",
		 "StatusCheckFailed_System"];
  return metrics.map(function(metric){
     return new aws.cloudwatch.MetricAlarm(
       prefix + "-" + metric + "-alarm-" + instanceId, {
	 comparisonOperator: "GreaterThanOrEqualToThreshold",
	 evaluationPeriods: 2,
	 metricName: "CPUUtilization",
	 namespace: "AWS/EC2",
	 dimensions: ["InstanceId", instanceId],
	 period: 60,
	 statistic: "Maximum",
	 threshold: 1,
	 alarmDescription: "Alerts on " + metric + "failure.",
	 alarmActions: [topic.arn.apply(identity)]
       })
  })
}
*/

module.exports.dashboard = function(name, instanceIds) {
  return new aws.cloudwatch.Dashboard(name, {
    dashboardName: name,
    dashboardBody: JSON.stringify({
        widgets: [
            {type: "metric",
             properties: {
	       metrics: defineMetrics(instanceIds),
               period: 300,
               stat: "Average",
               region: "us-west-2",
               title: "EC2 Instance CPU"
             }
            }
        ]
      })
  })
};
