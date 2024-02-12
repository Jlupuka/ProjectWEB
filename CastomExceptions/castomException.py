class NotFoundCryptoToken(Exception):
    """
    Called if there is no such crypto-network in the system
    """

    def __init__(self, *args: str | None) -> None:
        self.message = args[0] if args else None

    def __str__(self) -> str:
        return self.message


class BadRequest(Exception):
    """
    Called if bad response from API request
    """

    def __init__(self, *args: str | None) -> None:
        self.message = args[0] if args else None

    def __str__(self) -> str:
        return self.message
