from jinja2 import TemplateNotFound


class MailException(Exception):
    """Base exception for mail-related errors"""

    pass


class ServerConnectionError(MailException):
    """Raised when connection to mail server fails"""

    pass


class InvalidCredentialError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class InvalidEmailContentError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class EmailTemplateNotFoundError(TemplateNotFound):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class TemplateFolderNotFoundError(NotADirectoryError):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
