# user_forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms.widgets import DateInput
from datetime import date

# ===============================================
# 1. User Forms (로그인/회원가입)
# ===============================================


class RegistrationForm(FlaskForm):
    # [교수님 요구사항] 프로필 및 역할 필드 추가
    name = StringField('Name',
                       validators=[DataRequired(),
                                   Length(min=2, max=100)])
    contact = StringField('Contact Number',
                          validators=[DataRequired(),
                                      Length(min=10, max=20)])
    user_role = SelectField('Register as',
                            choices=[('guest', 'Guest'), ('host', 'Host')],
                            validators=[DataRequired()])

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(),
                                        EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        from main import User, app
        with app.app_context():
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is already in use. Please choose a different one.'
                )


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


# ===============================================
# 2. Caravan Forms (등록/수정)
# ===============================================


class CaravanForm(FlaskForm):
    name = StringField('Caravan Name',
                       validators=[DataRequired(),
                                   Length(min=2, max=100)])
    location = StringField('Location (City, Area)',
                           validators=[DataRequired(),
                                       Length(min=2, max=100)])
    price_per_day = IntegerField(
        'Price Per Day (KRW)',
        validators=[
            DataRequired(),
            NumberRange(min=1, message='Price must be a positive number.')
        ])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Register Caravan')


# ===============================================
# 3. Search Form (검색)
# ===============================================


class SearchForm(FlaskForm):
    search_query = StringField('Search by Location',
                               validators=[DataRequired()])
    submit = SubmitField('Search')


# ===============================================
# 4. Reservation Form (예약)
# ===============================================


class ReservationForm(FlaskForm):
    start_date = DateField('Start Date',
                           format='%Y-%m-%d',
                           validators=[DataRequired()])
    end_date = DateField('End Date',
                         format='%Y-%m-%d',
                         validators=[DataRequired()])
    submit = SubmitField('Book Now')

    def validate_start_date(self, start_date):
        if start_date.data < date.today():
            raise ValidationError(
                'Reservation start date cannot be in the past.')

    def validate_end_date(self, end_date):
        if end_date.data <= self.start_date.data:
            raise ValidationError('End date must be after the start date.')


# ===============================================
# 5. Review Form (이 부분이 반드시 있어야 합니다!)
# ===============================================
class ReviewForm(FlaskForm):
    rating = SelectField('Rating (1-5)',
                         choices=[(5, '5 - Excellent'), (4, '4 - Good'),
                                  (3, '3 - Average'), (2, '2 - Poor'),
                                  (1, '1 - Terrible')],
                         coerce=int,
                         validators=[DataRequired()])
    comment = TextAreaField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')
