# NOT USING ANYMORE - OLD/OUTDATE

import boto3
import json
import sys
from lambda_async_s3_uri import num_bed_pairs

def poll1():
    # Get the service resource
    sqs = boto3.resource('sqs')

    queue = sqs.get_queue_by_name(QueueName='jaccard3-success')

    for message in queue.receive_messages():
        messageOne = json.loads(message.body)
        print(messageOne)
        # message.delete()

    return messageOne

def poll_all():
    messagesList = []
    for x in range(num_bed_pairs):
        oneMessage = poll1()
        messagesList.append(oneMessage)

    print(messagesList)
    print(len(messagesList))

def main(args):
    # poll_all()
    print(num_bed_pairs)

if __name__ == '__main__':
    main(sys.argv[1:])

'''
all_messages = []
some_messages = queue.receive_messages(MaxNumberOfMessages=10)
while len(some_messages > 0):
    all_messages.extend(json.loads(some_messages.body))
    some_messages = queue.receive_messages(MaxNumberOfMessages=10)

print(all_messages)
print(len(all_messages))
'''

