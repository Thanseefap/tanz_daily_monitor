import boto3

# Create a DynamoDB client
dynamodb_client = boto3.client('dynamodb',region_name='us-east-1')

# Define the table name
table_name = 'Shoonya'

# Define the partition key value
partition_key_value = 'OTP'

# Define the updated values for other attributes
updated_attribute1 = '1111'

# Update the item using the partition key
response = dynamodb_client.update_item(
    TableName=table_name,
    Key={
        'metrices': {'S': partition_key_value}
    },
    UpdateExpression='SET attribute1 = :value1',
    ExpressionAttributeValues={
        ':value1': {'S': updated_attribute1}
    }
)

# Check the response for success/failure
if response['ResponseMetadata']['HTTPStatusCode'] == 200:
    print('Item updated successfully')
else:
    print('Failed to update the item')
