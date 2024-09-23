from commonutils.utils import CustomEnum


class EmailProviders(CustomEnum):
    AWS_SES = {
        "code": "AWS_SES",
        "name": "AWS SES"
    }
    SPARK_POST = {
        "code": "SPARK_POST",
        "name": "Spark Post"
    }


class SmsProviders(CustomEnum):
    AWS_SNS = {
        "code": "AWS_SNS",
        "name": "AWS SNS"
    }
    SPARK_POST = {
        "code": "PLIVO",
        "name": "Plivo"
    }
    SMS_COUNTRY = {
        "code": "SMS_COUNTRY",
        "name": "Sms Country"
    }


class PushProviders(CustomEnum):
    FCM = {
        "name": "Google Firebase",
        "code": "FCM"
    }


class WhatsappProviders(CustomEnum):
    INTERAKT = {
        "name": "Interakt For Whatsapp",
        "code": "INTERAKT"
    }
