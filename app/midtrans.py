import midtransclient
from .config import settings

class MidtransAPI:
    snap = midtransclient.Snap(
        is_production=False,
        server_key=settings.server_key
    )