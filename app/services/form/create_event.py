class CreateEventFormData:

    _form_data = {
      'name': 'create_event',
      'type': 'collection',
      'label': 'Create Event',
      'editable': True,
      'bordered': True,
      'disabled': False,
      'size': 'medium',
      'order': [
        'app_name',
        'event_name',
        'event_type',
        'callback_enabled',
        'event_priority',
        'email',
        'sms',
        'push',
        'whatsapp'
      ],
      'components': {
        'app_name': {
          'name': 'app_name',
          'type': 'select',
          'label': 'App Name',
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
          'options': [
            {
              'value': 'off2',
              'label': 'off2'
            },
            {
              'value': 'off3',
              'label': 'off3'
            },
            {
              'value': 'off4',
              'label': 'off4'
            },
            {
              'value': 'off5',
              'label': 'off5'
            },
            {
              'value': 'off6',
              'label': 'off6'
            },
            {
              'value': 'off7',
              'label': 'off7'
            },
            {
              'value': 'off',
              'label': 'off'
            },
            {
              'value': 'psp',
              'label': 'psp'
            },
            {
              'value': 'off1',
              'label': 'off1'
            },
            {
              'value': 'diagnostics',
              'label': 'diagnostics'
            },
            {
              'value': 'ecom',
              'label': 'ecom'
            }
          ],
          'dataFetchMode': 'STATIC',
          'showSearch': True
        },
        'event_name': {
          'name': 'event_name',
          'type': 'text',
          'label': 'Event Name',
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
        'event_type': {
          'name': 'event_type',
          'type': 'select',
          'label': 'Event Type',
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
          'options': [
            {
              'value': 'promotional',
              'label': 'PROMOTIONAL'
            },
            {
              'value': 'transactional',
              'label': 'TRANSACTIONAL'
            },
            {
              'value': 'otp',
              'label': 'OTP'
            }
          ],
          'dataFetchMode': 'STATIC',
          'showSearch': False
        },
        'callback_enabled': {
          'name': 'callback_enabled',
          'type': 'switch',
          'label': 'Callback Enabled',
          'editable': True,
          'bordered': True,
          'disabled': False,
          'size': 'medium',
          'newline': False,
          'offset': 0,
          'span': 12,
          'defaultChecked': False
        },
        'event_priority': {
          'name': 'priority',
          'type': 'select',
          'label': 'Priority',
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
          'span': 12,
          'options': [
            {
              'value': 'critical',
              'label': 'CRITICAL'
            },
            {
              'value': 'high',
              'label': 'HIGH'
            },
            {
              'value': 'medium',
              'label': 'MEDIUM'
            },
            {
              'value': 'low',
              'label': 'LOW'
            }
          ],
          'dataFetchMode': 'STATIC',
          'showSearch': False
        },
        'email': {
          'name': 'email',
          'type': 'collection',
          'label': 'Email',
          'editable': True,
          'bordered': True,
          'disabled': False,
          'size': 'medium',
          'order': [
            'description',
            'trigger_limit',
            'subject',
            'content'
          ],
          'components': {
            'description': {
              'name': 'description',
              'type': 'text',
              'label': 'Description',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'newline': False,
              'offset': 0,
              'span': 12,
              'placeholder': '...'
            },
            'trigger_limit': {
              'name': 'trigger_limit',
              'type': 'number',
              'label': 'Trigger Limit',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'tooltip': 'maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)',
              'rules': [
                {
                  'required': True,
                  'message': 'This is a required Field'
                }
              ],
              'newline': False,
              'offset': 0,
              'span': 12,
              'placeholder': '...'
            },
            'content': {
              'name': 'content',
              'type': 'textarea',
              'label': 'Content',
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
              'placeholder': '...',
              'rows': 4
            },
            'subject': {
              'name': 'subject',
              'type': 'text',
              'label': 'Subject',
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
            }
          },
          'cardType': None
        },
        'sms': {
          'name': 'sms',
          'type': 'collection',
          'label': 'SMS',
          'editable': True,
          'bordered': True,
          'disabled': False,
          'size': 'medium',
          'tooltip': 'The following steps have to be performed in order to create a SMS',
          'order': [
            'description',
            'trigger_limit',
            'content'
          ],
          'components': {
            'description': {
              'name': 'description',
              'type': 'text',
              'label': 'Description',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'newline': False,
              'offset': 0,
              'span': 12,
              'placeholder': '...'
            },
            'trigger_limit': {
              'name': 'trigger_limit',
              'type': 'number',
              'label': 'Trigger Limit',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'tooltip': 'maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)',
              'rules': [
                {
                  'required': True,
                  'message': 'This is a required Field'
                }
              ],
              'newline': False,
              'offset': 0,
              'span': 12,
              'placeholder': '...'
            },
            'content': {
              'name': 'content',
              'type': 'textarea',
              'label': 'Content',
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
              'placeholder': '...',
              'rows': 4
            }
          },
          'cardType': None
        },
        'push': {
          'name': 'push',
          'type': 'collection',
          'label': 'Push',
          'editable': True,
          'bordered': True,
          'disabled': False,
          'size': 'medium',
          'order': [
            'device_type',
            'trigger_limit',
            'title',
            'body',
            'target',
            'image'
          ],
          'components': {
            'device_type': {
              'name': 'device_type',
              'type': 'select',
              'label': 'Device Type',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'newline': False,
              'offset': 0,
              'span': 12,
              'options': [
                {
                  'value': 'ALL',
                  'label': 'ALL'
                },
                {
                  'value': 'IOS',
                  'label': 'iOS'
                },
                {
                  'value': 'ANDROID',
                  'label': 'ANDROID'
                }
              ],
              'dataFetchMode': 'STATIC',
              'showSearch': False
            },
            'trigger_limit': {
              'name': 'trigger_limit',
              'type': 'number',
              'label': 'Trigger Limit',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'tooltip': 'maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)',
              'rules': [
                {
                  'required': True,
                  'message': 'This is a required Field'
                }
              ],
              'newline': False,
              'offset': 0,
              'span': 12,
              'placeholder': '...'
            },
            'title': {
              'name': 'title',
              'type': 'text',
              'label': 'Title',
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
            'body': {
              'name': 'body',
              'type': 'text',
              'label': 'Body',
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
            'target': {
              'name': 'target',
              'type': 'select',
              'label': 'Target',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'tooltip': 'the location of page which opens the notification is clicked',
              'rules': [
                {
                  'required': True,
                  'message': 'This is a required Field'
                }
              ],
              'newline': False,
              'offset': 0,
              'span': 24,
              'options': [
                {
                  'value': 'WEB NPS',
                  'label': 'WEB NPS'
                },
                {
                  'value': 'TRACK ORDER',
                  'label': 'TRACK ORDER'
                },
                {
                  'value': 'ORDER HISTORY',
                  'label': 'ORDER HISTORY'
                },
                {
                  'value': 'UPLOAD PRESCRIPTION',
                  'label': 'UPLOAD PRESCRIPTION'
                },
                {
                  'value': 'PRESCRIPTION DETAIL',
                  'label': 'PRESCRIPTION DETAIL'
                },
                {
                  'value': 'DYNAMIC TARGET',
                  'label': 'DYNAMIC TARGET'
                }
              ],
              'dataFetchMode': 'STATIC',
              'showSearch': False
            },
            'image': {
              'name': 'image',
              'type': 'text',
              'label': 'Image',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'newline': False,
              'offset': 0,
              'span': 24,
              'placeholder': '...'
            }
          },
          'cardType': None
        },
        'whatsapp': {
          'name': 'whatsapp',
          'type': 'collection',
          'label': 'WhatsApp',
          'editable': True,
          'bordered': True,
          'disabled': False,
          'size': 'medium',
          'order': [
            'trigger_limit',
            'name'
          ],
          'components': {
            'trigger_limit': {
              'name': 'trigger_limit',
              'type': 'number',
              'label': 'Trigger Limit',
              'editable': True,
              'bordered': True,
              'disabled': False,
              'size': 'medium',
              'tooltip': 'maximum number of times a particular event can be triggered for a particular order (set -1 for infinite times)',
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
            }
          },
          'cardType': None
        }
      },
      'cardType': None
    }

    @classmethod
    def get(cls):
        return cls._form_data
