import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('WeatherReadings')

# Escanea todos los items
response = table.scan()
data = response['Items']

# Borra cada item
with table.batch_writer() as batch:
    for item in data:
        batch.delete_item(
            Key={
                'PK': item['PK'],
                'SK': item['SK']
            }
        )
