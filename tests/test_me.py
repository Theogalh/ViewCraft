from . import TestCaseApi


class TestMe(TestCaseApi):
    def test_GetMe(self):
        req = self.testapp.get('/api/me', headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.get('/api/me')
        self.assertEqual(req.status_code, 401)

    def test_PostAboutMe(self):
        req = self.testapp.post('/api/me', data={'about_me': 'Testing about me'}, headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.post('/api/me', data={'about_me': 'Testing about me'})
        self.assertEqual(req.status_code, 401)
        req = self.testapp.get('/api/me', headers=self.headers)
        self.assertEqual(req.json['about_me'], 'Testing about me')

    def test_DeleteMe(self):
        req = self.testapp.delete('/api/me', headers=self.headers)
        self.assertEqual(req.status_code, 204)
        req = self.testapp.delete('/api/me', headers=self.headers)
        self.assertEqual(req.status_code, 401)

    def test_ChangePassword(self):
        req = self.testapp.post('/api/me/password', data={'password': 'Testing_password',
                                                          'oldPassword': '1234AAA@'},
                                headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.post('/api/me/password', data={'password': 'Testing_password',
                                                          'oldPassword': '1234AAA@'})
        self.assertEqual(req.status_code, 401)
        req = self.testapp.post('/api/me/password', data={'password': '1234',
                                                          'oldPassword': 'Testing_password'},
                                headers=self.headers)
        self.assertEqual(req.status_code, 400)
        req = self.testapp.post('/api/me/password', data={'password': '1234@@@@@qq',
                                                          'oldPassword': 'Tdawdwad'},
                                headers=self.headers)
        self.assertEqual(req.status_code, 403)

    def test_ChangeEmail(self):
        req = self.testapp.post('/api/me/email', data={'email': 'test@lolifr.lol'}, headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = self.testapp.post('/api/me/email', data={'email': 'test@lolifr.lol'}, headers=self.headers)
        self.assertEqual(req.status_code, 400)
        req = self.testapp.post('/api/me/email', data={'email': 'test@lolifr.lol'})
        self.assertEqual(req.status_code, 401)
        req = self.testapp.post('/api/me/email', data={'email': 'testlolifr.lol'}, headers=self.headers)
        self.assertEqual(req.status_code, 400)
