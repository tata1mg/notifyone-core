class PushTarget:
    PROTOCOL = {
        "1MG": "onemg",
        "HTTP": "http",
        "HTTPS": "https",
        "1MG_WEB": "onemg-web",
    }
    DOMAIN_NAME = {
        "1MG_PHARMACY_ENV": '{{Hkp_url.split("://")[1]}}',
        "1MG_PHARMACY_PROD": "www.1mg.com",
    }
    ORDER_DETAILS_PLACE_HOLDER = {
        "order_id": "order.order_id",
        "email": "order.user.email",
        "group_id": "order.group_id",
    }
    PRESCRIPTION_DETAILS_PLACE_HOLDER = {
        "prescription_id": "id",
        "patient_id": "patient_id",
    }
    DYNAMIC_TARGET = {"name": "DYNAMIC TARGET", "value": "{{target}}"}
    TARGET = {
        "WEB NPS": {
            "PROTOCOL": PROTOCOL["1MG_WEB"],
            "DOMAIN_NAME": DOMAIN_NAME["1MG_PHARMACY_ENV"],
            "URL": "/feedback",
            "query_params": [
                {
                    "name": "orderId",
                    "place_holder": ORDER_DETAILS_PLACE_HOLDER["group_id"],
                },
                {
                    "name": "emailAddress",
                    "place_holder": ORDER_DETAILS_PLACE_HOLDER["email"],
                },
                {"name": "utm_source", "direct_value": "native_app"},
                {"name": "utm_campaign", "direct_value": "NPS"},
            ],
        },
        "TRACK ORDER": {
            "PROTOCOL": PROTOCOL["1MG"],
            "DOMAIN_NAME": DOMAIN_NAME["1MG_PHARMACY_PROD"],
            "URL": "/track",
            "query_params": [
                {
                    "name": "orderId",
                    "place_holder": ORDER_DETAILS_PLACE_HOLDER["order_id"],
                }
            ],
        },
        "ORDER HISTORY": {
            "PROTOCOL": PROTOCOL["1MG"],
            "DOMAIN_NAME": DOMAIN_NAME["1MG_PHARMACY_PROD"],
            "URL": "/history",
        },
        "UPLOAD PRESCRIPTION": {
            "PROTOCOL": PROTOCOL["1MG"],
            "DOMAIN_NAME": DOMAIN_NAME["1MG_PHARMACY_PROD"],
            "URL": "/attach_prescription",
            "query_params": [
                {
                    "name": "orderId",
                    "place_holder": ORDER_DETAILS_PLACE_HOLDER["order_id"],
                }
            ],
        },
        "PRESCRIPTION DETAIL": {
            "PROTOCOL": PROTOCOL["1MG"],
            "DOMAIN_NAME": DOMAIN_NAME["1MG_PHARMACY_PROD"],
            "URL": "/rx_detail",
            "query_params": [
                {
                    "name": "prescriptionId",
                    "place_holder": PRESCRIPTION_DETAILS_PLACE_HOLDER[
                        "prescription_id"
                    ],
                },
                {
                    "name": "patientId",
                    "place_holder": PRESCRIPTION_DETAILS_PLACE_HOLDER["patient_id"],
                },
            ],
        },
    }


class Push:
    TITLE = "title"
    BODY = "body"
    CONTENT_COLUMNS = [
        "id",
        "event_id",
        "target",
        "body",
        "title",
        "image",
        "updated_by",
        "updated",
    ]
