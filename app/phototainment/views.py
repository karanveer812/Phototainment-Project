from flask import render_template, request, redirect, url_for, flash, Blueprint, Response
import json
from collections import Counter
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError

import flask_csv

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app.privilege import admin, employee
from datetime import datetime, timedelta, time
from app.forms import LoginForm, RegisterForm, EventForm, EditUser, SearchForm, ChangeStatus, CommentForm, AddressForm, \
    ChangePassword, DayRange, TypeForm, CompanyForm, ReportForm
from app.models import db, User, Event, EventType, Client, AdditionalContact, ReferralContact, Comment, EventVenue, \
    login_manager, Company, EventStatus

custom_bp = Blueprint(
    'phototainment',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('phototainment.login'))


@custom_bp.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if request.method == "POST":
        req_user = db.session.query(User).filter_by(username=form.username.data.lower()).first()
        if req_user:
            if check_password_hash(pwhash=req_user.password, password=form.password.data):
                login_user(user=req_user)
                return redirect(url_for('phototainment.home'))
            else:
                flash(message="Incorrect Password")
        else:
            flash(message="No user found")
    
    return render_template('login.html', form=form)


@custom_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('phototainment.login'))


@custom_bp.route('/change_password/', methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePassword()
    if request.method == "POST":
        if check_password_hash(pwhash=current_user.password, password=form.old_password.data):
            new_password = generate_password_hash(password=form.new_password.data, method='pbkdf2:sha256',
                                                  salt_length=8)
            
            if check_password_hash(pwhash=new_password, password=form.confirm_password.data):
                current_user.password = new_password
                db.session.commit()
                flash(message="Your Password has been changed")
                return redirect(url_for('phototainment.home'))
            else:
                flash(message="Password does not match")
        else:
            flash(message="Old password is not correct")
    return render_template('change-password.html', form=form)


@custom_bp.route("/index", methods=["GET", "POST"])
@login_required
@employee
def home():
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client).order_by('event_date')
    
    event_types = db.session.query(EventType).order_by("event_type")
    
    users = db.session.query(User).order_by("username")
    
    recent_bookings = [event for event in events if datetime.now() - event[0].lead_date < timedelta(days=7)]
    
    pending_events = [event for event in events if
                      datetime.now() - event[0].lead_date < timedelta(days=7) and event[0].status_id == 1]
    completed_events = [event for event in events if
                        datetime.now() - event[0].event_date < timedelta(days=7) and event[0].status_id == 4]
    
    upcoming_events = [event for event in events if
                       event[0].event_date - datetime.now() < timedelta(days=7) and event[
                           0].event_date - datetime.now() > timedelta(days=0, minutes=0, seconds=0)]
    
    associated_companies = [company.company_name for company in
                            db.session.query(Company).order_by('company_name').all()]
    months = []
    graph_data2 = []
    
    for event in events:
        if event[0].lead_date.strftime("%b") in months:
            continue
        else:
            months.append(event[0].lead_date.strftime("%b"))
    
    for month in months:
        monthly_revenue = 0
        for event in events:
            if event[0].lead_date.strftime("%b") == month and event[0].estimated_cost:
                monthly_revenue += int(event[0].estimated_cost)
        graph_data2.append(monthly_revenue)
    
    type_form = TypeForm()
    company_form = CompanyForm()
    
    return render_template(
        "index.html",
        all_bookings=recent_bookings,
        pending_bookings=pending_events,
        completed_bookings=completed_events,
        event_types=event_types,
        upcoming_events=upcoming_events,
        type_form=type_form,
        months=months,
        graph_data2=graph_data2,
        event_num=len(upcoming_events),
        company_form=company_form,
        users=users,
        associated_companies=associated_companies
    )


@custom_bp.route("/add_event_type", methods=["POST"])
@login_required
@admin
def add_event_type():
    type_form = TypeForm()
    new_type = EventType(
        event_type=type_form.type_name.data.lower()
    )
    db.session.add(new_type)
    
    try:
        db.session.commit()
        flash("Event type has been added")
    except IntegrityError:
        flash("Event type already exist")
        db.session.rollback()
    
    return redirect(url_for('phototainment.home'))


