from viewcraft.cli.conf import URL
import requests
from pprint import pprint


def subparser_install(subparser):
    parser_roster_list = subparser.add_parser(
        'list',
        help='List the roster'
    )
    parser_roster_list.set_defaults(func=get_roster)
    parser_roster_create = subparser.add_parser(
        'create',
        help='Create a new roster'
    )
    parser_roster_create.set_defaults(func=roster_create)
    parser_roster_create.add_argument('name', help='The name of the roster u want create')
    parser_roster_delete = subparser.add_parser(
        'delete',
        help='Delete a roster'
    )
    parser_roster_delete.set_defaults(func=roster_delete)
    parser_roster_delete.add_argument('name', help='The name of the roster u want delete')
    parser_roster_infos = subparser.add_parser(
        'infos',
        help='Get roster informations'
    )
    parser_roster_infos.set_defaults(func=roster_get)
    parser_roster_infos.add_argument('name', help='The name of the roster u want getting informations')
    parser_roster_refresh = subparser.add_parser(
        'refresh',
        help='Refresh roster informations'
    )
    parser_roster_refresh.set_defaults(func=roster_refresh)
    parser_roster_refresh.add_argument('name', help='The name of the roster u want refresh')
    parser_roster_add_member = subparser.add_parser(
        'add_member',
        help='Add a member to a roster'
    )
    parser_roster_add_member.set_defaults(func=roster_add_member)
    parser_roster_add_member.add_argument('name', help='The name of the roster u want to add a member')
    parser_roster_add_member.add_argument('realm', help='The name of the character realm')
    parser_roster_add_member.add_argument('charName', help='The name of the character')
    parser_roster_refresh_member = subparser.add_parser(
        'refresh_member',
        help='Add a member to a roster'
    )
    parser_roster_refresh_member.set_defaults(func=roster_refresh_member)
    parser_roster_refresh_member.add_argument('name', help='The name of the roster member u want to refresh')
    parser_roster_refresh_member.add_argument('realm', help='The name of the character realm')
    parser_roster_refresh_member.add_argument('charName', help='The name of the character')
    parser_roster_del_member = subparser.add_parser(
        'del_member',
        help='Delete a member to a roster'
    )
    parser_roster_del_member.set_defaults(func=roster_del_member)
    parser_roster_del_member.add_argument('name', help='The name of the roster u want to del a member')
    parser_roster_del_member.add_argument('realm', help='The name of the character realm')
    parser_roster_del_member.add_argument('charName', help='The name of the character')
    parser_roster_get_members = subparser.add_parser(
        'get_members',
        help='Get all member of a roster'
    )
    parser_roster_get_members.set_defaults(func=roster_get_members)
    parser_roster_get_members.add_argument('name', help='The name of the roster u want to get members')


def get_roster(**kwargs):
    url = URL + '/api/rosters'
    req = requests.get(url, headers=kwargs['headers'])
    pprint(req.status_code)
    pprint(req.json())


def roster_create(name, **kwargs):
    url = URL + '/api/rosters/{}'.format(name)
    req = requests.post(url, headers=kwargs['headers'])
    pprint(req.status_code)
    pprint(req.json())


def roster_delete(name, **kwargs):
    url = URL + '/api/rosters/{}'.format(name)
    req = requests.delete(url, headers=kwargs['headers'])
    pprint(req.status_code)
    if req.status_code == 204:
        pprint('Roster deleted')
    else:
        pprint(req.json())


def roster_refresh(name, **kwargs):
    url = URL + '/api/rosters/{}'.format(name)
    req = requests.put(url, headers=kwargs['headers'])
    pprint({'status_code': req.status_code})
    pprint(req.json())


def roster_get(name, **kwargs):
    url = URL + '/api/rosters/{}'.format(name)
    req = requests.get(url, headers=kwargs['headers'])
    pprint({'status_code': req.status_code})
    pprint(req.json())


def roster_get_members(name, **kwargs):
    url = URL + '/api/rosters/{}/members'.format(name)
    req = requests.get(url, headers=kwargs['headers'])
    pprint({'status_code': req.status_code})
    pprint(req.json())


def roster_add_member(name, realm, charName, **kwargs):
    url = URL + '/api/rosters/{}/members/{}/{}'.format(name, realm, charName)
    req = requests.post(url, headers=kwargs['headers'])
    pprint({'status_code': req.status_code})
    pprint(req.json())


def roster_refresh_member(name, realm, charName, **kwargs):
    url = URL + '/api/rosters/{}/members/{}/{}'.format(name, realm, charName)
    req = requests.put(url, headers=kwargs['headers'])
    pprint({'status_code': req.status_code})
    pprint(req.json())


def roster_del_member(name, realm, charName, **kwargs):
    url = URL + '/api/rosters/{}/members/{}/{}'.format(name, realm, charName)
    req = requests.delete(url, headers=kwargs['headers'])
    pprint({'status_code': req.status_code})
    pprint(req.json())
