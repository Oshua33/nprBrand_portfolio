import datetime
from functools import cached_property
from typing import TYPE_CHECKING, List, Optional
from esmerald.config.jwt import JWTConfig
from esmerald import CORSConfig, StaticFilesConfig

from esmerald.conf.enums import EnvironmentType
from esmerald.conf.global_settings import EsmeraldAPISettings
from esmerald.config.template import TemplateConfig
from esmerald.template.jinja import JinjaTemplateEngine

from edgy import  Registry
from pydantic import  DirectoryPath
from pydantic_settings import SettingsConfigDict

from nprOlusolaBe.utils import get_path


class AppSettings(EsmeraldAPISettings):
    model_config = SettingsConfigDict(env_file='.env')
    app_name: str = "API application in production mode."
    title: str = "Olusola Owonikoko API"
    description: str = "This is the API documentation Olusola Owonikoko backend"
    summary: str = "Olusola Owonikoko API documentation"
    environment: Optional[str] = EnvironmentType.PRODUCTION
    version: str = "0.0.1"
    project_url: str
    debug: bool = False
    allow_origins: List[str] = ["*"]

    secret_key: str = (
        "esmerald-insecure-qh!x)fll%egioupm9o!(v!@r4xqbm1lwxp*vcluz%x2z^1kkdx"
    )
    # Database settings
    db_name: str
    db_user: str
    db_password: str
    db_port: int
    db_host: str
    db_driver: str

    # admin email settings
    smtp_username: str
    smtp_password: str
    smtp_port: int
    smtp_host: str

    # aws_set_up
    aws_region_name: str = None
    aws_access_key: str = None
    aws_secret_key: str = None
    aws_endpoint_url: str = None
    aws_bucket_name: str = None

    # paystack
    paystack_secret_key: str
    paystack_public_key: str

    # developer contact information
    contact_email: str
    contact_name: str

    email_template_dir: DirectoryPath = get_path.get_template_dir()
    static_file_dir: DirectoryPath = get_path.get_static_file_dir()

    def get_database_url(self) -> str:
        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def static_files_config(self) -> StaticFilesConfig:
        return StaticFilesConfig(path="/static", directory=self.static_file_dir)

    @property
    def password_hashers(self) -> list[str]:
        return [
            "esmerald.contrib.auth.hashers.PBKDF2PasswordHasher",
            "esmerald.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
        ]

    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            directory=self.email_template_dir,
            engine=JinjaTemplateEngine,
        )
        
    

    @property
    def cors_config(self) -> CORSConfig:
        return CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
        )

    # @property
    # def csrf_config(self) -> CSRFConfig:
    #     if not self.secret_key:
    #         raise ImproperlyConfigured("`secret` setting not configured.")
    #     return CSRFConfig(secret=self.secret_key)

    @property
    def jwt_config(self) -> JWTConfig:
        return JWTConfig(
            signing_key=self.secret_key,
            auth_header_types=["Bearer", "Token"],
            refresh_token_lifetime=datetime.timedelta(days=1),
            access_token_lifetime=datetime.timedelta(minutes=30),
            user_id_field="id",
            user_id_claim="user_id",
            refresh_token_name="refresh_token",
            access_token_name="access_token",
        
        )

    @cached_property
    def db_connection(self) -> Registry:
        return Registry(database=self.get_database_url())




