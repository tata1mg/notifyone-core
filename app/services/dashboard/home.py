class DashboardHome:

    @classmethod
    async def get_homepage_data(cls):
        return {
            "channels": {
                "title": "Available Channels",
                "sub_title": "Active/In-Active channels",
                "list": [
                    {
                        "title": "Email",
                        "sub_title": "Add/Manage Email providers",
                        "active": True,
                        "notifications": {
                            "sent": 100,
                            "success_rate": 85
                        }
                    },
                    {
                        "title": "Sms",
                        "sub_title": "Add/Manage SMS Providers",
                        "active": True,
                        "notifications": {
                            "sent": 500,
                            "success_rate": 92
                        }
                    },
                    {
                        "title": "Push",
                        "sub_title": "Add/Manage Push Providers",
                        "active": False,
                    },
                    {
                        "title": "Whatsapp",
                        "sub_title": "Add/Manage Whatsapp Providers",
                        "active": False,
                    }
                ]
            },
            "key_metrics": {
                "title": "Key System Metrics",
                "sub_title": "",
                "metrics": {
                    "total_notifications": 1000,
                    "success_rate": 92,
                    "latency": "<text> 99ms"
                }
            },
            "real_time_status": {
                "title": "Real Time System Health",
                "sub_title": "Get live notifications, components and Queues health",
                "live_notifications": {
                    "queued": 80,
                    "triggered": 120
                },
                "system_health": {
                    "components": [
                        {"component": "Gateway",
                         "health": "HEALTHY",
                         "message": "All services are operational, and the system is functioning without any issues"
                         },
                        {
                            "component": "Core",
                            "health": "DEGRADED",
                            "message": "The system is operational but experiencing minor issues"
                        },
                        {
                            "component": "Handler",
                            "health": "OUTAGE",
                            "message": "The system is operational but experiencing minor issues"
                        }
                    ],
                    "priority_queues": [
                        {
                            "priority_type": "High Priority",
                            "health": "HEALTHY",
                            "total_messages": 122,
                            "message": "Functioning smoothly with very less backlog"
                        },
                        {
                            "priority_type": "Medium Priority",
                            "health": "SLOW",
                            "total_messages": 212,
                            "message": "Functioning smoothly, but a bit high backlog"
                        },
                        {
                            "priority_type": "Low Priority",
                            "health": "OVERLOADED",
                            "total_messages": 539,
                            "message": "Queue is overloaded, scaling core component will fix this"
                        }
                    ],
                    "channel_queues": [
                        {
                            "channel": "Email",
                            "health": "HEALTHY",
                            "total_messages": 122,
                            "message": "Functioning smoothly with very less backlog"
                        },
                        {
                            "channel": "Sms",
                            "health": "SLOW",
                            "total_messages": 212,
                            "message":
                                "Functioning smoothly, but a bit high backlog. Things will go fine soon."
                        },
                        {
                            "channel": "Push",
                            "health": "OVERLOADED",
                            "total_messages": 539,
                            "message": "Queue is overloaded, scaling push handler will fix this"
                        },
                        {
                            "channel": "Whatsapp",
                            "health": "OVERLOADED",
                            "total_messages": 539,
                            "message": "Queue is overloaded, scaling whatsapp handler will fix this"
                        }
                    ]
                }
            },
            "user_engagement": {}
        }