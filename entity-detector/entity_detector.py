import boto3
import json
import os
import shutil
import time

comprehend = boto3.client(service_name='comprehend',
                          region_name=os.environ['AWS_REGION'],
                          aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
                          aws_secret_access_key=os.environ['AWS_SECRET_KEY']
                          )

while True:
    for file in os.listdir(os.environ['LANDING_ZONE'].strip('\n')):
        if file.endswith("txt"):
            abs_path = os.path.join(os.environ['LANDING_ZONE'].strip('\n'), file)
            file_handler = open(abs_path, "r+")
            text = file_handler.read()
            cloudwatch_events = boto3.client('events', region_name=os.environ['AWS_REGION'].strip('\n'),
                                             aws_access_key_id=os.environ['AWS_ACCESS_KEY'].strip('\n'),
                                             aws_secret_access_key=os.environ['AWS_SECRET_KEY'].strip('\n'))
            response = cloudwatch_events.put_events(
                Entries=[
                    {
                        'Detail': json.dumps({'text': text}),
                        'DetailType': 'entitySubmitted',
                        'Resources': [
                            'RESOURCE_ARN',
                        ],
                        'Source': 'entity_detector'
                    }
                ]
            )
            print(response['Entries'])
            result = json.dumps(comprehend.detect_entities(Text=text, LanguageCode='en'), sort_keys=True, indent=4)
            client = boto3.client('sns', region_name=os.environ['AWS_REGION'].strip('\n'),
                                  aws_access_key_id=os.environ['AWS_ACCESS_KEY'].strip('\n'),
                                  aws_secret_access_key=os.environ['AWS_SECRET_KEY'].strip('\n'))

            response = client.publish(
                TargetArn=os.environ['ARN'].strip('\n'),
                Message=json.dumps({'default': json.dumps(result)}),
                Subject='entity recognition',
                MessageStructure='json'
            )
            time.sleep(5)
            if os.path.exists(abs_path):
                shutil.move(abs_path, os.path.join(os.environ['COMPLETE_ZONE'].strip('\n'), file))
