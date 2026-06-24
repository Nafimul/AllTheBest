class AuthenticationError(Exception):
    """Raised when authentication or authorization fails."""

    status_code = 401

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)
        self.message = message
