from conf import URL
import requests
from requests.auth import HTTPBasicAuth
from getpass import getpass
import os


def subparser_install(subparser):
    parser_auth_get_token = subparser.add_parser(
        'get_token',
        help='Get a new token'
    )
    parser_auth_get_token.set_defaults(func=get_token)
    parser_auth_get_token.add_argument('username', help='Username of the User')
    parser_auth_revoke_token = subparser.add_parser(
        'revoke_token',
        help='Revoke the token'
    )
    parser_auth_revoke_token.set_defaults(func=revoke_token)
    parser_auth_revoke_token.add_argument('token', help='The token to revoke')


def get_token(username, **kwargs):
    url = URL + '/api/tokens'
    password = getpass(prompt='Password: ', stream=None)
    auth = HTTPBasicAuth(username, password)
    req = requests.post(url, auth=auth)
    print(req.status_code)
    print(req.json())
    if req.status_code == 200:
        with open('.token', 'w') as file:
            file.write(req.json()['token'])


def revoke_token(token, **kwargs):
    url = URL + '/api/tokens'
    headers = {"Authorization": "Bearer {}".format(token)}
    req = requests.delete(url, headers=headers)
    print(req.status_code)
    if req.status_code == 204:
        print('Token revoked')
    else:
        print(req.json())
