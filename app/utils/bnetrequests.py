import requests

REGIONS = [
    'eu',
    'us',
    'kr',
    'tw'
]

# TODO Rework pour mettre en ligne sur PIP.


class BnetRequests:
    def __init__(self):
        self.id = None
        self.secret = None
        self.token = None
        self.locale = None
        self.region = None
        self.headers = None

    def init_app(self, app):
        self.id = app.config['BNET_ID']
        self.secret = app.config['BNET_SECRET']
        self.token = None
        self.locale = app.config['BNET_LOCALE']
        self.region = app.config['BNET_REGION']
        self.get_token()
        self.headers = {'Authorization': 'Bearer {}'.format(self.token)}

    def get_token(self):
        body_params = {'grant_type': 'client_credentials'}
        url = 'https://{}.battle.net/oauth/token'.format(self.region)
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

    def get_guild(self, realm, guildname, field):
        url = 'https://{}.api.blizzard.com/wow/guild/{}/{}?fields={}&locale={}'.format(self.region,
                                                                                       realm,
                                                                                       guildname,
                                                                                       field,
                                                                                       self.locale)
        req = self.get(url)
        return req

    def get_character(self, realm, charName, field):
        url = 'https://{}.api.blizzard.com/wow/character/{}/{}?fields={}&locale={}'.format(self.region,
                                                                                           realm,
                                                                                           charName,
                                                                                           field,
                                                                                           self.locale)
        req = self.get(url)
        return req

    # @property
    # def region(self):
    #     return self._region
    #
    # @region.setter
    # def region(self, region):
    #     print(region)
    #     if str(region).lower() not in REGIONS:
    #         raise ValueError
    #     else:
    #         self._region = region
