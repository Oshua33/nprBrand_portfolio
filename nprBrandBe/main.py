#!/usr/bin/env python

import os
import sys
from esmerald import  Esmerald, Include
from edgy import Instance, monkay
from nprOlusolaBe.lib.database.connection import get_db_connection, lifespan
from nprOlusolaBe.configs import settings

def build_path():

    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

    if SITE_ROOT not in sys.path:
        sys.path.append(SITE_ROOT)
        sys.path.append(os.path.join(SITE_ROOT, "apps"))





def get_application() -> Esmerald:

    build_path()
    registry = get_db_connection()
    app = registry.asgi(Esmerald(
        routes=[Include(namespace="nprOlusolaBe.urls", path="/api/v1")],
        lifespan=lifespan,
        settings_module=settings,
    
    ))
   

    monkay.set_instance(Instance(registry=registry, app=app), apply_extensions=False)

    return app


app = get_application()
