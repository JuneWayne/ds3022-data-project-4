import boto3
import random
import string
import time
import datetime
import json
import os

BUCKET_NAME = 'wkt7ne-access'

def generate_test_event():
    # event_key is an epoch timestamp for now. It should be cast as a string but not in the long form with a decimal point.
    event_key = str(int(time.time()))
    # building_code is a random string of 1 uppercase letter and 2 digits
    building_code = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.digits, k=2))
    # building_door_id is a random string of 2 digits
    building_door_id = ''.join(random.choices(string.digits, k=2))
    # access_time is a current date time stamp
    access_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # user_identity is a random string of 3 lowercase letters, 1 digit, and 1 lowercase letter
    user_identity = ''.join(random.choices(string.ascii_lowercase, k=3)) + ''.join(random.choices(string.digits, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=1))

    # write these as a json file and upload to the s3 bucket
    data = {
        'event_key': event_key,
        'building_code': building_code,
        'building_door_id': building_door_id,
        'access_time': access_time,
        'user_identity': user_identity
    }
    print(data)
    try:
        with open('test-event.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error writing to file: {e}")
        return None

    try:
        s3 = boto3.client('s3')
        s3.upload_file('test-event.json', BUCKET_NAME, f'test-event-{event_key}.json')
        # then delete the file
        os.remove('test-event.json')
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
    return data

if __name__ == '__main__':
    generate_test_event()