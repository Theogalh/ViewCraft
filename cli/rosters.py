from conf import URL, TOKEN


def subparser_install(subparser):
    parser_roster_create = subparser.add_parser(
        'create',
        help='Create a new roster'
    )
    parser_roster_create.set_defaults(roster_create)
    parser_roster_create.add_argument('name', help='The name of the roster u want create')
    parser_roster_delete = subparser.add_parser(
        'delete',
        help='Delete a roster'
    )
    parser_roster_delete.set_defaults(roster_delete)
    parser_roster_delete.add_argument('name', help='The name of the roster u want delete')
    parser_roster_infos = subparser.add_parser(
        'infos',
        help='Get roster informations'
    )
    parser_roster_infos.set_defaults(roster_get)
    parser_roster_infos.add_argument('name', help='The name of the roster u want getting informations')
    parser_roster_refresh = subparser.add_parser(
        'refresh',
        help='Refresh roster informations'
    )
    parser_roster_refresh.set_defaults(roster_refresh)
    parser_roster_refresh.add_argument('name', help='The name of the roster u want refresh')
    parser_roster_add_member = subparser.add_parser(
        'add_member',
        help='Add a member to a roster'
    )
    parser_roster_add_member.set_defaults(roster_add_member)
    parser_roster_add_member.add_argument('name', help='The name of the roster u want to add member')
    parser_roster_add_member.add_argument('realm', help='The name of the character realm')
    parser_roster_add_member.add_argument('charName', help='The name of the character')
    parser_roster_del_member = subparser.add_parser(
        'del_member',
        help='Delete a member to a roster'
    )
    parser_roster_del_member.set_defaults(roster_del_member)
    parser_roster_del_member.add_argument('name', help='The name of the roster u want to add member')
    parser_roster_del_member.add_argument('realm', help='The name of the character realm')
    parser_roster_del_member.add_argument('charName', help='The name of the character')


def roster_create(name, **kwargs):
    pass


def roster_delete(name, **kwargs):
    pass


def roster_add_member(name, realm, charName, **kwargs):
    pass


def roster_del_member(name, realm, charName, **kwargs):
    pass


def roster_refresh(name, **kwargs):
    pass


def roster_get(name, **kwargs):
    pass
