import logging
from functools import update_wrapper, wraps

import click
import yaml

from .golos_helper import GolosHelper

log = logging.getLogger('golosscripts')


def common_options(func):
    @click.option('-d', '--debug', default=False, is_flag=True, help='enable debug output')
    @click.option(
        '-c', '--config', type=click.File('r'), default='./common.yml', help='specify custom path for config file'
    )
    @click.pass_context
    @wraps(func)
    def wrapper(ctx, *args, **kwargs):
        ctx.config = yaml.safe_load(kwargs.pop("config"))

        # create logger
        debug = kwargs.pop("debug")
        ctx.debug = debug
        if debug is True:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)
        ctx.log = log

        return func(*args, **kwargs)

    return wrapper


def helper(func):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.helper = GolosHelper(nodes=ctx.config['nodes'], keys=ctx.config['keys'], expiration=60)
        return ctx.invoke(func, *args, **kwargs)

    return update_wrapper(new_func, func)
