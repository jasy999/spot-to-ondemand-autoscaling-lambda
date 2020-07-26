import boto3

def lambda_handler(event, context):
    client = boto3.client('autoscaling')
    instance_id = event ["detail"]["instance-id"]
    auto_scale_instance_response = client.describe_auto_scaling_instances(
                                        InstanceIds=[instance_id]
                                    )
    if auto_scale_instance_response ['AutoScalingInstances']:
        auto_scale_group = auto_scale_instance_response ['AutoScalingInstances'][0]['AutoScalingGroupName']
        print ("{0} is part of an autoscaling group {1}".format(
                instance_id, auto_scale_group))
        auto_scale_group_response = client.describe_auto_scaling_groups(
                                        AutoScalingGroupNames=[auto_scale_group]
                                    )
        capacity = auto_scale_group_response["AutoScalingGroups"][0]["DesiredCapacity"]
        
        print ("Changing the capacity of {0} from {1} to {2}".format(
                auto_scale_group,capacity, capacity + 1))
        capacity_response = client.set_desired_capacity(
                                AutoScalingGroupName=auto_scale_group,
                                DesiredCapacity=capacity + 1,
                                HonorCooldown=False
                            )
        print (capacity_response)
    else:
        print (instance_id + " does not belong to an autoscaling group")
