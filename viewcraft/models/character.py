from viewcraft import db, bnet
from viewcraft.data import CLASS, RACE
from datetime import datetime, timedelta
from time import time
import requests


class Character(db.Model):
    """
    Character Models Class.
    A character can be in a multiple Roster, and One guild.
    No CharacterPost.
    """
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(24))
    realm = db.Column(db.String(24))
    region = db.Column(db.String(24))

    classe = db.Column(db.String(24))
    race = db.Column(db.String(24))

    level = db.Column(db.Integer)
    ilevel = db.Column(db.Float)
    rio_score = db.Column(db.Integer)

    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'))

    armory_link = db.Column(db.String(280))
    rio_link = db.Column(db.String(280))
    wlog_link = db.Column(db.String(280))

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Character {}:{}:{}>'.format(self.region, self.realm, self.name)

    def to_dict(self):
        data = {
            'name': self.name,
            'realm': self.realm,
            'region': self.region,
            'class': self.classe,
            'race': self.race,
            'level': self.level,
            'ilevel': self.ilevel,
            'rio_score': self.rio_score,
            '_links': {
                'armory': self.armory_link,
                'raiderio': self.rio_link,
                'warcraftlog': self.wlog_link
            }
        }
        return data

    @property
    def infos(self):
        return self.name, self.realm

    def refresh(self, index=0, created=False):
        """
        Refresh all web-data of the character.
        :param index: For retry the bnet request who sometimes failed.
        :param roster: For only refresh the data for the Roster, and not all the character.
        :param created: For force refresh after creation.
        :return: None
        """
#        if (self.update_date + timedelta(days=1)) > datetime.utcnow() and not created:
#            return
        if index > 3:
            return
        self.region = bnet.region
        r = bnet.get_character(self.realm, self.name, "items")
        if r.status_code != 200:
            raise ValueError(r.json())
        r = r.json()
        self.ilevel = int(r["items"]['averageItemLevelEquipped'])
        self.level = int(r['level'])
        self.classe = CLASS[int(r["class"])]
        self.race = RACE[int(r["race"])]
        self.armory_link = "https://worldofwarcraft.com/fr-fr/character/{}/{}".format(
            self.realm.replace(' ', '-'),
            self.name
        )
        url = 'https://raider.io/api/v1/characters/profile?region={}&realm={}&name={}&fields=mythic_plus_scores'.format(
            bnet.region,
            self.realm,
            self.name
        )
        r = requests.get(url)
        if r.status_code != 200:
            self.rio_score = 0
        else:
            r = r.json()
            self.rio_score = r["mythic_plus_scores"]["all"]
            self.rio_link = r["profile_url"]
        self.wlog_link = "https://www.warcraftlogs.com/character/{}/{}/{}".format(
            bnet.region,
            self.realm.replace(' ', '-'),
            self.name
        )
        self.update_date = datetime.now()


def get_character(realm, charName):
    char = Character.query.filter_by(realm=realm.capitalize(), charName=charName.capitalize()).first()
    if not char:
        char = Character(realm=realm.capitalize(), name=charName.capitalize())
        try:
            char.refresh()
            db.session.add(char)
        except ValueError:
            return None
    return char
