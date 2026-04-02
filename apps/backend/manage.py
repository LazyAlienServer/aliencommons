import os
import sys
from environs import Env
from pathlib import Path

env_name = os.getenv("DJANGO_ENV", "dev")
BASE_DIR = Path(__file__).resolve().parent

ENV_FILE_MAPPING = {
    "dev": BASE_DIR / ".env.dev",
    "devfull": BASE_DIR / ".env.devfull",
    "stg": BASE_DIR / ".env.stg",
    "pro": BASE_DIR / ".env.pro",
    "test": BASE_DIR / ".env.test",
}

env = Env()
env.read_env(ENV_FILE_MAPPING[env_name])


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
