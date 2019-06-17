from . import TestCaseApi


class TestUser(TestCaseApi):
    def test_CreateUser(self):
        username = 'Theogalh'
        password= '1234'
        email = 'theogalh@test.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })

    def test_CreateUserAlreadyExist(self):
        username = 'Theogalh'
        password= '1234'
        email = 'theogalh@test.fr'
        self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 200)
