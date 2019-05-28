from app import db, bnet
from app.data import CLASS, RACE
from datetime import datetime
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

    def refresh(self, index=0, roster=False):
        """
        Refresh all web-data of the character.
        :param index: For retry the bnet request who sometimes failed.
        :param roster: For only refresh the data for the Roster, and not all the character.
        :return: None
        """
        # TODO Ajouter un check sur le last_update pour update une fois par heure max.
        if index > 3:
            return 404
        r = bnet.get_character(self.realm, self.name, "items")
        if r.status_code != 200:
            return self.refresh(index+1)
        r = r.json()
        self.ilevel = int(r["items"]['averageItemLevelEquipped'])
        if roster:
            return
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
        self.update_date = datetime.now()
        # TODO Ajouter le check de MM+.
        # TODO Ajouter le lien warcraftlogs
