import unittest
from bestway import app, db


class MyTestCase(unittest.TestCase):
    # Test case setup and teardown
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///bestway.sqlite3'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Helper functions
    def new_customer(self, uname, password, confirm_password):
        return self.app.post(
            '/sign_up',
            data=dict(uname=uname, password=password, confirm_password=confirm_password),
            follow_redirects=True
        )

    def login(self, uname, password):
        return self.app.post(
            '/login',
            data=dict(uname=uname, password=password),
            follow_redirects=True
        )

    def new_acct(self, fname, lname, telephone, email, address1, address2, city, state, zip, customer):
        return self.app.post(
            '/new_acct',
            data=dict(fname=fname, lname=lname, telephone=telephone, email=email,
                      addres1=address1, address2=address2, city=city, state=state,
                      zip=zip, customer=customer),
            follow_redirects=True
        )

    # Tests
    def test_signup_form_displays(self):
        response = self.app.get('/sign_up')
        self.assertEqual(response.status_code, 200)

    def test_valid_signup(self):
        self.app.get('/sign_up', follow_redirects=True)
        response = self.new_customer('jsmith2', 'DidItWork', 'DidItWork')
        self.assertIn(b"Account created successfully for", response.data)

    def test_dup_uname_signup(self):
        self.app.get('/sign_up', follow_redirects=True)
        self.new_customer('jsmith2', 'DidItWork', 'DidItWork')
        self.app.get('/sign_up', follow_redirects=True)
        response = self.new_customer('jsmith2', 'DidItWork', 'DidItWork')
        self.assertIn(b'is already taken, please try another', response.data)

    def test_login_form_displays(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_valid_initial_login_with_new_acct_redirect(self):
        self.app.get('/sign_up', follow_redirects=True)
        self.new_customer('jsmith2', 'DidItWork', 'DidItWork')
        self.app.get('/logout', follow_redirects=True)
        self.app.get('/login', follow_redirects=True)
        response = self.login('jsmith2', 'DidItWork')
        self.assertIn(b'Login successful for', response.data)
        response = self.app.get('/new_acct')
        self.assertEqual(response.status_code, 200)

    def test_bad_credential_login(self):
        self.app.get('/sign_up', follow_redirects=True)
        self.new_customer('jsmith2', 'DidItWork', 'DidItWork')
        self.app.get('/logout', follow_redirects=True)
        self.app.get('/login', follow_redirects=True)
        response = self.login('jsmith2', 'HowDidItWork')
        self.assertIn(b'Login unsuccessful', response.data)

if __name__ == '__main__':
    unittest.main()
