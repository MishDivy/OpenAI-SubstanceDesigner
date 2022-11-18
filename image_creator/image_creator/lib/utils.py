import logging
from typing import Callable
import time

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


def wait_for_substance_engine(condition_func: Callable,  pass_message: str, fail_message: str, wait_limit: float = 10.0, wait_interval: float = 0.5, **kwargs) -> None:
    wait_time = 0.0
    while True:
        if callable(condition_func):
            if condition_func(**kwargs):
                print(pass_message)
                return
            else:
                if wait_time >= wait_limit:
                    raise SubstanceEngineError(
                        f'{fail_message}. Substance Engine taking too long to respond.')
                time.sleep(wait_interval)
                wait_time += wait_interval
                print('Waiting for Substance Engine....')
        else:
            raise NotImplementedError('Function provided is not callable.')
