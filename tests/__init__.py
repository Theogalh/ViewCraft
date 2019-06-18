import unittest
from viewcraft import create_app, db
from viewcraft.config import Config
from viewcraft.models import User
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestCaseApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.testapp = self.app.test_client()
        db.create_all()
        user1 = User(username='Theotest', email='theotest@test.fr')
        user1.set_password('1234AAA@')
        user1.get_token()
        self.headers = {'Authorization': 'Bearer {}'.format(user1.token)}
        db.session.add(user1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
