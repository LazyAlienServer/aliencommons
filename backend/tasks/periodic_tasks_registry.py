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
                "name": "clear old frontend debug logs",
                "task": "logs.tasks.clear_debug_logs",
                "queue_name": "maintenance",
                "schedule": {
                    'every': 1,
                    'period': 'day'
                },
                "args": [14],
            },
            {
                "name": "clear old frontend info logs",
                "task": "logs.tasks.clear_info_logs",
                "queue_name": "maintenance",
                "schedule": {
                    'every': 1,
                    'period': 'day'
                },
                "args": [30],
            },
            {
                "name": "clear old frontend warn logs",
                "task": "logs.tasks.clear_warn_logs",
                "queue_name": "maintenance",
                "schedule": {
                    'every': 1,
                    'period': 'day'
                },
                "args": [90],
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
