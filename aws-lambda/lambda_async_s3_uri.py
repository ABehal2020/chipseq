# python lambda_async_s3_uri.py 'https://www.encodeproject.org/search/?searchTerm=H3K4ME3&type=Experiment&replication_type=isogenic&assembly=GRCh38&award.rfa=ENCODE4&format=json'

import time

start_time = time.time()

from itertools import combinations_with_replacement
import multiprocessing
import boto3
import json
import sys
from s3_uri import fetch_encsr_encff, sequential_encsr_encff

def format(args):
    bed_paths = fetch_encsr_encff(args)

    # generating unique pairs of bed files to correlate
    bed_pairs = list(combinations_with_replacement(bed_paths, 2))

    num_bed_pairs = len(bed_pairs)

    bed_formatted = []

    for bed_pair, i in zip(bed_pairs, range(len(bed_pairs))):
        file1 = bed_pair[0][19:]
        file2 = bed_pair[1][19:]
        bed_formatted.append('{"file1": "' + file1 + '", "file2": "' + file2 + '"}')

    return bed_formatted, num_bed_pairs

def asyncInvokeLambda(payload):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName='arn:aws:lambda:us-west-2:618537831167:function:jaccard3',
        # provisioned concurrency
        # FunctionName='arn:aws:lambda:us-west-2:618537831167:function:jaccard:provisioned',
        InvocationType='Event',
        LogType='None',
        Payload=payload
        # Qualifier='$LATEST'
    )

    return response

def poll1():
    # Get the service resource
    sqs = boto3.resource('sqs')

    queue = sqs.get_queue_by_name(QueueName='jaccard3-success')

    for message in queue.receive_messages():
        messageOne = json.loads(message.body)
        message.delete()

    return messageOne

def poll_all(num_bed_pairs):
    messagesList = []
    processedList = []

    for x in range(num_bed_pairs):
        messagesList.append(poll1())

    for x in range(len(messagesList)):
        processedList.append(messagesList[x]['responsePayload'])

    print(processedList)
    print(len(processedList))

def main(args):
    processes = []
    payload_formatted, num_bed_pairs = format(args)

    for payload in payload_formatted:
        p = multiprocessing.Process(target=asyncInvokeLambda, args=(payload,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    print('All AWS Lambda Asynchrous Invocations Triggered --- %.2f seconds ---' % (time.time() - start_time))

    poll_all(num_bed_pairs)

    print('Total time --- %.2f seconds ---' % (time.time() - start_time))

if __name__ == '__main__':
    main(sys.argv[1:])