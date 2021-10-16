from flask import render_template, request, redirect, url_for, flash, Blueprint
from collections import Counter
from sqlalchemy.exc import IntegrityError

import flask_csv

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app.privilege import admin, employee
from datetime import datetime, timedelta, time
from app.forms import LoginForm, RegisterForm, EventForm, EditUser, SearchForm, ChangeStatus, CommentForm, AddressForm, \
    ChangePassword, DayRange, TypeForm
from app.models import db, User, Event, EventType, Client, AdditionalContact, ReferralContact, Comment, EventVenue, \
    login_manager

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
def home():
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client).order_by('event_date')
    
    event_types = db.session.query(EventType).all()
    
    recent_bookings = [event for event in events if datetime.now() - event[0].lead_date < timedelta(days=7)]
    
    pending_events = [event for event in events if
                      datetime.now() - event[0].lead_date < timedelta(days=7) and event[0].status_id == 1]
    completed_events = [event for event in events if
                        datetime.now() - event[0].event_date < timedelta(days=7) and event[0].status_id == 4]
    
    upcoming_events = [event for event in events if
                       event[0].event_date - datetime.now() < timedelta(days=7) and event[
                          0].event_date - datetime.now() > timedelta(days=0, minutes=0, seconds=0)]
    type_form = TypeForm()
    
    if request.method == 'POST':
        if type_form.is_submitted():
            new_type = EventType(
                event_type=type_form.type_name.data
            )
            db.session.add(new_type)

            try:
                db.session.commit()
            except IntegrityError:
                flash("Event type already exist")
                db.session.rollback()
        
    return render_template(
        "index.html",
        all_bookings=recent_bookings,
        pending_bookings=pending_events,
        completed_bookings=completed_events,
        event_types=event_types,
        upcoming_events=upcoming_events,
        type_form=type_form,
        event_num=len(upcoming_events)
    )


@custom_bp.route('/search-client', methods=["GET", "POST"])
@login_required
@employee
def client_table():
    clients = db.session.query(Client).all()
    return render_template('client-table.html', clients=clients)

@custom_bp.route('/register-user', methods=["GET", "POST"])
@login_required
@admin
def register():
    form = RegisterForm()
    if request.method == "POST":
        new_user = User(
            username=form.username.data.lower(),
            password=generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8),
            job_description=form.job_description.data,
            role_id=form.user_role.data
        )
        db.session.add(new_user)
        db.session.commit()
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
    db.session.delete(requested_user)
    db.session.commit()
    return redirect(url_for('phototainment.manage_user'))


@custom_bp.route('/edit-user/<user_id>', methods=["GET", "POST"])
@login_required
@admin
def edit_user(user_id):
    requested_user = db.session.query(User).filter_by(id=user_id).first()
    edit_form = EditUser(
        username=requested_user.username,
        user_role=requested_user.role_id,
        job_description=requested_user.job_description
    )
    
    if request.method == "POST":
        if edit_form.validate_on_submit():
            requested_user.username = edit_form.username.data
            requested_user.role_id = edit_form.user_role.data
            requested_user.job_description = edit_form.job_description.data
            db.session.commit()
            return redirect(url_for("manage_user"))
    
    return render_template('register.html', form=edit_form)


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
            primary_contact=form.primary_contact.data,
            company_name=form.company_name.data.lower()
        )
        db.session.add(new_client)
        db.session.commit()
        alt_contact = ""
        ref_contact = ""
        if form.alt_contact.data and form.alt_contact_name.data:
            alt_contact = AdditionalContact(
                mobile_number=form.alt_contact.data,
                contact_name=form.alt_contact_name.data
            )
            db.session.add(alt_contact)
            db.session.commit()
        
        if form.referrer_contact.data and form.referrer_name.data:
            ref_contact = ReferralContact(
                mobile_number=form.referrer_contact.data,
                contact_name=form.referrer_name.data
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
        if alt_contact != "":
            new_event.phone_id = alt_contact.phone_id
        
        if ref_contact != "":
            new_event.referee_id = ref_contact.referee_id
        
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('phototainment.view_booking', booking_id=new_event.booking_id))
    return render_template('add_event.html', form=form, today=date_today)


