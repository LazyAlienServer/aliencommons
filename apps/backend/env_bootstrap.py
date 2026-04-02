import os
from pathlib import Path

from environs import Env

BASE_DIR = Path(__file__).resolve().parents[1]

ENV_FILE_MAPPING = {
    "dev_lite": BASE_DIR / "env/.env.dev_lite",
    "dev": BASE_DIR / "env/.env.dev",
    "stg": BASE_DIR / "env/.env.stg",
    "pro": BASE_DIR / "env/.env.pro",
    "test": BASE_DIR / "env/.env.test",
}


def load_env() -> Env:
    env_name = os.getenv("DJANGO_ENV", "dev")
    env_file = ENV_FILE_MAPPING[env_name]

    env = Env()
    env.read_env(env_file)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))
    return env
