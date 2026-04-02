import os
from pathlib import Path

from environs import Env
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE_MAPPING = {
    "dev_lite": BASE_DIR / "env/.env.dev_lite",
    "dev": BASE_DIR / "env/.env.dev",
    "stg": BASE_DIR / "env/.env.stg",
    "pro": BASE_DIR / "env/.env.pro",
    "test": BASE_DIR / "env/.env.test",
}


def load_env() -> Env:
    env_name = os.getenv("DJANGO_ENV", "dev")

    if env_name not in list(ENV_FILE_MAPPING.keys()):
        raise RuntimeError(f"Invalid env name: {env_name}")

    env_file = ENV_FILE_MAPPING[env_name]

    if not env_file.exists():
        raise RuntimeError(f"Env file not found: {env_file}")

    load_dotenv(dotenv_path=env_file)

    env = Env()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))
    return env
