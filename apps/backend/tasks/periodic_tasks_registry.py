"""
All periodic tasks should be registered here.
"""

periodic_tasks = [
    {
        "name": "clear expired sessions",
        "task": "users.tasks.clean_expired_sessions",
        "queue_name": "maintenance",
        "schedule": {
            "every": 1,
            "period": "day",
        },
    },
    {
        "name": "cleanup unreferenced article images",
        "task": "articles.tasks.cleanup_unreferenced_article_images",
        "queue_name": "maintenance",
        "schedule": {
            'every': 1,
            'period': 'day'
        },
        "args": [1],  # grace_days=1
    },
    {
        "name": "fan out pending notification events",
        "task": "notifications.tasks.fan_out_pending_notification_events_task",
        "queue_name": "maintenance",
        "schedule": {
            "every": 1,
            "period": "minute",
        },
    },
]
