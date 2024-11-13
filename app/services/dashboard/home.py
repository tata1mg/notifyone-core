from queue import Queue

from commonutils.utils import CustomEnum

from app.constants import NotificationChannels, NotificationRequestLogStatus
from app.repositories.notification_request_log import NotificationRequestLogRepository
from app.repositories.providers import ProvidersRepository
from app.services import SubscribeNotificationRequest
from app.services.email import EmailHandler
from app.services.push import PushHandler
from app.services.sms import SMSHandler
from app.services.whatsapp import WhatsappHandler


class Components(CustomEnum):
    GATEWAY = "GATEWAY"
    CORE = "CORE"
    HANDLER = "HANDLER"


class QueueHealth:
    HEALTHY = {
        "health": "HEALTHY",
        "messages_threshold": 250,
        "message": "Functioning smoothly with very less backlog."
    }
    SLOW = {
        "health": "SLOW",
        "messages_threshold": 1000,
        "message": "Functioning smoothly, but a bit high backlog. Things should go fine soon."
    },
    OVERLOADED = {
        "health": "OVERLOADED",
        "messages_threshold": None,
        "message": "Queue is overloaded, scaling the respective handler will fix this."
    }

    @classmethod
    def get_queue_health(cls, messages_count: int) -> dict:
        if messages_count < cls.HEALTHY["messages_threshold"]:
            health = cls.HEALTHY["health"]
            message = cls.HEALTHY["message"]
        elif messages_count < cls.SLOW["messages_threshold"]:
            health = cls.SLOW["health"]
            message = cls.SLOW["message"]
        else:
            health = cls.OVERLOADED["health"]
            message = cls.OVERLOADED["message"]
        return {
            ""
            "health": health,
            "total_messages": messages_count,
            "message": message
        }


class ComponentHealth:
    HEALTHY = {
        "health": "HEALTHY",
        "latency_threshold": 500,
        "message": "All services are operational, and the system is functioning without any issues"
    }

    DEGRADED = {
        "health": "DEGRADED",
        "latency_threshold": 1000,
        "message": "The system is operational but experiencing minor issues"
    }

    OUTAGE = {
        "health": "OUTAGE",
        "latency_threshold": None,
        "message": "The system is operational but experiencing minor issues"
    }

    @classmethod
    async def get_component_health(cls, component: Components) -> dict:
        if component.value == Components.GATEWAY.value:
            # Make a health check call to Gateway component
            pass
        if component.value == Components.CORE.value:
            # Make a health check call to Core component
            pass
        if component.value == Components.HANDLER.value:
            # Make a health check call to Handler component
            pass
        return {
            "component": component.value.title(),
            "health": cls.HEALTHY["health"],
            "message": cls.HEALTHY["message"]
        }


