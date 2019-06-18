from . import TestCaseApi


class TestUser(TestCaseApi):
    def test_CreateUser(self):
        username = 'Theogalh'
        password= '1234AAAAQ@'
        email = 'theogalh@test.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 201)

    def test_CreateUserWithUsernameAlreadyExists(self):
        username = 'Theogalh'
        password= '1234QQQ@ded'
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
        self.assertEqual(req.status_code, 400)

    def test_CreateUserWithEmailAlreadyExists(self):
        username = 'Theogalh'
        password= '1234AAA@ded'
        email = 'theogalh@test.fr'
        self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        username = 'Theogalh2'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 400)

    def test_CreateUserWithInvalidEmail(self):
        username = 'Theogalh'
        password= '1234@@@@QQD'
        email = 'theogalhtest.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 400)

    def test_CreateUserWithInvalidPassword(self):
        username = 'Theogalh'
        password= '1234'
        email = 'theogalh@test.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 400)

    def test_GetUsers(self):
        req = self.testapp.get('/api/users', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(req.json), 1)
        username = 'Theogalh'
        password= '1234AAAA@'
        email = 'theogalh@test.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 201)
        req = self.testapp.get('/api/users', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(req.json), 2)
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 400)
        req = self.testapp.get('/api/users', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(req.json), 2)

    def test_GetUserSpecific(self):
        username = 'Theogalh'
        password= '1234AAAA@'
        email = 'theogalh@test.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 201)
        req = self.testapp.get('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.get('/api/users/Theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.get('/api/users/ThEoGaLh', headers=self.headers)
        self.assertEqual(req.status_code, 200)

    def test_GetUserDoesNotExists(self):
        req = self.testapp.get('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 404)

    def test_FollowUser(self):
        username = 'Theogalh'
        password= '1234AAAA@'
        email = 'theogalh@test.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 201)
        req = self.testapp.post('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.post('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 400)

    def test_UnfollowUser(self):
        username = 'Theogalh'
        password= '1234AAAA@'
        email = 'theogalh@test.fr'
        req = self.testapp.post('/api/users', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(req.status_code, 201)
        req = self.testapp.post('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.delete('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.delete('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 400)

    def test_FollowUserDoesNotExists(self):
        req = self.testapp.post('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 404)

    def test_UnfollowUserDoesNotExists(self):
        req = self.testapp.delete('/api/users/theogalh', headers=self.headers)
        self.assertEqual(req.status_code, 404)

    def test_FollowYourself(self):
        req = self.testapp.post('/api/users/theotest', headers=self.headers)
        self.assertEqual(req.status_code, 400)

    def test_UnfollowYourself(self):
        req = self.testapp.delete('/api/users/theotest', headers=self.headers)
        self.assertEqual(req.status_code, 400)

    def test_GetUsersWithoutLogin(self):
        req = self.testapp.get('/api/users/theogalh')
        self.assertEqual(req.status_code, 401)
