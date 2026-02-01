from dataclasses import dataclass
from typing import Optional

@dataclass
class ResolvePlayerRequest:
    auth_header: Optional[str] = None
    client_host: Optional[str] = "unknown"
    user_agent: Optional[str] = "unknown"
