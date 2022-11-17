import logging

# Setup Logger
logging.basicConfig(
    format='[%(asctime)s][%(name)-15s][%(levelname)s]: %(message)s')

logger = logging.getLogger('OpenAI-Helper')
logger.setLevel(logging.DEBUG)


class CustomException(Exception):
    pass


class InvalidTypeError(CustomException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SubstanceEngineError(CustomException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
