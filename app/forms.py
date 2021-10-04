from flask_wtf import FlaskForm
from app.models import Role, EventType
from app import app
from wtforms import StringField, SubmitField, PasswordField, validators, SelectField
from wtforms.fields.html5 import EmailField, DateField, TimeField, IntegerField
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime

ck_editor = CKEditor()

ck_editor.init_app(app)

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


class RegisterForm(FlaskForm):
    username = StringField("Username",
                           validators=[validators.DataRequired("Please Enter")],
                           render_kw={"placeholder": "Username"}
                           )
    password = PasswordField("Password",
                             validators=[validators.DataRequired("Please Enter")],
                             render_kw={"placeholder": "Password"}
                             )
    job_description = StringField("Job Description",
                                  validators=[validators.DataRequired("Please Enter")],
                                  render_kw={"placeholder": "Job Description"}
                                  )
    user_role = SelectField('Roles',
                       choices=[(role.role_id, role.role_name) for role in Role.query.order_by('role_name')],
                       validators=[validators.DataRequired("Please Enter")])
    submit = SubmitField("Submit")
    

class EditUser(FlaskForm):
    username = StringField("Username", validators=[validators.DataRequired("Please Enter")])
    job_description = StringField("Job Description", validators=[validators.DataRequired("Please Enter")])
    user_role = SelectField('Roles',
                            choices=[(role.role_id, role.role_name) for role in Role.query.order_by('role_name')],
                            validators=[validators.DataRequired("Please Enter")])
    submit = SubmitField("Submit")
    

class EventForm(FlaskForm):
    first_name = StringField("First Name*", validators=[validators.DataRequired("Please Enter")])
    last_name = StringField("Last Name*", validators=[validators.DataRequired("Please Enter")])
    company_name = StringField("Company Name")

    client_email = EmailField("Email Address*",
                              validators=[validators.DataRequired("Please Enter"), validators.Email()])
    primary_contact = IntegerField("Primary Contact*")

    secondary_contact1 = IntegerField("Secondary Contact")
    contact_person1 = StringField("Contact Name")
    
    secondary_contact2 = IntegerField("Secondary Contact")
    contact_person2 = StringField("Contact Name")
    
    event_name = StringField("Event Name*", validators=[validators.DataRequired("Please Enter")])

    event_date = DateField("Start Date*", validators=[validators.DataRequired("Please Enter")])
    start_time = TimeField(validators=[validators.DataRequired("Please Enter")])
    duration = TimeField(validators=[validators.DataRequired("Please Enter")], format='%H:%M')
    event_type = SelectField('Event Type*',
                             choices=[(type.type_id, type.event_type) for type in EventType.query.order_by('event_type')],
                             validators=[validators.DataRequired("Please Enter")])
    additional_information = CKEditorField("Additional Information", validators=[validators.DataRequired()])
    submit = SubmitField("Submit")


class EditEvent(FlaskForm):
    first_name = StringField("First Name*", validators=[validators.DataRequired("Please Enter")])
    last_name = StringField("Last Name*", validators=[validators.DataRequired("Please Enter")])
    company_name = StringField("Company Name*")
    
    client_email = EmailField("Email Address*",
                              validators=[validators.DataRequired("Please Enter"), validators.Email()])
    primary_contact = IntegerField("Primary Contact*")
    
    secondary_contact1 = IntegerField("Secondary Contact")
    contact_person1 = StringField("Last Name", )
    
    secondary_contact2 = IntegerField("Secondary Contact")
    contact_person2 = StringField("Last Name")
    
    event_name = StringField("Event Name*", validators=[validators.DataRequired("Please Enter")])
    
    event_date = DateField("Start Date*", validators=[validators.DataRequired("Please Enter")])
    start_time = TimeField(validators=[validators.DataRequired("Please Enter")])
    duration = TimeField(validators=[validators.DataRequired("Please Enter")])
    event_type = SelectField('Event Type*',
                             choices=[(type.type_id, type.event_type) for type in
                                      EventType.query.order_by('event_type')],
                             validators=[validators.DataRequired("Please Enter")])
    additional_information = CKEditorField("Comment", validators=[validators.DataRequired()])
    submit = SubmitField("Submit")
    

class AddressForm(FlaskForm):
    street_address = StringField("Street Address*", validators=[validators.DataRequired("Please Enter")])
    suburb = StringField("Suburb*", validators=[validators.DataRequired("Please Enter")])
    state = SelectField("State*", choices=('Select', 'VIC', 'NSW', 'QLD', 'ACT', 'TAS', 'NT', 'WA', 'SA'), validators=[validators.DataRequired("Please Enter")])
    post_code = IntegerField("Post Code*")
    submit = SubmitField("Submit")
    


class SearchForm(FlaskForm):
    search = StringField("Search*", render_kw={"placeholder": "Search"})
    
    search_fname = SubmitField("First Name")
    search_lname = SubmitField("Last Name")
    search_email = SubmitField("Email Address")
    search_contact = SubmitField("Contact Number")
    search_evname = SubmitField("Event Name")
    search_evtype = SubmitField("Event Type")
    search_staff = SubmitField("Staff Name")
    
    sort_start_date = SubmitField("Start Date")
    sort_register_date = SubmitField("Register Date")
    sort_end_date = SubmitField("End Date")
    
    
class ChangeStatus(FlaskForm):
    status_processing = SubmitField("Waiting Approval")
    status_approved = SubmitField("Processing")
    status_in_process = SubmitField("On Going")
    status_Completed = SubmitField("Completed")
    status_canceled = SubmitField("Canceled")


class CommentForm(FlaskForm):
    comment_action = StringField("Action", validators=[validators.DataRequired("Please Enter")])
    comment_reason = StringField("Reason", validators=[validators.DataRequired("Please Enter")])
    add_comment = SubmitField("Add")
    
    
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
