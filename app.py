import boto3

# Create a DynamoDB client
dynamodb_client = boto3.client('dynamodb')

# Define the table name
table_name = 'login'

# Define the data to be added
item = {
    'otp': {'458758}
}

# Add the item to the DynamoDB table
response = dynamodb_client.put_item(TableName=table_name, Item=item)

# Check the response for success/failure
if response['ResponseMetadata']['HTTPStatusCode'] == 200:
    print('Data added to DynamoDB successfully')
else:
    print('Failed to add data to DynamoDB')