@custom_bp.route("/add-company", methods=["POST"])
@login_required
@admin
def add_company():
    company_form = CompanyForm()
    new_company = Company(
        company_name=company_form.company_name.data.lower()
    )
    db.session.add(new_company)
    
    try:
        db.session.commit()
        flash("New Company has been added")
    except IntegrityError:
        flash("Company already exist")
        db.session.rollback()
    
    return redirect(url_for('phototainment.home'))


@custom_bp.route('/search-client', methods=["GET", "POST"])
@login_required
@employee
def client_table():
    clients = db.session.query(Client).all()
    return render_template('client-table.html', clients=clients)


@custom_bp.route('/delete-client/<client_id>')
@login_required
@admin
def delete_client(client_id):
    requested_client = db.session.query(Client).filter_by(client_id=client_id).first()
    if requested_client.events or requested_client.company:
        flash("Client can not be deleted")
    else:
        db.session.delete(requested_client)
        db.session.commit()
        flash("Client has been deleted")
    return redirect(url_for('phototainment.client_table'))


@custom_bp.route('/register-user', methods=["GET", "POST"])
@login_required
@admin
def register():
    form = RegisterForm()
    if request.method == "POST":
        new_user = User(
            username=form.username.data.lower(),
            password=generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8),
            email=form.email.data,
            role_id=form.user_role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("New user has been created")
        return redirect(url_for('phototainment.manage_user'))
    return render_template('register.html', form=form)


@custom_bp.route('/manage-user', methods=["GET"])
@login_required
@admin
def manage_user():
    users = db.session.query(User).order_by('id')
    return render_template('manage-users.html', users=users)


@custom_bp.route('/delete-user/<user_id>')
@login_required
@admin
def delete_user(user_id):
    requested_user = db.session.query(User).filter_by(id=user_id).first()
    if requested_user.events or requested_user.comment:
        flash("User can not be deleted")
    else:
        db.session.delete(requested_user)
        db.session.commit()
        flash("User has been deleted")
    return redirect(url_for('phototainment.manage_user'))


@custom_bp.route('/edit-user/<user_id>', methods=["GET", "POST"])
@login_required
@admin
def edit_user(user_id):
    requested_user = db.session.query(User).filter_by(id=user_id).first()
    edit_form = EditUser(
        username=requested_user.username,
        user_role=requested_user.role_id,
        email=requested_user.email
    )
    
    if request.method == "POST":
        requested_user.username = edit_form.username.data
        requested_user.role_id = edit_form.user_role.data
        requested_user.email = edit_form.email.data
        db.session.commit()
        return redirect(url_for("phototainment.manage_user"))
    
    return render_template('register.html', form=edit_form)


@custom_bp.route('/_companies', methods=['GET'])
@login_required
@employee
def get_companies():
    companies = [company.company_name.title() for company in db.session.query(Company).all()]
    return Response(json.dumps(companies), mimetype='application/json')


@custom_bp.route('/add-event', methods=["GET", "POST"])
@login_required
@employee
def add_event():
    form = EventForm()
    date_today = datetime.now()
    if request.method == "POST":
        new_client = Client(
            client_first_name=form.first_name.data.lower(),
            client_last_name=form.last_name.data.lower(),
            client_email=form.client_email.data.lower(),
            primary_contact=form.primary_contact.data
        )
        db.session.add(new_client)
        db.session.commit()
        if db.session.query(Company).filter_by(company_name=form.company.data.lower()).first():
            new_client.company = db.session.query(Company).filter_by(company_name=form.company.data.lower()).first()
        else:
            if form.company.data:
                new_company = Company(company_name=form.company.data.lower())
                db.session.add(new_company)
                db.session.commit()
                
                new_client.company = new_company
                db.session.commit()
        alt_contact = ""
        ref_contact = ""
        if form.alt_contact.data and form.alt_contact_name.data:
            alt_contact = AdditionalContact(
                mobile_number=form.alt_contact.data,
                contact_name=form.alt_contact_name.data.lower()
            )
            db.session.add(alt_contact)
            db.session.commit()
        
        if form.referrer_contact.data and form.referrer_name.data:
            ref_contact = ReferralContact(
                mobile_number=form.referrer_contact.data,
                contact_name=form.referrer_name.data.lower()
            )
            db.session.add(ref_contact)
            db.session.commit()
        
        new_event = Event(
            event_name=form.event_name.data.lower(),
            status_id=1,
            lead_date=date_today,
            event_date=datetime(
                form.event_date.data.year,
                form.event_date.data.month,
                form.event_date.data.day,
                form.start_time.data.hour,
                form.start_time.data.minute),
            start_time=time(
                form.start_time.data.hour,
                form.start_time.data.minute),
            duration=form.duration.data,
            client_id=new_client.client_id,
            
            user_id=current_user.id,
            type_id=form.event_type.data,
            additional_information=form.additional_information.data
        )
        
        if form.estimated_cost.data:
            new_event.estimated_cost = int(form.estimated_cost.data),
        
        if alt_contact != "":
            new_event.phone_id = alt_contact.phone_id
        
        if ref_contact != "":
            new_event.referee_id = ref_contact.referee_id
        
        db.session.add(new_event)
        db.session.commit()
        
        flash(message="New event has been created")
        return redirect(url_for('phototainment.view_booking', booking_id=new_event.booking_id))
    return render_template('add_event.html', form=form, today=date_today)


