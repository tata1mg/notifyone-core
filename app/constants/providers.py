from commonutils.utils import CustomEnum

from app.constants import NotificationChannels


class ProvidersStatus(CustomEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class Providers(CustomEnum):

    AWS_SES = {
        "name": "AWS SES",
        "code": "AWS_SES",
        "logo": "",
        "channels": [
            NotificationChannels.EMAIL.value
        ],
        "configuration": {
            "AWS_REGION": ""
        }
    }

    SPARK_POST = {
        "name": "Spark Post",
        "code": "SPARK_POST",
        "logo": "",
        "channels": [
            NotificationChannels.EMAIL.value
        ],
        "configuration": {
            "API_KEY": "",
            "AWS_ACCESS_KEY_ID": "",
            "AWS_ACCESS_KEY_SECRET": "",
        }
    }

    AWS_SNS = {
        "code": "AWS_SNS",
        "name": "AWS SNS",
        "logo": "",
        "channels": [
            NotificationChannels.SMS.value
        ],
        "configuration": {
            "REGION_NAME": "",
            "AWS_ACCESS_KEY_ID": "",
            "AWS_SECRET_ACCESS_KEY": "",
            "SNS_ENDPOINT_URL": "",
            "MESSAGE_ATTRIBUTES": {
                "sms_type": "",
                "sender_id": ""
            }
        }
    }

    PLIVO = {
        "name": "Plivo",
        "code": "PLIVO",
        "logo": "",
        "channels": [
            NotificationChannels.SMS.value
        ],
        "configuration": {
            "PLIVO_AUTH_ID": "",
            "PLIVO_AUTH_TOKEN": "",
            "PLIVO_SENDER_ID": "",
            "PLIVO_CALLBACK_URL": ""
        }
    }

    SMS_COUNTRY = {
        "name": "Sms Country",
        "code": "SMS_COUNTRY",
        "logo": "",
        "channels": [
            NotificationChannels.SMS.value
        ],
        "configuration": {
            "SMS_COUNTRY_USERNAME": "",
            "SMS_COUNTRY_PASSWORD": "",
            "SMS_COUNTRY_SENDER_ID": "",
            "SMS_COUNTRY_URL": ""
        }
    }

    FCM = {
        "name": "Google Firebase",
        "code": "FCM",
        "logo": "",
        "channels": [
            NotificationChannels.PUSH.value
        ],
        "configuration": {
            "AUTH_KEY": ""
        }
    }

    INTERAKT = {
        "name": "Interakt For Whatsapp",
        "code": "INTERAKT",
        "logo": "",
        "channels": [
            NotificationChannels.WHATSAPP.value
        ],
        "configuration": {
            "CAPACITY": 0,
            "AUTHORIZATION_TOKEN": ""
        }
    }

    @classmethod
    def is_valid_provider_code(cls, code) -> bool:
        return code in [value["code"] for value in cls.get_all_values()]

    @classmethod
    def get_channel_providers(cls, channel: NotificationChannels) -> list:
        channel_providers = list()
        for provider_configuration in cls.get_all_values():
            if channel.value in provider_configuration["channels"]:
                channel_providers.append(provider_configuration["code"])
        return channel_providers

    @classmethod
    def get_channel_providers_details(cls, channel: NotificationChannels) -> list:
        channel_providers_details = list()
        for provider_configuration in cls.get_all_values():
            if channel.value in provider_configuration["channels"]:
                channel_providers_details.append(
                    {
                        "name": provider_configuration["name"],
                        "code": provider_configuration["code"]
                    }
                )
        return channel_providers_details

    @classmethod
    def get_enum_from_code(cls, code: str):
        for custom_enum in cls:
            if code == custom_enum.value["code"]:
                return custom_enum
        return None

