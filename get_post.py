#!/usr/bin/env python

import sys
from pprint import pprint

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('--tags-only', default=False, is_flag=True, help='show only post tags')
@click.option('--body-only', default=False, is_flag=True, help='show only body')
@click.argument('url')
@click.pass_context
def main(ctx, tags_only, body_only, url):
    """Get comment object."""

    post = ctx.helper.parse_url(url)
    post = ctx.helper.get_post(post.id)

    if not post:
        sys.exit(1)

    if tags_only:
        pprint(post['tags'])
    elif body_only:
        print(post['body'])
    else:
        pprint(dict(post))


if __name__ == '__main__':
    main()
