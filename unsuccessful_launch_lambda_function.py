import boto3
def lambda_handler(event, context):
    client = boto3.client('autoscaling')
    
    if event ['detail-type'] == "EC2 Instance Launch Unsuccessful":
        group_name = event ["detail"]["AutoScalingGroupName"]
        print ("EC2 instance launch failed in autoscaling group " + group_name)
        
        response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[group_name])
        if "MixedInstancesPolicy" in response ['AutoScalingGroups'][0]:
            if response ['AutoScalingGroups'][0]["MixedInstancesPolicy"]["InstancesDistribution"]["OnDemandPercentageAboveBaseCapacity"] != 100:
                print ("{0} group is using some percentage of spot instances. Making it 100% on-demand".format(group_name))
                config = response ['AutoScalingGroups'][0]["MixedInstancesPolicy"]
                config ["InstancesDistribution"]["OnDemandPercentageAboveBaseCapacity"] = 100
                del (config ['LaunchTemplate'] )
                update_response = client.update_auto_scaling_group(AutoScalingGroupName = group_name, 
                                    MixedInstancesPolicy = config)
                print (update_response)
            else:
                raise Exception ("Autoscaling group is already set to have 100% on demand instance")
