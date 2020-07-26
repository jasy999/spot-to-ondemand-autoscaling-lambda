# spot-to-ondemand-autoscaling-lambda
AWS Autoscaling group can have spot instances via [launch templates](https://ec2spotworkshops.com/launching_ec2_spot_instances/asg.html). These spot instances can be taken away by AWS anytime when there is high demand, with a two minute advance notification. These lambda functions along with cloudwatch service events can help us to determine spot instance termination in advance and change them to on-demand instance type to ensure less outage.

## Lambda functions
|Script | Purpose |
|--------------|-------------------|
| termination_alert_lambda_function.py | This function will be triggered when a spot instance is set to be terminated in 2 minutes. It increases the corresponding autoscaling group's instance count by 1 |
| unsuccessful_launch_lambda_function.py | This function will be triggered when an autoscaling group is unable to launch the spot instance. It changes the instance class from spot to on-demand in the corresponding autoscaling group|

## termination_alert_lambda_function.py
This function is designed to be triggered by clouwatch ec2 event type "EC2 Spot Instance Interruption Warning". It retrieves the associated autoscaling group of an EC2 instance and increases the capacity by 1 to enable smooth transition. It does not convert the instance class of an autoscaling group to on-demand yet. An autoscaling group can have multiple instance types and some times this spot instance termination might be happening for a particular instance type. This allows autoscaling group to find another spot instance from the list of configured instance types. For this lambda function to work, we need a cloud watch event and appropriate IAM policy.

A clound watch event in the corresponding region should be created with the following event pattern.
```
{
  "detail-type": [
    "EC2 Spot Instance Interruption Warning"
  ],
  "source": [
    "aws.ec2"
  ]
}
```
This can be done via AWS console following the steps in [this article](https://ec2spotworkshops.com/running_spark_apps_with_emr_on_spot_instances/tracking_spot_interruptions.html). This cloudwatch event should be integrated with the above lambda function via event targets.

Below is the Lambda IAM policy which could enable the script to perform the programmed actions.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "autoscaling:DescribeAutoScalingInstances",
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:SetDesiredCapacity"
            ],
            "Resource": "*"
        }
    ]
}
```

## unsuccessful_launch_lambda_function.py
This function is designed to be triggered by clouwatch autoscaling event type "EC2 Instance Launch Unsuccessful". It converts the instance class of an autoscaling group to on-demand. For this lambda function to work, we need a cloud watch event and appropriate IAM policy.

A clound watch event in the corresponding region should be created with the following event pattern.
```
{
  "source": [
    "aws.autoscaling"
  ],
  "detail-type": [
    "EC2 Instance Launch Unsuccessful"
  ]
}
```
Alternatively, you can also limit this event for a specific set of autoscaling groups.
```
{
  "source": [
    "aws.autoscaling"
  ],
  "detail-type": [
    "EC2 Instance Launch Unsuccessful"
  ],
  "detail": {
    "AutoScalingGroupName": [
      "Autoscaling-Group-Name-1",
      "Autoscaling-Group-Name-2"
    ]
  }
}
```
This can be done via AWS console following the below steps.
1) Open [CloudWatch service page](https://console.aws.amazon.com/cloudwatch/).
2) Click on Rules under Events section in the left panel
3) Click create rule
4) Select event pattern in the event source
5) Select Auto Scaling in the service name
6) Select "Instance Launch and Terminate" in the Event type
7) Check "Specific instance event(s)" option
8) Select "EC2 Instance Launch Unsuccessful" from the dropdown
9) If you want this enabled for all the autoscaling group, then select "Any group name"
10) If you want this enabled for selected set of   autoscaling group, then select "Specific group name(s)" and select autoscaling groups from the dropdown
11) Click "Add target" from the right side panel and add the above lambda function
12) Click configure details and save them by giving a user friendly name.

Below is the Lambda IAM policy which could enable the script to perform the programmed actions.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ec2:GetLaunchTemplateData",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeLaunchTemplates",
                "autoscaling:DescribeAutoScalingGroups",
                "ec2:DescribeVpcs",
                "ec2:DescribeLaunchTemplateVersions",
                "autoscaling:UpdateAutoScalingGroup",
                "ec2:DescribeSubnets"
            ],
            "Resource": "*"
        }
    ]
}
```

## Points to Remember
* The first step of this lambda function is increasing the capacity of autoscaling group, to create new instances in the event of spot instance termination alert, which gives 2 minutes to create a new instance and ensure minimal outage of service. Hence, it is important for the autoscaling group to have maximum capacity set higher than 1.
* It is also important to have autoscaling rules in place to terminate excess instances to avoid underutilization.
* [AWS suggested best practices for spot instances in autscaling groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-purchase-options.html#asg-spot-best-practices)
