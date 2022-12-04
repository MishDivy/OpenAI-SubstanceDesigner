import openai
from pathlib import Path
import os
from typing import Callable
from enum import Enum
import importlib
from lib import url_helper, utils, helper_api
# import url_helper
# import utils
# import helper_api

importlib.reload(url_helper)
importlib.reload(utils)
importlib.reload(helper_api)


class Resolution(Enum):
    HD1080 = '1024x1024'
    SD512 = '512x512'
    SD256 = '256x256'


def read_api_key(file: Path) -> str:
    with open(file, 'r') as f:
        return f.read()


def openai_error_check(fn: Callable) -> Callable:
    def inner(*args, **kwargs):
        key_file = helper_api.ETC_DIR / '.keys.txt'
        key = read_api_key(key_file)
        openai.api_key = key
        return_obj = None
        try:
            return_obj = fn(*args, *kwargs)
        except openai.error.OpenAIError as e:
            utils.logger.error(e.error)
            utils.logger.error(e.http_status)
        return return_obj
    return inner


@openai_error_check
def generate_image(prompt: str, resolution: Resolution = Resolution.HD1080) -> url_helper.URL:
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=resolution.value
    )
    image_url = response['data'][0]['url']

    return url_helper.URL(image_url)


@openai_error_check
def generate_variations(image_file: Path, num_iterations: int = 1, resolution: Resolution = Resolution.HD1080) -> list[url_helper.URL]:
    response = openai.Image.create_variation(
        image=open(str(image_file), "rb"),
        n=num_iterations,
        size=resolution.value
    )
    image_urls = [url_helper.URL(response['data'][i]['url'])
                  for i in range(num_iterations)]
    return image_urls


@openai_error_check
def edit_image(image_file: Path, mask_image: Path, prompt: str, num_iterations: int = 1, resolution=Resolution.HD1080) -> list[url_helper.URL]:
    response = openai.Image.create_edit(
        image=open(str(image_file), "rb"),
        mask=open(str(mask_image), "rb"),
        prompt=prompt,
        n=num_iterations,
        size=resolution.value
    )
    image_urls = [url_helper.URL(response['data'][i]['url'])
                  for i in range(num_iterations)]
    return image_urls


def check_file_name(file: Path) -> Path:
    if file.is_file():
        version = file.stem.split('_')[-1]
        if version.isdigit():
            new_version = str(int(version) + 1)
            file = file.parent / \
                (file.stem.replace(version, new_version) + file.suffix)
        else:
            new_stem = file.stem + '_1'
            file = file.parent / (new_stem + file.suffix)
        return check_file_name(file)
    else:
        return file
