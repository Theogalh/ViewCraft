from conf import URL
import requests
from pprint import pprint


def subparser_install(subparser):
    parser_character_get = subparser.add_parser(
        'get',
        help='Get a character'
    )
    parser_character_get.set_defaults(func=get_character)
    parser_character_get.add_argument('name', help='The name of the character u want get')
    parser_character_get.add_argument('realm', help='The realm of the character u want get')
    parser_character_refresh = subparser.add_parser(
        'refresh',
        help='Refresh a character'
    )
    parser_character_refresh.set_defaults(func=refresh_character)
    parser_character_refresh.add_argument('name', help='The name of the character u want get')
    parser_character_refresh.add_argument('realm', help='The realm of the character u want get')


def get_character(realm, name, **kwargs):
    url = URL + '/api/characters/{}/{}'.format(realm, name)
    req = requests.get(url, headers=kwargs['headers'])
    pprint(req.status_code)
    pprint(req.json())


def refresh_character(realm, name, **kwargs):
    url = URL + '/api/characters/{}/{}'.format(realm, name)
    req = requests.put(url, headers=kwargs['headers'])
    pprint(req.status_code)
    pprint(req.json())
