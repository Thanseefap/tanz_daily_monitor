import json

import boto3
import time 
def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')
    # The ID of the EC2 instance you want to stop
    instance_id = 'i-0e87d7ccd5b8b4f2c'
    
    response = ec2.start_instances(InstanceIds=[instance_id])
    
    time.sleep(125)
    
    
    commands_to_run = [
    'cd /home/ec2-user/tanz_daily_monitor && screen -dmS bot_session_name python3 -u rms_umma.py']
    
    # Send commands using SSM
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands': commands_to_run
        }
    )

    command_id = response['Command']['CommandId']
    return {
        'statusCode': 200,
        'body': {
            'message': 'Commands sent!',
            'command_id': command_id
        }
    }
    # Ideally, you should use waiter or a loop to check instance state.
    # In this example, a sleep is used for simplicity.
    
