from nprOlusolaBe.configs import settings as config


def get_prefix():
    try:
        return f"/api/v{int(config.version) if int(config.version )> 0 else 1}"
    except Exception:
        return str("/api/v1")
