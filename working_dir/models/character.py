from init import g, config, bnet

CLASS = {
    1: "Warrior",
    2: "Paladin",
    3: "Hunter",
    4: "Rogue",
    5: "Priest",
    6: "Death Knight",
    7: "Shaman",
    8: "Mage",
    9: "Warlock",
    10: "Monk",
    11: "Druid",
    12: "Demon Hunter"
}

RACE = {
    1: "Humain",
    2: "Orc",
    3: "Nain",
    4: "Elfe de la nuit",
    5: "Mort vivant",
    6: "Tauren",
    7: "Gnome",
    8: "Troll",
    9: "Gobelin",
    10: "Elfe de sang",
    11: "Draenei",
    22: "Worgen",
    24: "Pandaren N",
    25: "Pandaren A",
    26: "Pandaren H",
    27: "Sacrenuit",
    28: "Tauren de Haut Roc",
    29: "Elfe du vide",
    30: "Draenei Sancteforge",
    34: "Nain sombrefer",
    36: "Orc mag'har",
}


class Character:
    def __init__(self, name, server, guild, level):
        self.name = name
        self.server = server
        self.guild = guild
        self.classe = None
        self.race = None
        self.armory = None
        self.ilvl = None
        self.level = level
        self.raiderio = None
        self.raiderio_link = None
        self.mod = None

    def get_msg(self, leaves):
        if leaves:
            mod = 'left'
        else:
            mod = 'joined'
        msg = 'Player {} {} {}.\n' \
              'Ilvl : {}\n' \
              'Rio Score : {}\n' \
              'Class : {}\n' \
              'Race : {} \n' \
              'Armory : <{}>\n' \
              'RaiderIo : <{}>\n'.format(self.name, mod, self.guild, self.ilvl, self.raiderio, self.classe, self.race,
                                         self.armory, self.raiderio_link)
        return msg

    def save_leaver(self, mod):
        if mod:
            self.mod = 'Left'
        else:
            self.mod = 'joined'
        g['redis'].hmset('leaver:{}:{}'.format(self.server, self.name),
                         self.__dict__)
        g['redis'].sadd('guilds:update', 'leaver:{}:{}'.format(self.server, self.name))

    def refresh(self, index=0, roster=False):
        if index > 3:
            return 404
        r = bnet.get_player(self.server, self.name, "items")
        if r.status_code != 200:
            return self.refresh(index+1)
        r = r.json()
        self.ilvl = int(r["items"]['averageItemLevelEquipped'])
        if roster:
            return
        if self.ilvl < int(config['DEFAULT']['ILVL_LIMIT']):
            return
        self.classe = CLASS[int(r["class"])]
        self.race = RACE[int(r["race"])]
        self.armory = "https://worldofwarcraft.com/fr-fr/character/{}/{}".format(
            self.server,
            self.name
        )
        url = 'https://raider.io/api/v1/characters/profile?region={}&realm={}&name={}&fields=mythic_plus_scores'.format(
            config['DEFAULT']['REGION'],
            self.server,
            self.name
        )
        r = bnet.get(url)
        if r.status_code != 200:
            self.raiderio = 0
        else:
            r = r.json()
            self.raiderio = r["mythic_plus_scores"]["all"]
            self.raiderio_link = r["profile_url"]

    @classmethod
    def from_db(cls, guild, name):
        dict = g['redis'].hgetall('char:{}:{}'.format(guild.capitalize(), name.capitalize()))
        Char = Character(dict['name'], dict['server'], dict['guild'], dict['level'])
        return Char

    def save_db(self):
        g['redis'].hmset('char:{}:{}'.format(self.guild, self.name), {'server': self.server,
                                                                      'guild': self.guild,
                                                                      'name': self.name,
                                                                      'level': self.level})

    def del_db(self):
        g['redis'].delete('char:{}:{}'.format(self.guild, self.name))
