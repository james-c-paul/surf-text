'''from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from app import Locations

# Creating Login Form contains email and password
class LoginForm(Form):
    email = StringField("Email", validators=[validators.Length(min=7, max=50), validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])

surf_spots = [(g.id, g.location_name) for g in Locations.query.order_by('location_name')]

class RegisterForm(Form):
    first_name = StringField("Ad", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    last_name = = StringField("Lastname", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    phone = StringField("Phone", validators=[validators.Length(min=7, max=11), validators.DataRequired(message="Please Fill This Field")])
    location1 = SelectField("Location1", choices=surf_spots)
    location2 = SelectField("Location1", choices=surf_spots)
    location3 = SelectField("Location1", choices=surf_spots)
    #username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address")]) #May need to look into dynamic choices values https://wtforms.readthedocs.io/en/2.3.x/fields/
    text_time = DateTimeField('Time', format='%H:%M') # May need to make this a select list
    password = PasswordField("Password", validators=[
        validators.DataRequired(message="Please Fill This Field"),
        validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")
    ])
    confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")]) '''