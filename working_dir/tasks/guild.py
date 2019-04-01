from init import client, config, g
import discord
import asyncio
from models.character import Character
from utils.daemon import Daemon


def get_new_members(json):
    result = []
    for member in json['members']:
        member = member['character']
        try:
            if int(member['level']) == 120:
                char = Character(member['name'], member['realm'], member['guild'], member['level'])
                char.save_db()
                result.append(member['name'])
        except KeyError:
            continue
    return result


def formate_msg(data):
    try:
        msg = 'Player {} {} {}.\n' \
              'Ilvl : {}\n' \
              'Rio Score : {}\n' \
              'Class : {}\n' \
              'Race : {} \n' \
              'Armory : <{}>\n' \
              'RaiderIo : <{}>\n' \
              '-------------------------------------'.format(data['name'],
                                                             data['mod'],
                                                             data['guild'],
                                                             data['ilvl'],
                                                             data['raiderio'],
                                                             data['classe'],
                                                             data['race'],
                                                             data['armory'],
                                                             data['raiderio_link'])
    except KeyError:
        return None
    return msg


async def refresh_guilds():
    await client.wait_until_ready()
    channel = discord.Object(id=config['DISCORD']['CHANNEL_GUILD_ID'])
    while not client.is_closed:
        print('Refreshing guilds...')
        daemon = Daemon(config['RABBITMQ']['USERNAME'], config['RABBITMQ']['PASSWORD'])
        daemon.send_guild(config['REDIS']['DB'])
        list = g['redis'].smembers('guilds:update')
        for char in list:
            data = g['redis'].hgetall(char)
            msg = formate_msg(data)
            if msg:
                await client.send_message(channel, msg)
            g['redis'].srem('guilds:update', char)
        print('Refreshing guilds done.')
        daemon.close()
        await asyncio.sleep(int(config['DEFAULT']['REFRESH_GUILD_TIME']))
