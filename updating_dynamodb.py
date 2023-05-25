
import boto3

# Create a DynamoDB client with the desired region
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

# Define the table name
table_name = 'Shoonya'

# Define the key and updated value
key = 'metrices'
updated_value = '1111'

# Update the key-value pair in the DynamoDB table
response = dynamodb_client.update_item(
   TableName=table_name,
   Key={
       'metrices': {'S': 'OTP'}  # Assuming 'id' is the primary key
   },
   UpdateExpression='SET #key = :value',
   ExpressionAttributeNames={
       '#key': key
   },
   ExpressionAttributeValues={
       ':value': {'S': updated_value}
   }
)

# Check the response for success/failure
if response['ResponseMetadata']['HTTPStatusCode'] == 200:
   print('Key-value pair updated successfully')
else:
   print('Failed to update the key-value pair')
