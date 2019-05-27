from conf import URL
import requests


def subparser_install(subparser):
    parser_guild_follow = subparser.add_parser(
        'follow',
        help='Follow a guild'
    )
    parser_guild_follow.set_defaults(func=guild_follow)
    parser_guild_follow.add_argument('realm', help='Realm of the guild.')
    parser_guild_follow.add_argument('name', help='Realm of the guild.')
    parser_guild_unfollow = subparser.add_parser(
        'unfollow',
        help='Unfollow a guild'
    )
    parser_guild_unfollow.set_defaults(func=guild_unfollow)
    parser_guild_unfollow.add_argument('realm', help='Realm of the guild.')
    parser_guild_unfollow.add_argument('name', help='Realm of the guild.')
    parser_guild_refresh = subparser.add_parser(
        'refresh',
        help='Refresh a guild'
    )
    parser_guild_refresh.set_defaults(func=guild_refresh)
    parser_guild_refresh.add_argument('realm', help='Realm of the guild.')
    parser_guild_refresh.add_argument('name', help='Realm of the guild.')
    parser_guild_infos = subparser.add_parser(
        'infos',
        help='Get guild infos'
    )
    parser_guild_infos.set_defaults(func=guild_infos)
    parser_guild_infos.add_argument('realm', help='Realm of the guild.')
    parser_guild_infos.add_argument('name', help='Realm of the guild.')
    parser_guild_posts = subparser.add_parser(
        'posts',
        help='Get guild posts'
    )
    parser_guild_posts.set_defaults(func=guild_posts)
    parser_guild_posts.add_argument('realm', help='Realm of the guild.')
    parser_guild_posts.add_argument('name', help='Realm of the guild.')


def guild_follow(realm, name, **kwargs):
    url = URL + '/api/guild/{}/{}'.format(realm, name)
    req = requests.post(url, headers=kwargs['headers'])
    print(req.status_code)
    print(req.json())


def guild_unfollow(realm, name, **kwargs):
    url = URL + '/api/guild/{}/{}'.format(realm, name)
    req = requests.delete(url, headers=kwargs['headers'])
    print(req.status_code)
    print(req.json())


def guild_refresh(realm, name, **kwargs):
    url = URL + '/api/guild/{}/{}'.format(realm, name)
    req = requests.put(url, headers=kwargs['headers'])
    print(req.status_code)
    print(req.json())


def guild_infos(realm, name, **kwargs):
    url = URL + '/api/guild/{}/{}'.format(realm, name)
    req = requests.get(url, headers=kwargs['headers'])
    print(req.status_code)
    print(req.json())


def guild_posts(realm, name, **kwargs):
    url = URL + '/api/guild/{}/{}/posts'.format(realm, name)
    req = requests.get(url, headers=kwargs['headers'])
    print(req.status_code)
    print(req.json())