class DashboardHomeScreen:

    @classmethod
    async def get_homepage_data(cls):
        channel_status_breakup = await NotificationRequestLogRepository.get_channel_status_analytics(interval_hours=24)
        email_providers = await ProvidersRepository.get_providers_for_channel(NotificationChannels.EMAIL)
        sms_providers = await ProvidersRepository.get_providers_for_channel(NotificationChannels.SMS)
        push_providers = await ProvidersRepository.get_providers_for_channel(NotificationChannels.PUSH)
        whatsapp_providers = await ProvidersRepository.get_providers_for_channel(NotificationChannels.WHATSAPP)

        # get priority queues messages count
        messages_in_priority_queues = await SubscribeNotificationRequest.get_messages_in_priority_queues()

        # get channel queues messages count
        email_queue_messages_count = int(await EmailHandler._dispatch_notification.async_dispatcher.get_messages_count())
        sms_queue_messages_count = int(await SMSHandler._dispatch_notification.async_dispatcher.get_messages_count())
        push_queue_messages_count = int(await PushHandler._dispatch_notification.async_dispatcher.get_messages_count())
        whatsapp_queue_messages_count = int(await WhatsappHandler._dispatch_notification.async_dispatcher.get_messages_count())



        def _get_notifications_breakup(data):
            total_notifications = 0
            success_notifications = 0
            not_success_notifications = 0
            for row in data:
                total_notifications += row.count
                if row.status in NotificationRequestLogStatus.trigger_successful_statuses():
                    success_notifications += row.count
                else:
                    not_success_notifications += row.count
            success_rate = int((success_notifications/total_notifications)*100) if total_notifications > 0 else 0
            return {
                "total_notifications": total_notifications,
                "success_rate": success_rate,
                "success_rate_percentage": "{}%".format(success_rate)
            }

        def _get_channel_notifications_breakup(data, channel_enum:NotificationChannels):
            total_notifications = 0
            success_notifications = 0
            not_success_notifications = 0
            for row in data:
                total_notifications += row.count
                if row.channel == channel_enum.value:
                    if row.status in NotificationRequestLogStatus.trigger_successful_statuses():
                        success_notifications += row.count
                    else:
                        not_success_notifications += row.count
            success_rate = int((success_notifications/total_notifications)*100) if total_notifications > 0 else 0
            return {
                "sent": total_notifications,
                "success_rate": success_rate,
                "success_rate_percentage": "{}%".format(success_rate)
            }

        channels = {
            "title": "Available Channels",
            "sub_title": "Active/In-Active channels",
            "list": [
                {
                    "title": "Email",
                    "sub_title": "Add/Manage Email providers",
                    "active": True if email_providers else False,
                    "notifications": _get_channel_notifications_breakup(channel_status_breakup, NotificationChannels.EMAIL)
                },
                {
                    "title": "Sms",
                    "sub_title": "Add/Manage SMS Providers",
                    "active": True if sms_providers else False,
                    "notifications": _get_channel_notifications_breakup(channel_status_breakup, NotificationChannels.SMS)
                },
                {
                    "title": "Push",
                    "sub_title": "Add/Manage Push Providers",
                    "active": True if push_providers else False,
                    "notifications": _get_channel_notifications_breakup(channel_status_breakup ,NotificationChannels.PUSH)
                },
                {
                    "title": "Whatsapp",
                    "sub_title": "Add/Manage Whatsapp Providers",
                    "active": True if whatsapp_providers else False,
                    "notifications": _get_channel_notifications_breakup(channel_status_breakup, NotificationChannels.WHATSAPP)
                }
            ]
        }

        metrics = {
            "latency": "200ms"
        }
        metrics.update(_get_notifications_breakup(channel_status_breakup))
        key_metrics = {
            "title": "Key System Metrics",
            "sub_title": "",
            "metrics": metrics
        }
        components_health = [
            await ComponentHealth.get_component_health(Components.GATEWAY),
            await ComponentHealth.get_component_health(Components.CORE),
            await ComponentHealth.get_component_health(Components.HANDLER)
        ]
        high_priority_queue_health = {
            "priority_type": "High Priority",
        }
        medium_priority_queue_health = {
            "priority_type": "Medium Priority",
        }
        low_priority_queue_health = {
            "priority_type": "Low Priority",
        }
        high_priority_queue_health.update(QueueHealth.get_queue_health(messages_in_priority_queues["HIGH_PRIORITY"]))
        medium_priority_queue_health.update(QueueHealth.get_queue_health(messages_in_priority_queues["MEDIUM_PRIORITY"]))
        low_priority_queue_health.update(QueueHealth.get_queue_health(messages_in_priority_queues["LOW_PRIORITY"]))

        priority_queues_health = [
            high_priority_queue_health, medium_priority_queue_health, low_priority_queue_health
        ]

        email_queue_health = {
            "channel": "Email",
        }
        email_queue_health.update(QueueHealth.get_queue_health(email_queue_messages_count))
        sms_queue_health = {
            "channel": "Sms",
        }
        sms_queue_health.update(QueueHealth.get_queue_health(sms_queue_messages_count))
        push_queue_health = {
            "channel": "Push"
        }
        push_queue_health.update(QueueHealth.get_queue_health(push_queue_messages_count))
        whatsapp_queue_health = {
            "channel": "Whatsapp"
        }
        whatsapp_queue_health.update(QueueHealth.get_queue_health(whatsapp_queue_messages_count))
        channel_queues_health = [
            email_queue_health, sms_queue_health, push_queue_health, whatsapp_queue_health
        ]
        return {
            "channels": channels,
            "key_metrics": key_metrics,
            "real_time_status": {
                "title": "Real Time System Health",
                "sub_title": "Get live notifications, components and Queues health",
                "live_notifications": {
                    "queued": sum(messages_in_priority_queues.values()),
                    "triggered": sum([email_queue_messages_count, sms_queue_messages_count, push_queue_messages_count, whatsapp_queue_messages_count])
                },
                "system_health": {
                    "components": components_health,
                    "priority_queues": priority_queues_health,
                    "channel_queues": channel_queues_health
                }
            },
            "user_engagement": {}
        }