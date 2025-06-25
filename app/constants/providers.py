from commonutils.utils import CustomEnum

from app.constants import NotificationChannels


class ProvidersStatus(CustomEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class Providers(CustomEnum):

    AWS_SES = {
        "name": "AWS SES",
        "code": "AWS_SES",
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/aws-ses.svg",
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
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/sparkpost.png",
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
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/aws-sns.svg",
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
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/plivo.svg",
        "channels": [
            NotificationChannels.SMS.value
        ],
        "configuration": {
            "PLIVO_SMS_URL": "",
            "PLIVO_AUTH_ID": "",
            "PLIVO_AUTH_TOKEN": "",
            "PLIVO_SENDER_ID": "",
            "PLIVO_CALLBACK_URL": "",
        }
    }

    SMS_COUNTRY = {
        "name": "Sms Country",
        "code": "SMS_COUNTRY",
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/sms-country.png",
        "channels": [
            NotificationChannels.SMS.value
        ],
        "configuration": {
            "SMS_COUNTRY_USERNAME": "",
            "SMS_COUNTRY_PASSWORD": "",
            "SMS_COUNTRY_SENDER_ID": "",
            "SMS_COUNTRY_OTP_USERNAME": "",
            "SMS_COUNTRY_OTP_PASSWORD": "",
            "SMS_COUNTRY_OTP_SENDER_ID": "",
            "SMS_COUNTRY_DROPLET_USERNAME": "",
            "SMS_COUNTRY_DROPLET_PASSWORD": "",
            "SMS_COUNTRY_DROPLET_SENDER_ID": "",
            "SMS_COUNTRY_URL": "",
        }
    }

    FCM = {
        "name": "Google Firebase",
        "code": "FCM",
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/fcm.svg",
        "channels": [
            NotificationChannels.PUSH.value
        ],
        "configuration": {
            "PROJECT_ID": "",
            "TYPE": "",
            "PRIVATE_KEY_ID": "",
            "PRIVATE_KEY": "",
            "CLIENT_EMAIL": "",
            "CLIENT_ID": "",
            "TOKEN_URI": "",
            "AUTH_URI": "",
            "AUTH_PROVIDER_X509_CERT_URL": "",
            "CLIENT_X509_CERT_URL": "",
            "UNIVERSE_DOMAIN": ""
        }
    }

    APNS = {
        "name": "Apple Push Notification Service",
        "code": "APNS",
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/apns.png",
        "channels": [
            NotificationChannels.PUSH.value
        ],
        "configuration": {
            "HOST": "",
            "ENDPOINT": "",
            "BUNDLE_IDENTIFIER": "",
            "REFRESH_TOKEN_DELAY": 1800,
            "ALGORITHM": "",
            "TEAM_ID": "",
            "KEY_ID": "",
            "PRIVATE_KEY": ""
        }
    }

    INTERAKT = {
        "name": "Interakt For Whatsapp",
        "code": "INTERAKT",
        "logo": "https://raw.githubusercontent.com/tata1mg/notifyone-core/refs/heads/notifyone/issues/14/media/logo/interakt.png",
        "channels": [
            NotificationChannels.WHATSAPP.value
        ],
        "configuration": {
            "APP_AUTHORIZATIONS": {
            "corporate-service": "CORPORATE",
            "diagnostics": "DIAGNOSTICS",
            "health_records": "DIAGNOSTICS",
            "off": "PHARMACY",
            "ppmc_api": "CORPORATE",
            "validation_service": "PHARMACY",
            "verification": "PHARMACY"
            },
            "AUTHORIZATION": {
            "CORPORATE": "Basic VkN6SjkxZVQ3SkV6R2sxdmtMblZkb092M1dHUVR2RXZ2ekVUVlJBNHZsTTo=",
            "DEFAULT": "Basic dm9VOWNseVNPeUpadUpmQ2VTMnVfdFhqdzB4V3JvWVNvUWozOVpIM2NGNDo=",
            "DIAGNOSTICS": "Basic dm9VOWNseVNPeUpadUpmQ2VTMnVfdFhqdzB4V3JvWVNvUWozOVpIM2NGNDo=",
            "PHARMACY": "Basic TTl1SFg2TlZxOWJjZDNndldsSGhfRVBWRVd0ZWNRbHVVS2ZOeV8temllZzo="
            },
            "HOST": "https://api.interakt.ai",
            "PATH": "/v1/public/message/"
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
                        "code": provider_configuration["code"],
                        "logo": provider_configuration["logo"]
                    }
                )
        return channel_providers_details

    @classmethod
    def get_enum_from_code(cls, code: str):
        for custom_enum in cls:
            if code == custom_enum.value["code"]:
                return custom_enum
        return None

