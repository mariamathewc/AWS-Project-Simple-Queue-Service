#!/usr/local/bin/python3
import boto3
# create a boto3 client
client = boto3.client('sqs', region_name='us-east-1')
# create the test queue
# for a FIFO queue, the name must end in .fifo, and you must pass FifoQueue = True
client.create_queue(QueueName='ip_queue.fifo', Attributes={'FifoQueue':'true'})
# get a list of queues, we get back a dict with 'QueueUrls' as a key with a list of queue URLs
queues = client.list_queues(QueueNamePrefix='ip_queue.fifo') # we filter to narrow down the list
test_queue_url = queues['QueueUrls'][0]
# send 100 messages to this queue
for i in range(0,5):
    # we set a simple message body for each message
    # for FIFO queues, a 'MessageGroupId' is required, which is a 128 char alphanumeric string
#    print(i)
    enqueue_response = client.send_message(QueueUrl=test_queue_url, MessageGroupId='1', MessageDeduplicationId=str(i), MessageBody='10.0.0.'+str(i))
    # the response contains MD5 of the body, a message Id, MD5 of message attributes, and a sequence number (for FIFO queues)
    print('Message ID : ',enqueue_response['MessageId'])
# next, we dequeue these messages - 10 messages at a time (SQS max limit) till the queue is exhausted.
# in production/real setup, I suggest using long polling as you get billed for each request, regardless of an empty response
while True:
    messages = client.receive_message(QueueUrl=test_queue_url,MaxNumberOfMessages=10) # adjust MaxNumberOfMessages if needed
    if 'Messages' in messages: # when the queue is exhausted, the response dict contains no 'Messages' key
        abc="default"
        for message in messages['Messages']: # 'Messages' is a list
            # process the messages
            abc=message['Body']
            print(abc)
            # next, we delete the message from the queue so no one else will process it again
            client.delete_message(QueueUrl=test_queue_url,ReceiptHandle=message['ReceiptHandle'])
    else:
        print('Last Input Address:'+abc)
        print('Queue is now empty')
#        print(abc)
        break