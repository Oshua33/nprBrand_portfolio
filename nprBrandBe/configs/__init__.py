from functools import lru_cache
from os import getenv
from typing import Union

from nprOlusolaBe.configs.production.settings import AppSettings
from nprOlusolaBe.configs.development.settings import DevelopmentAppSettings
from nprOlusolaBe.configs.testing.settings import TestingAppSettings


@lru_cache
def get_settings_class() -> (
    Union[AppSettings, DevelopmentAppSettings, TestingAppSettings]
):
    environment: str = getenv("ENVIRONMENT", "production")
    if environment == "production":
        return AppSettings()
    elif environment == "development":
        return DevelopmentAppSettings()
    elif environment == "testing":
        return TestingAppSettings()
    raise ValueError(f"Invalid environment: {environment}")


settings = get_settings_class()
