"""
All periodic tasks should be registered here.
"""

periodic_tasks = [
            {
                "name": "update youtube cache",
                "task": "pages.tasks.refresh_youtube_cache",
                "queue_name": "maintenance",
                "schedule": {
                    'every': 1,
                    'period': 'minute'
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
]