@custom_bp.route('/delete-event/<booking_id>')
@login_required
@admin
def delete_event(booking_id):
    event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    venue = event.venue
    contact = event.contacts
    comments = db.session.query(Comment).filter_by(booking_id=booking_id).all()
    
    if comments:
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
    if contact:
        db.session.delete(contact)
        db.session.commit()
    db.session.delete(event)
    db.session.commit()
    if venue:
        db.session.delete(venue)
        db.session.commit()
    flash("Event has been deleted")
    return redirect(url_for('phototainment.search_event'))


@custom_bp.route('/search', methods=["GET", "POST"])
@login_required
@employee
def search_event():
    form = SearchForm()
    search_for = form.search.data
    
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client).order_by('event_date')
    
    if form.search.data != "":
        if form.is_submitted():
            if form.search.data != "":
                if form.search_fname.data:
                    search_by = "client_first_name"
                    events = events.filter(Client.__table__.c[search_by].like(search_for.lower()))
                elif form.search_lname.data:
                    search_by = "client_last_name"
                    events = events.filter(Client.__table__.c[search_by].like(search_for.lower()))
                elif form.search_email.data:
                    search_by = "client_email"
                    events = events.filter(Client.__table__.c[search_by].like(search_for.lower()))
                elif form.search_contact.data:
                    search_by = "primary_contact"
                    events = events.filter(Client.__table__.c[search_by].like(search_for.lower()))
                elif form.search_evname.data:
                    search_by = "event_name"
                    events = events.filter(Event.__table__.c[search_by].like(search_for.lower()))
                elif form.search_evtype.data:
                    type_name = db.session.query(EventType).filter(
                        EventType.__table__.c['event_type'].like(search_for)).first()
                    if type_name:
                        search_for = type_name.type_id
                    events = [event for event in events if event[0].type_id == search_for]
                elif form.search_staff.data:
                    user_name = db.session.query(User).filter(
                        User.__table__.c['username'].like(f"{search_for}%")).first()
                    if user_name:
                        search_for = user_name.id
                    events = [event for event in events if event[0].user_id == search_for]
                
                elif form.search_status.data:
                    status = db.session.query(EventStatus).filter(
                        EventStatus.__table__.c['status'].like(f"{search_for}%")).first()
                    if status:
                        search_for = status.status_id
                    events = [event for event in events if event[0].status_id == search_for]
    
    return render_template('search-event.html', form=form, filtered_events=events)


@custom_bp.route('/view_booking/<booking_id>', methods=["GET", "POST"])
@login_required
@employee
def view_booking(booking_id):
    event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    if event.contacts:
        alt_contacts = f'{event.contacts.contact_name}: {event.contacts.mobile_number}'
    else:
        alt_contacts = ""
    
    if event.referred_by:
        ref_contact = f'{event.referred_by.contact_name}: {event.referred_by.mobile_number}'
    else:
        ref_contact = ""
    status_form = ChangeStatus()
    comment_form = CommentForm()
    venue = ""
    if event.venue:
        venue = event.venue
    
    print(type(list(event.comment)))
    
    return render_template('event-view.html',
                           event=event,
                           alt_contact=alt_contacts,
                           ref_contact=ref_contact,
                           event_venue=venue,
                           status_form=status_form,
                           comment_form=comment_form,
                           comments=db.session.query(Comment).order_by(desc('comment_time')))


