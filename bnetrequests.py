import requests


class BnetRequests:
    def __init__(self, id, secret, region, locale):
        self.id = id
        self.secret = secret
        self.token = None
        self.locale = locale
        self.region = region
        self.get_token()
        self.headers = {'Authorization': 'Bearer {}'.format(self.token)}

    def get_token(self):
        body_params = {'grant_type': 'client_credentials'}
        url = 'https://eu.battle.net/oauth/token'.format(self.region)
        req = requests.post(url, data=body_params, auth=(self.id, self.secret))
        if req.status_code != 200:
            raise Exception(ConnectionRefusedError)
        self.token = req.json()['access_token']

    def get(self, url):
        req = requests.get(url, headers=self.headers)
        if req.status_code == 403:
            self.get_token()
            req = requests.get(url, headers=self.headers)
        return req

    def get_guild(self, server, guildname, field):
        url = 'https://{}.api.blizzard.com/wow/guild/{}/{}?fields={}&locale={}'.format(self.region,
                                                                                       server,
                                                                                       guildname,
                                                                                       field,
                                                                                       self.locale)
        req = self.get(url)
        return req

    def get_player(self, server, charName, field):
        url = 'https://{}.api.blizzard.com/wow/character/{}/{}?fields={}&locale={}'.format(self.region,
                                                                                           server,
                                                                                           charName,
                                                                                           field,
                                                                                           self.locale)
        req = self.get(url)
        return req
