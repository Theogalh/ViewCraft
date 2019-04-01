from init import client, config, g
import asyncio
from models.character import Character
import requests
import discord


def get_average_roster_ilvl():
    ilvl = 0
    count = 0
    chars = []
    fchars = []
    for member in g['redis'].smembers('roster'):
        char = Character(member.split(':')[1], member.split(':')[0], None, 120)
        char.refresh(roster=True)
        count += 1
        ilvl = ilvl + char.ilvl
        chars.append(char)
    if ilvl == 0:
        return 0
    for char in chars:
        if char.ilvl < ilvl / count:
            fchars.append(char.name + '({})'.format(char.ilvl))
    return ilvl / count, fchars


async def refresh_affixes():
    await client.wait_until_ready()
    print('Refreshing affixes...')
    try:
        channel = client.get_channel(config['DISCORD']['CHANNEL_AFFIXES_ID'])
    except KeyError:
        return
    url = 'https://raider.io/api/v1/mythic-plus/affixes?region={}&locale={}'.format(
        config['DEFAULT']['REGION'],
        config['DEFAULT']['LOCALE'].split('_')[0]
    )
    while not client.is_closed:
        old = g['redis'].get('affixes')
        req = requests.get(url)
        if req.status_code == 200:
            req = req.json()
            if old != req['title']:
                embed = discord.Embed(title="Affixes de la semaine", colour=discord.Colour(0x6e5b4))
                for affixes in req['affix_details']:
                    print(affixes)
                    embed.add_field(name=affixes['name'],
                                    value=affixes['description'])
                try:
                    await client.send_message(channel, embed=embed)
                except Exception as e:
                    print(e)
                    raise Exception(e)
                g['redis'].set('affixes', req['title'])
        print('Refreshing Affixes done.')
        await asyncio.sleep(3600)