@custom_bp.route('/add_status_comment/<booking_id>', methods=["POST"])
@login_required
@employee
def status_comment(booking_id):
    event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    status_form = ChangeStatus()
    if status_form.is_submitted():
        if status_form.status_processing.data:
            event.status_id = 1
        elif status_form.status_approved.data:
            event.status_id = 2
        elif status_form.status_in_process.data:
            event.status_id = 3
        elif status_form.status_Completed.data:
            event.status_id = 4
        elif status_form.status_canceled.data:
            event.status_id = 5
        db.session.commit()
        
        status_comment = Comment(
            user_id=current_user.id,
            booking_id=booking_id,
            comment_action=f"Changed status to {event.status.status}",
            comment_time=datetime.now()
        )
        db.session.add(status_comment)
        db.session.commit()
        return redirect(url_for('phototainment.view_booking', booking_id=booking_id))


@custom_bp.route('/add_comment/<booking_id>', methods=["POST"])
@login_required
@employee
def add_comment(booking_id):
    comment_form = CommentForm()
    if comment_form.is_submitted():
        new_comment = Comment(
            user_id=current_user.id,
            booking_id=booking_id,
            comment_time=datetime.now(),
            comment_action=comment_form.comment_action.data,
            comment_reason=comment_form.comment_reason.data
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('phototainment.view_booking', booking_id=booking_id))


@custom_bp.route('/delete_comment/<comment_id>')
@login_required
@admin
def delete_comment(comment_id):
    comment = db.session.query(Comment).filter_by(comment_id=comment_id).first()
    booking_id = comment.booking_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('phototainment.view_booking', booking_id=booking_id))


@custom_bp.route('view_booking/<booking_id>/add_address', methods=["GET", "POST"])
@login_required
@employee
def add_address(booking_id):
    event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    address_form = AddressForm()
    if request.method == "POST":
        address = EventVenue(
            street_address=address_form.street_address.data.lower(),
            suburb=address_form.suburb.data.lower(),
            state=address_form.state.data.lower(),
            post_code=address_form.post_code.data
        )
        db.session.add(address)
        db.session.commit()
        
        new_comment = Comment(
            user_id=current_user.id,
            booking_id=booking_id,
            comment_action=f"Approved booking and updated address details"
        )
        db.session.add(new_comment)
        db.session.commit()
        
        event.venue_id = address.venue_id
        event.status_id = 2
        db.session.commit()
        return redirect(url_for('phototainment.view_booking', booking_id=booking_id))
    
    return render_template("add-address.html", form=address_form)


@custom_bp.route('view_booking/<booking_id>/edit_address', methods=["GET", "POST"])
@login_required
@employee
def edit_address(booking_id):
    event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    address_form = AddressForm(
        street_address=event.venue.street_address,
        suburb=event.venue.suburb,
        state=event.venue.state,
        post_code=event.venue.post_code
    )
    if request.method == "POST":
        event.venue.street_address = address_form.street_address.data.lower()
        event.venue.suburb = address_form.suburb.data.lower()
        event.venue.state = address_form.state.data.lower()
        event.venue.post_code = address_form.post_code.data
        
        db.session.commit()
        
        return redirect(url_for('phototainment.view_booking', booking_id=booking_id))
    
    return render_template("add-address.html", form=address_form)


@custom_bp.route('/upcoming-events', methods=['GET', 'POST'])
@login_required
@employee
def upcoming_events():
    form = DayRange()
    days = 30
    print(form.days.data)
    if request.method == "POST":
        days = int(form.days.data.split()[0])
    
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client).order_by('event_date')
    filtered_event = [event for event in events if
                      event[0].event_date - datetime.now() < timedelta(days=days) and event[
                          0].event_date - datetime.now() > timedelta(days=0, minutes=0, seconds=0)]
    return render_template('upcoming-events.html', filtered_events=filtered_event, days=days, form=form)


