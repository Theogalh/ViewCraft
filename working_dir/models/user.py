from viewcraft.models.resource import Resource
from viewcraft.utils import database_required, normalize_names, hash_password, apikey_generate
from flask import g, current_app
from jwt import DecodeError
from binascii import Error as binasciierror
from base64 import b64decode
import jwt


class AuthenticationError(Exception):
    """Exception class for every authentication error"""
    pass


class UserResource(Resource):
    def __init__(self, name):
        super().__init__(name)
        self._log_via_apikey = False
        self._log_via_jwt = False
        self._admin = False
        self._rosters = []
        self._guilds = []
        self._password = None
        self._active = False

        self._authenticated = False
        self._anonymous = False

    @classmethod
    @database_required
    def from_db(cls, name):
        user = super().from_db(name)
        # Charger les guildes
        # Charger les rosters
        return user

    @database_required
    def save_db(self):
        super().save_db()
        # Save les guilds
        # Save les rosters

    @database_required
    def delete_db(self):
        super().delete_db()
        # Delete les roster
        # Delete la liste des guildes suivis

    @classmethod
    @database_required
    def create(cls, firstname, lastname, email, pseudo, password, admin=False):
        try:
            nfirstname, nlastname = normalize_names(firstname, lastname)
        except ValueError:
            raise
        # TODO Check si le pseudo existe deja.
        # TODO Check si le mail existe deja.
        # TODO Check si le password est valide
        user = cls(pseudo)
        user.property_set('firstname', firstname.capitalize())
        user.property_set('lastname', lastname.capitalize())
        user.property_set('nfirstname', nfirstname)
        user.property_set('nlastname', nlastname)
        user.property_set('email', email)
        user.property_set('admin', admin)

        password, salt = hash_password(password)
        user.property_set('password', password)

        user.save_db()
        return user

    def check_password(self, password):
        try:
            hashed_password, salt = hash_password(password, self._password)
            if hashed_password == self._password:
                return True
        except:
            return False
        return False

    @classmethod
    def from_bearer_auth(cls, key):
        """

        :param key:
        :return:
        """

        user = None
        try:
            payload = jwt.decode(key, current_app.config.get('JWT_TOKEN_SECRET'))
            user = UserResource.from_db(payload['sub'])
            log_jwt = True
        except DecodeError:
            pass
        if not user:
            log_jwt = False
            username = g.redis.get('keys:{}'.format(key))
            if not username:
                raise AuthenticationError
            user = cls.from_db(username)
        if not user or not user.active:
            raise AuthenticationError

        user.log_via_apikey = True
        user.log_via_jwt = log_jwt
        user.authenticated = True
        return user

    @classmethod
    def from_password(cls, pseudo, password):
        user = cls.from_db(pseudo)
        if not user or not user.active or not user.check_password(password):
            raise AuthenticationError
        return user

    @classmethod
    def from_basic_auth(cls, basic):
        """Create a User object based on a http basic auth
        :param basic: The base64 string supplied in the HTTP header
        :returns: A UserResource object
        :raises AuthenticationError: If the base64 is wrong, username doesn't exists, password is wrong.
        """
        try:
            basic_decoded = b64decode(basic).decode('utf8').split(':')
            username = basic_decoded[0]
            password = ':'.join(basic_decoded[1:])
        except binasciierror:
            raise AuthenticationError
        except ValueError:
            raise AuthenticationError
        except IndexError:
            raise AuthenticationError
        try:
            user = cls.from_db(username)
        except IndexError:
            raise AuthenticationError
        if not user or not user.active or not user.check_password(password):
            raise AuthenticationError
        user.authenticated = True
        return user

    @database_required
    def apikey_renew(self):
        """Regenerate a apikey for a user
        :returns: The new apikey
        """
        try:
            oldkey = self.properties['apikey']
        except KeyError:
            oldkey = None
        newkey = apikey_generate()
        self.property_set('apikey', newkey)
        if oldkey:
            g.redis.delete('keys:{0}'.format(oldkey))
        g.redis.set('keys:{0}'.format(newkey), self.id)
        self.save_db()
        return newkey

    @property
    def path(self):
        return 'user:{}'.format(self.id)

    @property
    def active(self):
        return self._active

    @property
    def admin(self):
        return self._admin

    @admin.setter
    def admin(self, admin):
        self._admin = admin

    @property
    def log_via_apikey(self):
        """If True the user is loggued via an apikey"""
        return self._log_via_apikey

    @log_via_apikey.setter
    def log_via_apikey(self, via):
        """Set to True if the user is loggued via an apikey
        :param via: True is the user is loggued via an apikey, otherwise set it to false
        """
        self._log_via_apikey = via

    @property
    def log_via_jwt(self):
        """If True the user is loggued via an jwt"""
        return self._log_via_jwt

    @log_via_jwt.setter
    def log_via_jwt(self, via):
        """Set to True if the user is loggued via an jwt
        :param via: True is the user is loggued via an jwt, otherwise set it to false
        """
        self._log_via_jwt = via

    @property
    def authenticated(self):
        """True if the user is authenticated, needed for Flask-Login"""
        return self._authenticated

    @authenticated.setter
    def authenticated(self, value):
        """Setter for the authenticated property, needed for Flask-Login
        :param value: True if the user is authenticated, False otherwise
        """
        self._authenticated = True

    def is_authenticated(self):
        """True if the user is authenticated, needed for Flask-Login
        :returns: True if the user is authenticated, False otherwise
        """
        return self._authenticated

    def is_active(self):
        """True if the user is active, needed for Flask-Login
        :returns: True if the user is active, False otherwise
        """
        return self._active

    def is_anonymous(self):
        """True if the user is anonymous, needed for Flask-Login
        :returns: True if the user is anonymous, False otherwise
        """
        return self._anonymous

    def get_id(self):
        """Return the id of the User, needed for Flask-Login
        :returns: The user id
        """
        return self.id
