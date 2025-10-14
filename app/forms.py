from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Recipient

class CompanySettingsForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired()])
    address_line1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line2 = StringField('Address Line 2', validators=[Optional()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Update Settings')

class RecipientForm(FlaskForm):
    client_name = StringField('Client Name', validators=[DataRequired(), Length(max=100)])
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=100)])
    address_line2 = StringField('Address Line 2', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    state = StringField('State', validators=[DataRequired(), Length(max=50)])
    zip_code = StringField('Zip Code', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save Recipient')

class InvoiceForm(FlaskForm):
    recipient = QuerySelectField(
        'Recipient',
        query_factory=lambda: Recipient.query.order_by(Recipient.client_name),
        get_pk=lambda a: a.id,
        get_label=lambda a: a.client_name,
        allow_blank=False,
        validators=[DataRequired()]
    )
    date_created = DateField('Date Created', format='%Y-%m-%d', validators=[DataRequired()])
    date_due = DateField('Date Due', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Status', choices=[('OUTSTANDING', 'Outstanding'), ('PAID', 'Paid')], validators=[DataRequired()])
    submit = SubmitField('Save Invoice')