@custom_bp.route('/edit-event/<booking_id>', methods=["GET", "POST"])
@login_required
@employee
def edit_event(booking_id):
    current_event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    
    alt_contact = ""
    alt_contact_name = ""
    referrer_contact = ""
    referrer_name = ""
    company_name = ""
    
    if current_event.contacts:
        alt_contact = current_event.contacts.mobile_number
        alt_contact_name = current_event.contacts.contact_name
    if current_event.referred_by:
        referrer_contact = current_event.contacts.mobile_number
        referrer_name = current_event.contacts.contact_name
    if current_event.client.company:
        company_name = current_event.client.company.company_name
    
    form = EventForm(
        first_name=current_event.client.client_first_name,
        last_name=current_event.client.client_last_name,
        company=company_name,
        client_email=current_event.client.client_email,
        primary_contact=current_event.client.primary_contact,
        event_name=current_event.event_name,
        event_date=current_event.event_date,
        start_time=current_event.start_time,
        duration=current_event.duration,
        event_type=current_event.type_id,
        estimated_cost=current_event.estimated_cost,
        
        alt_contact=alt_contact,
        alt_contact_name=alt_contact_name,
        
        referrer_contact=referrer_contact,
        referrer_name=referrer_name,
        
        additional_information=current_event.additional_information,
    )
    
    if request.method == "POST":
        current_event.client.client_first_name = form.first_name.data.lower()
        current_event.client.client_last_name = form.last_name.data.lower()
        
        if db.session.query(Company).filter_by(company_name=form.company.data.lower()).first():
            current_event.client.company = db.session.query(Company).filter_by(
                company_name=form.company.data.lower()).first()
        else:
            if form.company.data:
                new_company = Company(company_name=form.company.data.lower())
                db.session.add(new_company)
                current_event.client.company = new_company
        
        current_event.client.primary_contact = form.primary_contact.data
        current_event.event_name = form.event_name.data
        current_event.event_date = form.event_date.data
        current_event.start_time = form.start_time.data
        current_event.duration = form.duration.data
        current_event.estimated_cost = int(form.estimated_cost.data)
        current_event.type_id = form.event_type.data
        current_event.additional_information = form.additional_information.data
        
        if current_event.contacts:
            current_event.contacts.mobile_number = form.alt_contact.data
            current_event.contacts.contact_name = form.alt_contact_name.data
        else:
            if form.alt_contact.data and form.alt_contact_name.data:
                new_contact = AdditionalContact(contact_name=form.alt_contact_name.data.lower(),
                                                mobile_number=form.alt_contact.data)
                db.session.add(new_contact)
                db.session.commit()
                current_event.contacts = new_contact
        
        if current_event.referred_by:
            current_event.referred_by.mobile_number = form.referrer_contact.data
            current_event.referred_by.contact_name = form.referrer_name.data
        else:
            if form.alt_contact.data and form.alt_contact_name.data:
                new_contact = ReferralContact(contact_name=form.referrer_name.data.lower(),
                                              mobile_number=form.referrer_contact.data)
                db.session.add(new_contact)
                db.session.commit()
                current_event.referred_by = new_contact
        
        db.session.commit()
        return redirect(url_for('phototainment.view_booking', booking_id=current_event.booking_id))
    return render_template('edit-event.html', form=form)


@custom_bp.route('/charts', methods=["GET", "POST"])
@login_required
@employee
def charts():
    form = DayRange()
    days = 30
    if request.method == "POST":
        days = int(form.days.data.split()[0])
    
    events = db.session.query(Event).order_by('lead_date')
    filtered_event = [event for event in events if datetime.now() - event.lead_date < timedelta(days=days)]
    
    type_names = [event.type.event_type for event in filtered_event]
    status_names = [event.status.status for event in filtered_event]
    
    months = []
    graph_data2 = []
    
    for event in events:
        if event.lead_date.strftime("%b") in months:
            continue
        else:
            months.append(event.lead_date.strftime("%b"))
    
    for month in months:
        monthly_revenue = 0
        for event in events:
            if event.lead_date.strftime("%b") == month and event.estimated_cost:
                monthly_revenue += int(event.estimated_cost)
        graph_data2.append(monthly_revenue)
    
    available_types = []
    events_revenue = []
    for event in events:
        if event.type.event_type in available_types:
            continue
        else:
            available_types.append(event.type.event_type)

    for event_type in available_types:
        event_revenue = 0
        for event in events:
            if event.type.event_type == event_type and event.estimated_cost:
                event_revenue += int(event.estimated_cost)
        events_revenue.append(event_revenue)
        
    print(events_revenue)
    

    
    doughnut_chart_data = dict(Counter(status_names))
    bar_graph_data = dict(Counter(type_names))
    
    return render_template('charts.html',
                           bar_graph_data=bar_graph_data,
                           doughnut_chart_data=doughnut_chart_data,
                           months=months,
                           graph_data2=graph_data2,
                           form=form,
                           available_types=available_types,
                           events_revenue=events_revenue
                           )


