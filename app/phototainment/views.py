from flask import render_template, request, redirect, url_for, flash, Blueprint

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app.privilege import admin, employee
from datetime import datetime, timedelta, time
from app.forms import LoginForm, RegisterForm, EventForm, EditUser, SearchForm, ChangeStatus, CommentForm, AddressForm, \
    ChangePassword, EditEvent
from app.models import db, User, Event, EventType, Client, ContactDetails, BookingContacts, Comment, EventVenue

custom_bp = Blueprint(
    'phototainment',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@custom_bp.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    print('login')
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
                print('true')
                current_user.password = new_password
                db.session.commit()
                flash(message="Your Password has been changed")
                return redirect(url_for('phototainment.home'))
            else:
                flash(message="Password does not match")
        else:
            flash(message="Old password is not correct")
    return render_template('change-password.html', form=form)


@custom_bp.route("/index")
@login_required
def home():
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client)
    
    recent_bookings = [event for event in events if datetime.now() - event[0].lead_date < timedelta(days=7)]
    
    pending_events = events.filter(Event.__table__.c['status_id'].like(1))
    completed_events = events.filter(Event.__table__.c['status_id'].like(4))
    return render_template(
        "index.html",
        all_bookings=recent_bookings,
        pending_bookings=pending_events,
        completed_bookings=completed_events
    )


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
        
        new_event = Event(
            event_name=form.event_name.data.lower(),
            status_id=1,
            lead_date=datetime.now(),
            event_date=datetime(
                form.event_date.data.year,
                form.event_date.data.month,
                form.event_date.data.day,
                form.start_time.data.hour,
                form.start_time.data.minute),
            start_time=time(
                form.start_time.data.hour,
                form.start_time.data.minute),
            duration=time(
                form.duration.data.hour,
                form.duration.data.minute),
            client_id=new_client.client_id,
            user_id=current_user.id,
            type_id=form.event_type.data,
            additional_information=form.additional_information.data
        )
        db.session.add(new_event)
        db.session.commit()
        
        if form.secondary_contact1.data and form.contact_person1.data:
            contact = ContactDetails(
                mobile_number=form.secondary_contact1.data,
                contact_name=form.contact_person1.data
            )
            db.session.add(contact)
            db.session.commit()
            
            alt_contact = BookingContacts(
                phone_id=contact.phone_id,
                booking_id=new_event.booking_id
            )
            db.session.add(alt_contact)
            db.session.commit()
        
        if form.secondary_contact2.data and form.contact_person2.data:
            contact = ContactDetails(
                mobile_number=form.secondary_contact2.data,
                contact_name=form.contact_person2.data
            )
            db.session.add(contact)
            db.session.commit()
            
            alt_contact = BookingContacts(
                phone_id=contact.phone_id,
                booking_id=new_event.booking_id
            )
            db.session.add(alt_contact)
            db.session.commit()
        
        return redirect(url_for('phototainment.view_booking', booking_id=new_event.booking_id))
    return render_template('add_event.html', form=form)


@custom_bp.route('/delete-event/<booking_id>')
@login_required
@admin
def delete_event(booking_id):
    event = db.session.query(Event).filter_by(booking_id=booking_id).first()
    client = event.client
    venue = event.venue
    contact = db.session.query(BookingContacts).filter_by(booking_id=booking_id).first()
    comments = db.session.query(Comment).filter_by(booking_id=booking_id).all()
    
    if comments:
        print("true")
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
    if contact:
        phone = contact.phone_numbers
        db.session.delete(contact)
        db.session.delete(phone)
        db.session.commit()
    db.session.delete(event)
    db.session.delete(client)
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
                              Client.primary_contact, ).select_from(Event, Client).join(Client)
    
    if form.search.data != "":
        if form.is_submitted():
            if form.search.data != "":
                if form.search_fname.data:
                    search_by = "client_first_name"
                    events = events.filter(Client.__table__.c[search_by].like(search_for))
                elif form.search_lname.data:
                    search_by = "client_last_name"
                    events = events.filter(Client.__table__.c[search_by].like(search_for))
                elif form.search_email.data:
                    search_by = "client_email"
                    events = events.filter(Client.__table__.c[search_by].like(search_for))
                elif form.search_contact.data:
                    search_by = "primary_contact"
                    events = events.filter(Client.__table__.c[search_by].like(search_for))
                elif form.search_evname.data:
                    search_by = "event_name"
                    events = events.filter(Event.__table__.c[search_by].like(search_for))
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
    alt_contacts = db.session.query(BookingContacts).filter_by(booking_id=booking_id).all()
    contacts = {contact.phone_numbers.contact_name: contact.phone_numbers.mobile_number for contact in alt_contacts}
    status_form = ChangeStatus()
    comment_form = CommentForm()
    venue = ""
    if event.venue:
        venue = event.venue
    
    return render_template('event-view.html',
                           event=event,
                           contacts=contacts,
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
        print("yes")
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


@custom_bp.route('/upcoming-events', )
@login_required
@employee
def upcoming_events():
    events = db.session.query(Event, Client.client_first_name, Client.client_last_name, Client.client_email,
                              Client.primary_contact, ).select_from(Event, Client).join(Client)
    filtered_event = [event for event in events if event[0].event_date - datetime.now() < timedelta(days=30) and event[
        0].event_date - datetime.now() > timedelta(days=0, minutes=0, seconds=0)]
    return render_template('upcoming-events.html', filtered_events=filtered_event)


@custom_bp.route('/edit-event/<event_id>', methods=["GET", "POST"])
@login_required
@employee
def edit_event(event_id):
    current_event = db.session.query(Event).filter_by(booking_id=event_id).first()
    print(current_event.client_fname)
    edit_form = EventForm()
    edit_form.first_name.data = current_event.client_fname
    return render_template('edit-event.html', form=edit_form)
