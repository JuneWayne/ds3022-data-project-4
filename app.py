import os
from chalice import Chalice
import boto3
from botocore.exceptions import ClientError
import json

app = Chalice(app_name='s3-events')
app.debug = True

# Set the values in the .chalice/config.json file.
S3_BUCKET = os.environ.get('APP_BUCKET_NAME', '')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', '')

@app.on_s3_event(bucket=S3_BUCKET, events=['s3:ObjectCreated:*'], suffix='.json')
def s3_handler(event):
    # get the event, pull the file from s3, read it, and insert into DDB
    # log the event that triggered the lambda
    app.log.debug(f"Received bucket event: {event.bucket}, key: {event.key}")
    # read the file form s3 and parse it 
    data = get_s3_object(event.bucket, event.key)
    # insert data into dynamodb table 
    insert_data_into_dynamodb(data)
    # return the data value 
    return data

def get_s3_object(bucket, key):
    # get the object from s3
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        app.log.error(f"Error getting object from S3: {e}")
        print(e)

def insert_data_into_dynamodb(data):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    try:
        response = table.put_item(
            Item={
                'event_key': data['event_key'],
                'building_code': data['building_code'],
                'building_door_id': data['building_door_id'],
                'access_time': data['access_time'],
                'user_identity': data['user_identity']
            }
        )
        app.log.debug(f"DynamoDB response: {response}")
        return response
    except ClientError as e:
        app.log.error(f"Error inserting data into DynamoDB: {e}")
        raise e

@app.route('/access', methods=['GET'])
def get_access():
    # return all records from DDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    try:
        items = table.scan()['Items']
        sorted_items = sorted(items, key=lambda x: x['access_time'], reverse=True)
        return sorted_items
    except ClientError as e:
        app.log.error(f"Error scanning DynamoDB table: {e}")
        raise e
    # sorted_items = sorted(items, key=lambda x: x['access_time'], reverse=True)
    # return sorted_items
    