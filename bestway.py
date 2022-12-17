"""
Name: Jim Talarski
Course: CIS189 16516
Module: Final Project
Topic: Main File - Flask App
Assignment: Final Project
"""

from flask import Flask, redirect, url_for, render_template, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from forms import NewCustomerForm, NewAccountDetailForm, LoginForm, \
    ChangeForm, AccountActionsForm
from flask_session import Session

# Overwrites existing text file generated during the /change route
open("my_account_record.txt", "w").close()

# Setup Flask app and connect to the rg sqlalchemy/sqlite 3 database
app = Flask(__name__)
app.secret_key = "wysiwyg2@22"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///bestway.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Alias for the Sqlalchemy app
db = SQLAlchemy(app)


# Create two classes used to create sqlite3 tables
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, uname, password):
        self.uname = uname
        self.password = password

    def __str__(self):
        return f"Username is {self.uname}, password is {self.password} and date created is {self.date_created}"

    def __repr__(self):
        return f"Customer(uname={self.uname}, password={self.password}, date_created={self.date_created}"


class AcctDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    telephone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    address1 = db.Column(db.String(100))
    address2 = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip = db.Column(db.String(10))
    basic_pack = db.Column(db.Boolean, default=True)
    movie_pack = db.Column(db.Boolean, default=False)
    sports_pack = db.Column(db.Boolean, default=False)
    news_pack = db.Column(db.Boolean, default=False)
    spanish_pack = db.Column(db.Boolean, default=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.Column(db.Integer, db.ForeignKey('customer.id'), unique=True)

    def __init__(self, fname, lname, telephone, email, address1, address2, city, state, zip, customer):
        self.fname = fname
        self.lname = lname
        self.telephone = telephone
        self.email = email
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip
        self.customer = customer

    def __str__(self):
        return f'fname is {self.fname}, lname is {self.lname}, telephone is {self.telephone}, email is {self.email}, ' \
               f'address1 is {self.address1}, address2 is {self.address2}, city is {self.city}, state is {self.state}.' \
               f'zip is {self.zip}, updated is {self.updated}, and customer is {self.customer}'

    def __repr__(self):
        return f"NewAcctDetails(fname={self.fname}, lname={self.lname}, telephone={self.telephone}, " \
               f"email={self.email},address1={self.address1}, address2={self.address2}, city={self.city}, " \
               f"state={self.state}, zip={self.zip}, basic_pack={self.basic_pack}, movie_pack={self.movie_pack}," \
               f"sports_pack={self.sports_pack}, news_pack={self.news_pack}, spanish_pack={self.spanish_pack}," \
               f"update={self.updated}, customer{self.customer}"


# Route for initial landing page
@app.route('/', methods=["GET", "POST"])
def hello():
    return render_template('index.html')


# Route to take in new user credential information
@app.route('/sign_up', methods=["POST", "GET"])
def sign_up():
    form = NewCustomerForm()
    if form.validate_on_submit():
        try:
            u = form.uname.data
            p = form.password.data
            ph = generate_password_hash(p, method='sha256')
            new = Customer(u, ph)
            db.session.add(new)
            db.session.commit()
            flash(f'Account created successfully for {form.uname.data}', category='success')
            return redirect(url_for('login'))
        except IntegrityError:
            flash(f"The username {form.uname.data} is already taken, please try another.", category='danger')
            db.session.rollback()
            return redirect(url_for('sign_up'))
    return render_template("sign_up.html", form=form)


# Route for user credential authentication
@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try_name = Customer.query.filter_by(uname=form.uname.data).first()
        if try_name and check_password_hash(try_name.password, form.password.data):
            flash(f'Login successful for {form.uname.data}', category='success')
            session['id'] = try_name.id
            session['uname'] = try_name.uname
            return redirect(url_for('account'))
        else:
            flash(f'Login unsuccessful {form.uname.data}. Please check username and password', category='danger')
    return render_template("login.html", form=form)


# Route for users to input personal information and establish basic service tier
@app.route('/new_acct', methods=["POST", "GET"])
def new_acct():
    form = NewAccountDetailForm()
    try_id = AcctDetails.query.filter_by(customer=session.get('id')).first()
    if not session.get('id'):
        return redirect(url_for('login'))
    if try_id:
        flash('You have already registered for basic service. Visit the Change Plan page to add additional'
              ' service packages to your account', category='warning')
        return redirect(url_for('hello'))
    if form.validate_on_submit():
        f = form.fname.data
        l = form.lname.data
        t = form.telephone.data
        e = form.email.data
        a1 = form.address1.data
        a2 = form.address2.data
        c = form.city.data
        s = form.state.data
        z = form.zip.data
        ci = session.get('id')
        new = AcctDetails(f, l, t, e, a1, a2, c, s, z, ci)
        db.session.add(new)
        db.session.commit()
        flash(f'Basic service successfully added for {form.fname.data}', category='success')
        return redirect(url_for('account'))
    return render_template("new_acct.html", form=form)


# Route to log user out of the session
@app.route('/logout', methods=["GET"])
def logout():
    flash(f'You have been successfully logged out', category='success')
    # Clear session ''id' and 'uname' which are used for authentication and queries in the app
    session['id'] = None
    session['uname'] = None
    return redirect(url_for('hello'))


# Route to allow users to add or remove additional service packages to their account
@app.route('/change', methods=["GET", "POST"])
def change():
    if not session.get('id'):
        return redirect(url_for('login'))
    form = ChangeForm()
    session['id'] = session.get('id')
    if form.validate_on_submit():
        acct_to_change = AcctDetails.query.filter_by(customer=session.get('id')).first()
        acct_to_change.movie_pack = form.movie_pack.data
        acct_to_change.sports_pack = form.sports_pack.data
        acct_to_change.news_pack = form.news_pack.data
        acct_to_change.spanish_pack = form.spanish_pack.data
        acct_to_change.updated = datetime.utcnow()
        db.session.commit()
        flash('Your services have been updated', category='success')
        return redirect(url_for('account'))
    return render_template('change.html', form=form, values=AcctDetails.query.all())


# Allow users to review their current account settings, save a record of their account settings,
# and delete their account
@app.route('/account', methods=["POST", "GET"])
def account():
    if not session.get('id'):
        return redirect(url_for('login'))
    session['id'] = session.get('id')
    exists = db.session.query(AcctDetails.id).filter_by(customer=session.get('id')).first() is not None
    form = AccountActionsForm()
    if exists:
        if form.dreaded_delete.data == 'delete' and form.confirm_delete.data == 'delete':
            # Delete customer record from account detail table first so there is no issue
            # with foreign key assignment
            AcctDetails.query.filter_by(customer=session.get('id')).delete()
            db.session.commit()
            # Delete customer's username and password from customer table to remove them
            # from the database
            Customer.query.filter_by(id=session.get('id')).delete()
            db.session.commit()
            flash('Your account has been successfully deleted', category="warning")
            return redirect(url_for('hello'))
        if form.print_record.data == "print":
            to_save = AcctDetails.query.all()
            for u in to_save:
                with open("my_account_record.txt", "w") as file:
                    to_save = AcctDetails.query.all()
                    for u in to_save:
                        if u.customer == session['id']:
                            print('In with for save')
                            # Convert datetime into something easier for the customer to read
                            date = datetime.strftime(u.updated, '%b-%d-%y')
                            file.write(f"{u.fname} {u.lname}\n")
                            file.write(f"{u.address1}\n")
                            file.write(f'{u.address2}\n')
                            file.write(f'{u.city} {u.state} {u.zip}\n\n')
                            file.write(f'Date services were last updated: {date}\n\n')
                            file.write(f'Here is what services are setup for your account:\n')
                            file.write(f"You have the basic package: {u.basic_pack}\n")
                            file.write(f"You have the movie package: {u.movie_pack}\n")
                            file.write(f"You have the sports package: {u.sports_pack}\n")
                            file.write(f"You have the news package: {u.sports_pack}\n")
                            file.write(f"You have the Spanish package: {u.spanish_pack}\n")
                            file.write(f"\n\nThank you for watching with BestWay")
                            flash("You account record was saved as 'my_account_record.txt' in your working directory",
                                  "success")
                            return render_template('account.html', values=AcctDetails.query.all(), form=form)
        else:
            return render_template('account.html', values=AcctDetails.query.all(), form=form)
    else:
        flash("Let's get some more information about you and sign you up for basic service", category='info')
        return redirect(url_for('new_acct'))
    # return render_template('account.html', values=AcctDetails.query.all())


if __name__ == '__main__':
    # Add app.context to be sure that app can be accessed during all operations
    with app.app_context():
        db.create_all()
    # Automatically start the flask server in debug when this fie is run from the console
    app.run(debug=True)
