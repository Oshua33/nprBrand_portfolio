from esmerald import Request


def get_ip_address(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    real_ip = request.headers.get("X-Real-IP")
    if forwarded_for:
        return forwarded_for.split(",")[0]
    elif real_ip:
        return real_ip
    else:
        return request.client.host if request.client else "localhost"
