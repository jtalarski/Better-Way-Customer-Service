# Import necessary Python packages
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, RadioField, SubmitField, ValidationError
from wtforms.validators import InputRequired, Length, Email, EqualTo, AnyOf
import phonenumbers


# Class to set ip a form to create a new username and password combination needed for authentication
# while using the web app. A database rule is that username's must be unique. The validation for
# unique usernames is handled on the server in the log_in route
class NewCustomerForm(FlaskForm):
    uname = StringField('Username', validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


# Class to set up a form for customers to enter basic personal information required to establish
# a basic service account. The class contains a custom validation function which validates the format
# the telephone number provided. Validity check is provided against the python-phonenumbers
# module
class NewAccountDetailForm(FlaskForm):
    fname = StringField('First Name', validators=[InputRequired(), Length(min=3, max=100)])
    lname = StringField('Last Name', validators=[InputRequired(), Length(min=3, max=100)])
    telephone = StringField('Telephone', validators=[InputRequired(),])
    email = StringField('Email', validators=[InputRequired(), Length(min=3, max=100), Email()])
    address1 = StringField('Address Line 1', validators=[InputRequired(), Length(min=3, max=100)])
    address2 = StringField('Address Line 2 (optional)')
    city = StringField('City', validators=[InputRequired(), Length(min=3, max=100)])
    state = StringField('State', validators=[InputRequired(), Length(min=2, max=100)])
    zip = StringField('Zip Code', validators=[InputRequired(), Length(min=5, max=10)])
    submit = SubmitField('Set Up Basic Service')

    def validate_telephone(form, field):
        """
        This function provides WTForms custom validation for the telephone field
        :param field: The telephone field from the NewAccountDetailForm class above
        :return: Will return a ValidationError if the telephone input provided fails validation check
        """
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except ValidationError:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')


# Class to set up a basic username and password input used to authenticate the user when accessing the
# web app. Username and userid are stored as the session.get('id') value and used for authentication
# when accessing different views
class LoginForm(FlaskForm):
    uname = StringField('Username', validators=[InputRequired(), Length(min=3, max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    submit = SubmitField('Log In')


# Class to setup a form that will allow customers to chose the addition of additional entertainment
# packaged to their account
class ChangeForm(FlaskForm):
    movie_pack = BooleanField('I want more movies :', default=False)
    sports_pack = BooleanField('I want more sports :', default=False)
    news_pack = BooleanField('I want more news :', default=False)
    spanish_pack = BooleanField('Mas en español :', default=False)
    submit = SubmitField('Make Changes:')


# A class to set up a form that will allow users the option to write account details to a local file or to delete their
# account from the database. Account deletion is a two step process where the user account detail is deleted
# from the acct_details table first then the customer table. This approach is taken to account for the foreign key
# constraint in the acc_details table. See the change route for additional details.
class AccountActionsForm(FlaskForm):
    dreaded_delete = StringField('Type the word delete to delete your account:', validators=[AnyOf(('delete', "Delete"), message='You must enter delete')])
    confirm_delete = StringField('Type the word delete to confirm:', validators=[AnyOf('delete', 'Delete'), EqualTo('dreaded_delete')])
    delete = SubmitField('Execute')
    print_record = RadioField(label=" ", choices=[('print', 'Select to save')])
    execute = SubmitField('Execute')


# Class to set up a one line form that will allow customers to enter a short string that will be parsed and evaluated
# to provide helpful information to the customer
class HelpSearchForm(FlaskForm):
    help_phrase = StringField(validators=[InputRequired(), Length(min=3, max=80)])
    search = SubmitField('Get help')
