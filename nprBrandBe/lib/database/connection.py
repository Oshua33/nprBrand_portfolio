
from contextlib import asynccontextmanager
from functools import lru_cache
from esmerald import Esmerald

from edgy import Registry
from nprOlusolaBe.configs import settings


@lru_cache()
def get_db_connection()->Registry:
    return settings.db_connection


@asynccontextmanager
async def lifespan(app: Esmerald): 
    registry = get_db_connection()
    await registry.database.connect()
    yield
    await registry.database.disconnect()
        

