import os
import re
from typing import Union

from edgy import EdgySettings
from esmerald import Path
from nprOlusolaBe.core.model import app_models

from nprOlusolaBe.configs import settings

class MigrationSettings(EdgySettings):
    preloads:list[str] | tuple[str] = app_models
    multi_schema: Union[bool, re.Pattern, str] = False
    ignore_schema_pattern: Union[None, re.Pattern, str] = "information_schema"
    migrate_databases: Union[list[Union[str, None]], tuple[Union[str, None], ...]] = (settings.get_database_url(),)
    migration_directory: Union[str, os.PathLike] = Path("migrations/")
    # extra keyword arguments to pass to alembic
    alembic_ctx_kwargs: dict = {
        "compare_type": True,
        "render_as_batch": True,
    }