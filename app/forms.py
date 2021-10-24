#################### Imports #####################

from flask_wtf import FlaskForm
from app.models import Role, EventType, User
from app import app
from wtforms import StringField, SubmitField, PasswordField, validators, SelectField
from wtforms.fields.html5 import EmailField, DateField, TimeField, IntegerField
from flask_ckeditor import CKEditor, CKEditorField


#################### Editor Field #####################
ck_editor = CKEditor()
ck_editor.init_app(app)


#################### Login #####################
class LoginForm(FlaskForm):
    username = StringField("Username",
                           validators=[validators.DataRequired("Please Enter")],
                           render_kw={"placeholder": "Username"}
                           )
    password = PasswordField("Password",
                             validators=[validators.DataRequired("Please Enter")],
                             render_kw={"placeholder": "Password"}
                             )
    submit = SubmitField("Log In")


#################### Register #####################
class RegisterForm(FlaskForm):
    username = StringField("Username",
                           validators=[validators.DataRequired("Please Enter")],
                           render_kw={"placeholder": "Username"}
                           )
    password = PasswordField("Password",
                             validators=[validators.DataRequired("Please Enter")],
                             render_kw={"placeholder": "Password"}
                             )
    email = StringField("Email",
                                  validators=[validators.DataRequired("Please Enter")],
                                  render_kw={"placeholder": "Email", "type": "email"}
                                  )
    user_role = SelectField('Roles',
                       choices=[(role.role_id, role.role_name) for role in Role.query.order_by('role_name')],
                       validators=[validators.DataRequired("Please Enter")])
    submit = SubmitField("Submit")
    

#################### Edit User #####################
class EditUser(FlaskForm):
    username = StringField("Username", validators=[validators.DataRequired("Please Enter")])
    email = StringField("Email", validators=[validators.DataRequired("Please Enter")])
    user_role = SelectField('Roles',
                            choices=[(role.role_id, role.role_name) for role in Role.query.order_by('role_name')],
                            validators=[validators.DataRequired("Please Enter")])
    submit = SubmitField("Submit")
    

#################### Create Booking #####################
class EventForm(FlaskForm):
    first_name = StringField("First Name*", validators=[validators.DataRequired("Please Enter")])
    last_name = StringField("Last Name*", validators=[validators.DataRequired("Please Enter")])
    company = StringField("Company Name", id='city_autocomplete')

    client_email = EmailField("Email Address*",
                              validators=[validators.DataRequired("Please Enter"), validators.Email()])
    primary_contact = IntegerField("Primary Contact*")

    alt_contact = IntegerField("Secondary Contact")
    alt_contact_name = StringField("Contact Name")
    
    referrer_contact = IntegerField("Secondary Contact")
    referrer_name = StringField("Contact Name")
    
    event_name = StringField("Event Name*", validators=[validators.DataRequired("Please Enter")])

    event_date = DateField("Start Date*", validators=[validators.DataRequired("Please Enter")])
    start_time = TimeField(validators=[validators.DataRequired("Please Enter")])
    duration = StringField("Duration*", validators=[validators.DataRequired("Please Enter")])
    event_type = SelectField('Event Type*',
                             choices=[(type.type_id, type.event_type) for type in EventType.query.order_by('event_type')],
                             validators=[validators.DataRequired("Please Enter")])
    additional_information = CKEditorField("Additional Information", validators=[validators.DataRequired()])
    
    estimated_cost = StringField("Estimated Cost")
    submit = SubmitField("Submit")


#################### Address #####################
class AddressForm(FlaskForm):
    street_address = StringField("Street Address*", validators=[validators.DataRequired("Please Enter")])
    suburb = StringField("Suburb*", validators=[validators.DataRequired("Please Enter")])
    state = SelectField("State*", choices=('Select', 'VIC', 'NSW', 'QLD', 'ACT', 'TAS', 'NT', 'WA', 'SA'), validators=[validators.DataRequired("Please Enter")])
    post_code = IntegerField("Post Code*")
    submit = SubmitField("Submit")
    

#################### Address #####################
class SearchForm(FlaskForm):
    search = StringField("Search*", render_kw={"placeholder": "Search"})
    
    search_fname = SubmitField("First Name")
    search_lname = SubmitField("Last Name")
    search_email = SubmitField("Email Address")
    search_contact = SubmitField("Contact Number")
    search_evname = SubmitField("Event Name")
    search_evtype = SubmitField("Event Type")
    search_staff = SubmitField("Staff Name")
    
    search_status = SubmitField("Status")
    
    
#################### Status Dropdown #####################
class ChangeStatus(FlaskForm):
    status_processing = SubmitField("Waiting Approval")
    status_approved = SubmitField("Processing")
    status_in_process = SubmitField("On Going")
    status_Completed = SubmitField("Completed")
    status_canceled = SubmitField("Canceled")


#################### Comment #####################
class CommentForm(FlaskForm):
    comment_action = StringField("Action", validators=[validators.DataRequired("Please Enter")])
    comment_reason = StringField("Reason", validators=[validators.DataRequired("Please Enter")])
    add_comment = SubmitField("Add")
    

#################### Change Password #####################
class ChangePassword(FlaskForm):
    old_password = PasswordField("Old Password",
                                 validators=[validators.DataRequired("Please Enter")],
                                 render_kw={"placeholder": "Old Password"}
                                 )
    new_password = PasswordField("New Password",
                                 validators=[validators.DataRequired("Please Enter")],
                                 render_kw={"placeholder": "New Password"}
                                 )
    confirm_password = PasswordField("Confirm Password",
                                     validators=[validators.DataRequired("Please Enter")],
                                     render_kw={"placeholder": "Confirm Password"}
                                     )
    submit = SubmitField("Update", render_kw={"class": "Confirm-Password"})
    

#################### Select Days #####################
class DayRange(FlaskForm):
    days = SelectField("Days", choices=('30 Days', '15 Days', '7 Days'))
    submit = SubmitField("Submit")


#################### Event Type #####################
class TypeForm(FlaskForm):
    type_name = StringField("Name", validators=[validators.DataRequired("Please Enter")])
    type_description = StringField("Description", validators=[validators.DataRequired("Please Enter")])
    submit = SubmitField("Submit")


#################### Company #####################
class CompanyForm(FlaskForm):
    company_name = StringField("Company Name", validators=[validators.DataRequired("Please Enter")])
    submit = SubmitField("Submit")


#################### Generate Report #####################
class ReportForm(FlaskForm):
    from_date = DateField("From Date")
    to_date = DateField("From Date")
    user_field = SelectField('User', choices=[(0, 'Please select')])
    event_type = SelectField('Event Type', choices=[(0, 'Please select')])
    status = SelectField('Event Status', choices=[(0, 'Please select')])
    company = SelectField('Event Status', choices=[(0, 'Please select')])
    submit = SubmitField("Submit")
