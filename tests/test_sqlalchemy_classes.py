import unittest

from bestway import app, db, Customer, AcctDetails
from sqlalchemy.exc import IntegrityError


class MyTestCaseSignUp(unittest.TestCase):
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

    def test_duplicate_uname(self):
        c = Customer(uname='jerryben010', password='Password')
        b = Customer(uname='jerryben010', password='Password')
        with app.app_context():
            db.session.add(c)
            db.session.commit()
            db.session.add(b)
            self.assertRaises(IntegrityError)

    def test_new_uname(self):
        c = Customer(uname='jsmith0037', password='Password')
        with app.app_context():
            db.session.add(c)
            db.session.commit()
            self.assertEqual('jsmith0037', c.uname)


class MyTestCaseNewAcct(unittest.TestCase):
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

    def test_good_new_acct(self):
        t = AcctDetails(fname="John", lname='Smith', telephone='6122813772', email='js@js.ca', address1='123 4th St',
                        address2='Apt 304', city='Anytown', state='PA', zip='12345', customer=101)
        with app.app_context():
            db.session.add(t)
            db.session.commit()
            # Check equality of multiple required fields
            self.assertEqual('John', t.fname)
            self.assertEqual('6122813772', t.telephone)
            self.assertEqual(101, t.customer)

    def test_dup_new_acct(self):
        # This will test the database constraint for unique for customer since test is truing to use same
        # value for customer as in test_good_new_acct
        x = AcctDetails(fname="John", lname='Smith', telephone='6122813772', email='js@js.ca', address1='123 4th St',
                        address2='Apt 304', city='Anytown', state='PA', zip='12345', customer='101')
        with app.app_context():
            db.session.add(x)
            db.session.commit()
            self.assertRaises(IntegrityError)

    def test_missing_detail_new_acct(self):
        # This will test is the there is an attempt to instantiate the class with the missing parameter for
        # zip. Test should encounter a TypeError
        with self.assertRaises(TypeError):
            x = AcctDetails(fname="John", lname='Smith', telephone='6122813772', email='js@js.ca', address1='123 4th St',
                            address2='Apt 304', city='Anytown', state='PA', customer='101')
            with app.app_context():
                db.session.add(x)
                db.session.commit()


if __name__ == '__main__':
    unittest.main()
