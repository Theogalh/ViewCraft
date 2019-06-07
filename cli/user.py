from conf import URL
import requests
from pprint import pprint


def subparser_install(subparser):
    parser_user_get = subparser.add_parser(
        'get',
        help='Get an user'
    )
    parser_user_get.set_defaults(func=get_user)
    parser_user_get.add_argument('username', help='The username of the User')


def get_user(username, **kwargs):
    url = URL + '/api/users/{}'.format(username)
    req = requests.get(url, headers=kwargs['headers'])
    pprint(req.status_code)
    pprint(req.json())