@custom_bp.route('/delete-event/<booking_id>')
@login_required
@admin
def delete_event(booking_id):
    event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    venue = event.venue
    contact = db.session.query(BookingContacts).filter_by(booking_id=booking_id).first()
    comments = db.session.query(Comment).filter_by(booking_id=booking_id).all()
    
    if comments:
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
    if contact:
        phone = contact.phone_numbers
        db.session.delete(contact)
        db.session.delete(phone)
        db.session.commit()
    db.session.delete(event)
    db.session.commit()
    if venue:
        db.session.delete(venue)
        db.session.commit()
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
                    search_by = "type_id"
                    type_name = db.session.query(EventType).filter(
                        EventType.__table__.c['event_type'].like(search_for)).first()
                    if type_name:
                        search_for = type_name.type_id
                    events = events.filter(Event.__table__.c[search_by].like(search_for))
                elif form.search_staff.data:
                    search_by = "user_id"
                    user_name = db.session.query(User).filter(
                        User.__table__.c['username'].like(f"{search_for}%")).first()
                    if user_name:
                        search_for = user_name.id
                    events = events.filter(Event.__table__.c[search_by].like(search_for))
        
        if events:
            if form.sort_register_date.data:
                events = events.order_by("register_date")
            elif form.sort_start_date.data:
                events = events.order_by("event_date")
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
    
    return render_template('event-view.html',
                           event=event,
                           alt_contact=alt_contacts,
                           ref_contact=ref_contact,
                           event_venue=venue,
                           status_form=status_form,
                           comment_form=comment_form,
                           comments=event.comment)


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
            comment_action=f"Changed status to {event.status.status}"
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
            street_address=address_form.street_address.data,
            suburb=address_form.suburb.data,
            state=address_form.state.data,
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
        event.venue.street_address = address_form.street_address.data
        event.venue.suburb = address_form.suburb.data
        event.venue.state = address_form.state.data
        event.venue.post_code = address_form.post_code.data
        
        db.session.commit()
        
        return redirect(url_for('phototainment.view_booking', booking_id=booking_id))
    
    return render_template("edit-address.html", form=address_form)


@custom_bp.route('/upcoming-events', methods=['GET', 'POST'])
@login_required
@employee
def upcoming_events():
    form = DayRange()
    days = 30
    if request.method == "POST":
        days = int(form.days.data)
    
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
    
    if current_event.contacts:
        alt_contact = current_event.contacts.mobile_number
        alt_contact_name = current_event.contacts.contact_name
    if current_event.referred_by:
        referrer_contact = current_event.contacts.mobile_number
        referrer_name = current_event.contacts.contact_name
    
    form = EventForm(
        first_name=current_event.client.client_first_name,
        last_name=current_event.client.client_last_name,
        company_name=current_event.client.company_name,
        client_email=current_event.client.client_email,
        primary_contact=current_event.client.primary_contact,
        event_name=current_event.event_name,
        event_date=current_event.event_date,
        start_time=current_event.start_time,
        duration=current_event.duration,
        event_type=current_event.type_id,
        
        alt_contact=alt_contact,
        alt_contact_name=alt_contact_name,
        
        referrer_contact=referrer_contact,
        referrer_name=referrer_name,
        
        additional_information=current_event.additional_information,
    )
    
    if request.method == "POST":
        print(form.primary_contact.data)
        current_event.client.client_first_name = form.first_name.data
        current_event.client.client_last_name = form.last_name.data
        current_event.client.company_name = form.company_name.data
        current_event.client.primary_contact = form.primary_contact.data
        current_event.event_name = form.event_name.data
        current_event.event_date = form.event_date.data
        current_event.start_time = form.start_time.data
        current_event.duration = form.duration.data
        current_event.type_id = form.event_type.data
        current_event.additional_information = form.additional_information.data
        current_event.contacts.mobile_number = form.alt_contact.data
        current_event.contacts.contact_name = form.alt_contact_name.data
        current_event.referred_by.mobile_number = form.referrer_contact.data
        current_event.referred_by.contact_name = form.referrer_name.data
        
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
        days = int(form.days.data)
    
    events = db.session.query(Event)
    filtered_event = [event for event in events if datetime.now() - event.lead_date < timedelta(days=days)]
    for event in events:
        print(datetime.now() - event.lead_date)
    
    type_names = [event.type.event_type for event in filtered_event]
    status_names = [event.status.status for event in filtered_event]
    
    pie_chart_data = dict(Counter(status_names))
    bar_graph_data = dict(Counter(type_names))
    # line_graph_data = dict(Counter([event.status.status for event in filtered_event]))
    
    for event in events:
        print(event.event_date.strftime("%b"))
    print()
    print(len(filtered_event))
    
    return render_template('charts.html', bar_graph_data=bar_graph_data, pie_chart_data=pie_chart_data, form=form)


