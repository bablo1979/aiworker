import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self, dotenv_path: str = "../.env"):
        self._load_environment(dotenv_path)

    def _load_environment(self, dotenv_path: str):
        # Carica .env solo se esiste
        env_path = Path(dotenv_path)
        if env_path.exists():
            load_dotenv(dotenv_path)
            print(f"Loaded configuration from {dotenv_path}")
        else:
            print("No .env file found, using environment variables (likely running in K8s)")

    def get(self, key: str, default=None):
        return os.getenv(key, default)

    def get_required(self, key: str):
        value = os.getenv(key)
        if value is None:
            raise KeyError(f"Missing required configuration key: {key}")
        return value