@custom_bp.route('/get-report', methods=["GET", "POST"])
@login_required
@admin
def generate_report():
    today = datetime.now()
    start_date = today - timedelta(days=30)
    
    report_form = ReportForm()
    
    for user in User.query.order_by('username'):
        report_form.user_field.choices.append((user.id, user.username))
    
    for event_type in EventType.query.order_by('event_type'):
        report_form.event_type.choices.append((event_type.type_id, event_type.event_type))
    
    for status in EventStatus.query.order_by('status'):
        report_form.status.choices.append((status.status_id, status.status))
    
    for company in Company.query.order_by('company_name'):
        report_form.company.choices.append((company.company_id, company.company_name))
    
    return render_template('report.html', today=today, start_date=start_date, form=report_form)


@custom_bp.route('/download-report', methods=["POST"])
@login_required
@admin
def download_report():
    events = db.session.query(Event).order_by('event_date')
    
    report_form = ReportForm()
    
    filtered_event = [event for event in events if
                      report_form.from_date.data < event.lead_date.date() < report_form.to_date.data + timedelta(
                          days=1)]
    if int(report_form.event_type.data) != 0:
        filtered_event = [event for event in filtered_event if event.type.type_id == int(report_form.event_type.data)]
    
    if int(report_form.user_field.data) != 0:
        filtered_event = [event for event in filtered_event if event.user.id == int(report_form.user_field.data)]
    
    if int(report_form.status.data) != 0:
        filtered_event = [event for event in filtered_event if event.status.status_id == int(report_form.status.data)]
    
    company_events = []
    if int(report_form.company.data) != 0:
        for event in filtered_event:
            if event.client.company:
                if event.client.company.company_id == int(report_form.company.data):
                    company_events.append(event)
        filtered_event = company_events
    
    data = []
    
    for event in filtered_event:
        company_name = ""
        alt_contact = ""
        alt_contact_name = ""
        ref_contact = ""
        ref_contact_name = ""
        address = ""
        if event.client.company:
            company_name = event.client.company.company_name
        if event.contacts:
            alt_contact = event.contacts.mobile_number
            alt_contact_name = event.contacts.contact_name.title()
        
        if event.referred_by:
            ref_contact = event.referred_by.mobile_number
            ref_contact_name = event.referred_by.contact_name.title()
        
        if event.venue:
            street_address = event.venue.street_address.title()
            suburb = event.venue.suburb.title()
            state = event.venue.suburb.title()
            post_code = event.venue.post_code
            address = f"{street_address}, {suburb}, {state}, {post_code}"
        
        data.append({
            'Name': f"{event.client.client_first_name.title()} {event.client.client_last_name.title()}",
            'Event Name': event.event_name.title(),
            'Company Name': company_name,
            'Type': event.type.event_type.title(),
            'Date Added': event.lead_date.strftime('%d/%m/%y'),
            'Date': event.event_date.strftime('%d/%m/%y'),
            'Time': event.event_date.strftime('%I:%M %p'),
            'Alternative Contact': alt_contact,
            'Alternative Contact Name': alt_contact_name,
            'Referee Contact': ref_contact,
            'Referee Contact Name': ref_contact_name,
            'Venue': address,
            'User': event.user.username.title(),
            'Estimated Cost': event.estimated_cost,
            'Status': event.status.status.title()
        })
    if data:
        return flask_csv.send_csv(data, "report.csv", list(data[0].keys()))
    else:
        flash(message="No data found")
        return redirect(url_for('phototainment.generate_report'))


@custom_bp.route('/forgot_password', methods=["GET", "POST"])
@login_required
@employee
def forgot_password():
    return render_template('forgot-password.html')


@custom_bp.route('/test')
def test():
    return render_template('test.html')
