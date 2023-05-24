import midtransclient
from .config import settings

class MidtransAPI:
    snap = midtransclient.Snap(
        is_production=False,
        client_key=settings.client_key,
        server_key=settings.server_key
    )