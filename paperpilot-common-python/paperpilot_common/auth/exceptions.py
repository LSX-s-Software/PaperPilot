class AuthException(Exception):
    def __init__(self, message):
        super().__init__(message)


class OpenIdException(AuthException):
    def __init__(self, message):
        super().__init__(message)


class OpenIdNotBound(OpenIdException):
    def __init__(self, openid: str = ""):
        super().__init__(f"OpenID {openid} not bound")


class OpenIdNotProvided(OpenIdException):
    def __init__(self):
        super().__init__("OpenID not provided")
