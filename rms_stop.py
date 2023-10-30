import json

import boto3
import time 
def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')
    # The ID of the EC2 instance you want to stop
    instance_id = 'i-0e87d7ccd5b8b4f2c'
    
    response = ec2.stop_instances(InstanceIds=[instance_id])
    
    return response
