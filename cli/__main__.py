#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from argparse import ArgumentParser

from rosters import subparser_install as roster_subparser
from auth import subparser_install as auth_subparser
from guilds import subparser_install as guild_subparser
from posts import subparser_install as post_subparser

MAIN_COMMANDS = [
    ('roster', roster_subparser),
    ('auth', auth_subparser),
    ('guild', guild_subparser),
    ('post', post_subparser),
]


def main():
    """
    Main entry point
    """
    parser = ArgumentParser()

    subparser = parser.add_subparsers(dest='main_command', help='The main command')
    subparser.required = True

    for command in MAIN_COMMANDS:
        cmd_parser = subparser.add_parser(command[0])
        cmd_subparser = cmd_parser.add_subparsers(dest='sub_command', help='The {0} sub-command'.format(command[0]))
        cmd_subparser.required = True
        command[1](cmd_subparser)

    argument = parser.parse_args()
    argument.func(**vars(argument))


if __name__ == '__main__':
    main()
