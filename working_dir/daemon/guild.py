from init import bnet, g, config
from models.character import Character
from tasks.guild import get_new_members
from daemon.utils import get_db


def guild_job(ch, method, properties, body):
    print(' [*] Guild job running...')
    data = body.decode('UTF-8').split(':')
    g['redis'] = get_db(data[1])
    list = g['redis'].smembers('guilds')
    for guild in list:
        old_members = g['redis'].smembers('{}:members'.format(guild))
        req = bnet.get_guild(guild.split(':')[2], guild.split(':')[3], 'members')
        if req.status_code != 200:
            continue
        new_members = get_new_members(req.json())
        name = req.json()['name']
        for member in old_members:
            if member not in new_members:
                try:
                    char = Character.from_db(name, member)
                    char.refresh()
                    if not char.ilvl:
                        g['redis'].srem('{}:members'.format(guild), member)
                        continue
                    if char.ilvl > int(config['DEFAULT']['ILVL_LIMIT']):
                        char.save_leaver(True)
                    g['redis'].sadd('leavers', member)
                    g['redis'].srem('{}:members'.format(guild), member)
                    char.del_db()
                except KeyError:
                    continue
        for member in new_members:
            if member not in old_members:
                try:
                    char = Character.from_db(name, member)
                    char.refresh()
                    if not char.ilvl:
                        g['redis'].sadd('{}:members'.format(guild), member)
                        continue
                    if int(char.ilvl) > int(config['DEFAULT']['ILVL_LIMIT']):
                        char.save_leaver(False)
                    g['redis'].sadd('{}:members'.format(guild), member)
                    g['redis'].srem('leavers', member)
                except KeyError:
                    continue
    print(' [+] Guild job over')