@custom_bp.route('/get-report', methods=["GET", "POST"])
@login_required
@admin
def generate_report():
    today = datetime.now()
    start_date = today - timedelta(days=30)
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client).order_by('event_date')
    data = []
    if request.method == "POST":
        if request.form.get('up_coming'):
            filtered_event = [event for event in events if
                              event[0].event_date - datetime.now() < timedelta(days=30) and event[
                                  0].event_date - datetime.now() > timedelta(days=0, minutes=0, seconds=0)]
            data = [
                {
                    'Name': f"{event.client_first_name.title()} {event.client_last_name.title()}",
                    'Type': event[0].type.event_type.title(),
                    'Event Name': event[0].event_name.title(),
                    'Date': event[0].event_date.strftime('%d/%m/%y'),
                    'Time': event[0].event_date.strftime('%I:%M %p'),
                    'Status': event[0].status.status.title()
                }
                for event in filtered_event]
        
        if request.form.get('past_events'):
            
            completed_events = [event for event in events if
                                datetime.strptime(request.form.get('from-date'), '%Y-%m-%d') < event[
                                    0].lead_date < datetime.strptime(request.form.get('to-date'), '%Y-%m-%d')]
            print(completed_events)
            for event in events:
                print(datetime.strptime(request.form.get('from-date'), '%Y-%m-%d') < event[0].lead_date)
                print(event[0].lead_date > datetime.strptime(request.form.get('to-date'), '%Y-%m-%d'))
            data = [
                {
                    'Name': f"{event.client_first_name.title()} {event.client_last_name.title()}",
                    'Type': event[0].type.event_type.title(),
                    'Event Name': event[0].event_name.title(),
                    'Date': event[0].event_date.strftime('%d/%m/%y'),
                    'Time': event[0].event_date.strftime('%I:%M %p'),
                    'Status': event[0].status.status.title()
                }
                for event in completed_events]
        if data:
            return flask_csv.send_csv(data, "report.csv", list(data[0].keys()))
        else:
            flash(message="Please select a valid date range")
    return render_template('report.html', today=today, start_date=start_date)


@custom_bp.route('/download-report', methods=["GET", "POST"])
@login_required
@admin
def download_report():
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client).order_by('event_date')
    data = [
        {
            'Name': f"{event.client_first_name.title()} {event.client_last_name.title()}",
            'Type': event[0].type.event_type.title(),
            'Event Name': event[0].event_name.title(),
            'Date': event[0].event_date.strftime('%d/%m/%y'),
            'Time': event[0].event_date.strftime('%I:%M %p'),
            'Status': event[0].status.status.title()
        }
        for event in events]
    return flask_csv.send_csv(data, "report.csv", list(data[0].keys()))


@custom_bp.route('/forgot_password', methods=["GET", "POST"])
@login_required
@employee
def forgot_password():
    return render_template('forgot-password.html')

@custom_bp.route('/test')
def test():
    return render_template('test.html')
