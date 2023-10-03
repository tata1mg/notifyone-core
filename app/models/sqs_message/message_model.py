class SQSMessage:

    def __init__(self, sqs_message):
        self.id = sqs_message['MessageId']
        self.receipt_handle = sqs_message['ReceiptHandle']
        self.body = sqs_message['Body']
        self.attributes = SQSAttribute(sqs_message['Attributes'])
        self.message_attributes = SQSMessageAttribute(sqs_message.get('MessageAttributes') or dict())


class SQSAttribute:

    def __init__(self, attributes):
        self.approximate_receive_count = int(attributes['ApproximateReceiveCount'])


class SQSMessageAttribute:

    def __init__(self, message_attributes):
        message_attributes = message_attributes or dict()
        self.compressed_message = 'compressedMessage' in message_attributes and message_attributes['compressedMessage']['StringValue'] == 'yes'
