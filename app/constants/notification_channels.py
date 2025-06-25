from commonutils.utils import CustomEnum


class NotificationChannels(CustomEnum):
    EMAIL = 'email'
    SMS = 'sms'
    WHATSAPP = 'whatsapp'
    PUSH = 'push'

    def __str__(self) -> str:
        return self.value

    @classmethod
    def get_sent_to_for_channel(cls, channel, request_body) -> list:
        # For email, sms, and whatsapp only one send address is supported.
        send_address = list()
        if channel in [cls.EMAIL.value]:
            send_address = request_body.get('to', {}).get('email') or list()
            send_address = [send_address[0]] if send_address else list()
        elif channel in [cls.SMS.value, cls.WHATSAPP.value]:
            send_address = request_body.get('to', {}).get('mobile') or list()
            send_address = [send_address[0]] if send_address else list()
        elif channel in [cls.PUSH.value]:
            send_address = request_body.get('to', {}).get('device') or list()
        return send_address

    @classmethod
    def get_source_identifier_for_event(cls, event_name, request_body):
        # TODO add more logic for other apps of needed
        source_identifier = None
        if 'body' in request_body:
            body = request_body['body'] or dict()
            if 'order' in body:
                order = body['order'] or dict()
                if 'order_id' in order or 'appointment_id' in order:
                    source_identifier = order.get('order_id') or order.get('appointment_id')
        return source_identifier
    
