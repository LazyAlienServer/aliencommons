"""
ASGI config for backend project.
It exposes the ASGI callable as a module-level variable named ``application``.
"""
from django.core.asgi import get_asgi_application

from env_bootstrap import load_env

load_env()

application = get_asgi_application()
