from typing import Protocol, Optional, Dict, Any


class ProviderInterface(Protocol):
    """Protocol that all provider implementations must follow.

    Implementations must provide a `send` method that returns a dict
    containing at least `success` (bool) and `provider` (str).
    """

    def send(self, to: str, subject: str, body: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ...
