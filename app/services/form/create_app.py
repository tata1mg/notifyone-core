import json


class CreateAppFormData:

    _form_data = {
        'name': 'create_app',
        'type': 'collection',
        'label': 'Create App',
        'editable': True,
        'bordered': True,
        'disabled': False,
        'size': 'medium',
        'order': [
            'name',
            'callback_url',
            'callback_events'
        ],
        'components': {
            'name': {
                'name': 'name',
                'type': 'text',
                'label': 'Name',
                'editable': True,
                'bordered': True,
                'disabled': False,
                'size': 'medium',
                'rules': [
                    {
                        'required': True,
                        'message': 'This is a required Field'
                    }
                ],
                'newline': False,
                'offset': 0,
                'span': 24,
                'placeholder': '...'
            },
            'callback_url': {
                'name': 'callback_url',
                'type': 'url',
                'label': 'Callback URL',
                'editable': True,
                'bordered': True,
                'disabled': False,
                'size': 'medium',
                'newline': False,
                'offset': 0,
                'span': 24,
                'placeholder': '...'
            },
            'callback_events': {
                'name': 'callback_events',
                'type': 'collection',
                'label': 'Callback Events',
                'editable': True,
                'bordered': True,
                'disabled': False,
                'size': 'medium',
                'order': [
                    'email',
                    'sms',
                    'push',
                    'whatsapp'
                ],
                'components': {
                    'email': {
                        'name': 'email',
                        'type': 'select',
                        'label': 'Email',
                        'editable': True,
                        'bordered': True,
                        'disabled': False,
                        'size': 'medium',
                        'newline': False,
                        'offset': 0,
                        'span': 24,
                        'options': [
                            {
                                'value': 'OPENED',
                                'label': 'OPENED'
                            },
                            {
                                'value': 'REJECTED',
                                'label': 'REJECTED'
                            },
                            {
                                'value': 'SENT',
                                'label': 'SENT'
                            },
                            {
                                'value': 'DEFERRED',
                                'label': 'DEFERRED'
                            },
                            {
                                'value': 'DELIVERED',
                                'label': 'DELIVERED'
                            },
                            {
                                'value': 'BOUNCED',
                                'label': 'BOUNCED'
                            },
                            {
                                'value': 'CLICKED',
                                'label': 'CLICKED'
                            },
                            {
                                'value': 'SPAM',
                                'label': 'SPAM'
                            },
                            {
                                'value': 'UNSUBSCRIBED',
                                'label': 'UNSUBSCRIBED'
                            },
                            {
                                'value': 'DELAYED',
                                'label': 'DELAYED'
                            },
                            {
                                'value': 'COMPLAINT',
                                'label': 'COMPLAINT'
                            },
                            {
                                'value': 'UNKNOWN',
                                'label': 'UNKNOWN'
                            }
                        ],
                        'dataFetchMode': 'STATIC',
                        'showSearch': False,
                        'mode': 'multiple'
                    },
                    'sms': {
                        'name': 'sms',
                        'type': 'select',
                        'label': 'SMS',
                        'editable': True,
                        'bordered': True,
                        'disabled': False,
                        'size': 'medium',
                        'newline': False,
                        'offset': 0,
                        'span': 24,
                        'options': [
                            {
                                'value': 'SENT',
                                'label': 'SENT'
                            },
                            {
                                'value': 'QUEUED',
                                'label': 'QUEUED'
                            },
                            {
                                'value': 'FAILED',
                                'label': 'FAILED'
                            },
                            {
                                'value': 'EXPIRED',
                                'label': 'EXPIRED'
                            },
                            {
                                'value': 'OPT_OUT',
                                'label': 'OPT_OUT'
                            },
                            {
                                'value': 'REJECTED',
                                'label': 'REJECTED'
                            },
                            {
                                'value': 'ACCEPTED',
                                'label': 'ACCEPTED'
                            },
                            {
                                'value': 'DELIVERED',
                                'label': 'DELIVERED'
                            },
                            {
                                'value': 'UNDELIVERED',
                                'label': 'UNDELIVERED'
                            },
                            {
                                'value': 'INVALID_NUMBER',
                                'label': 'INVALID_NUMBER'
                            },
                            {
                                'value': 'UNKNOWN',
                                'label': 'UNKNOWN'
                            }
                        ],
                        'dataFetchMode': 'STATIC',
                        'showSearch': False,
                        'mode': 'multiple'
                    },
                    'push': {
                        'name': 'push',
                        'type': 'select',
                        'label': 'Push',
                        'editable': True,
                        'bordered': True,
                        'disabled': False,
                        'size': 'medium',
                        'newline': False,
                        'offset': 0,
                        'span': 24,
                        'options': [

                        ],
                        'dataFetchMode': 'STATIC',
                        'showSearch': False,
                        'mode': 'multiple'
                    },
                    'whatsapp': {
                        'name': 'whatsapp',
                        'type': 'select',
                        'label': 'WhatsApp',
                        'editable': True,
                        'bordered': True,
                        'disabled': False,
                        'size': 'medium',
                        'newline': False,
                        'offset': 0,
                        'span': 24,
                        'options': [
                            {
                                'value': 'SENT',
                                'label': 'SENT'
                            },
                            {
                                'value': 'DELIVERED',
                                'label': 'DELIVERED'
                            },
                            {
                                'value': 'READ',
                                'label': 'READ'
                            },
                            {
                                'value': 'FAILED',
                                'label': 'FAILED'
                            },
                            {
                                'value': 'UNKNOWN',
                                'label': 'UNKNOWN'
                            }
                        ],
                        'dataFetchMode': 'STATIC',
                        'showSearch': False,
                        'mode': 'multiple'
                    }
                },
                'cardType': None
            }
        },
        'cardType': None
    }

    @classmethod
    def get(cls):
        return json.dumps(cls._form_data)
