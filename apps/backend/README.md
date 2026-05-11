# AlienCommons Backend

The Django API service for AlienCommons.

## Tech Stacks

- Python 3.14
- Django 6
- Django REST Framework
- Django Channels and Daphne
- PostgreSQL
- Redis
- RQ task workers via `django-tasks-rq`
- S3-compatible media storage in hosted environments

## Apps

- `users`: users, sessions, emails, and subscriptions
- `articles`: source articles, published articles, collections, and article workflows
- `bookmarks`: bookmark folders and article bookmarks
- `comments`: article comments and replies
- `posts`: community posts and related content
- `reactions`: like/dislike targets and user reactions
- `reports`: content and user moderation reports
- `tasks`: scheduled/background task definitions
- `core`: shared utilities, responses, permissions, and test helpers

## Local Commands

Run from `apps/backend`:

```bash
uv run python manage.py check
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py test --settings=backend.settings.test
uv run ruff check articles bookmarks comments posts reactions reports core users logs tasks backend manage.py
```

Or use the root Make targets:

```bash
make dev-up
make dev-backend-test
make dev-backend-check
```

## Settings

- `backend.settings.dev`: local development
- `backend.settings.test`: tests
- `backend.settings.stg`: staging
- `backend.settings.pro`: production

Hosted media is stored through S3-compatible storage. Static files are served separately.
