#################### Imports #####################
from app import app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash
from flask_login import LoginManager

#################### Login Manager #####################
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#################### Initialize Database #####################
db = SQLAlchemy(app)


#################### Role Model #####################
class Role(db.Model):
    __tablename__ = "user_role"
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    role_description = db.Column(db.String(50))
    user = relationship("User", back_populates="role")


#################### User Model #####################
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.String(50), nullable=False)
    
    role_id = db.Column(db.Integer, db.ForeignKey("user_role.role_id"), nullable=False)
    role = relationship("Role", back_populates="user")
    
    comment = relationship("Comment", back_populates="user")
    events = relationship("Event", back_populates="user")


#################### Type Model #####################
class EventType(db.Model):
    __tablename__ = "event_type"
    type_id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), unique=True, nullable=False)
    events = relationship("Event", back_populates="type")


#################### Status Model #####################
class EventStatus(db.Model):
    __tablename__ = "event_status"
    status_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), unique=True, nullable=False)
    events = relationship("Event", back_populates="status")


#################### Client Model #####################
class Client(db.Model):
    __tablename__ = "client"
    client_id = db.Column(db.Integer, primary_key=True)
    client_first_name = db.Column(db.String(50), nullable=False)
    client_last_name = db.Column(db.String(50), nullable=False)
    client_email = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(50), nullable=False)
    primary_contact = db.Column(db.String(10), nullable=False)
    events = relationship("Event", back_populates="client")


#################### Contact Model #####################
class ContactDetails(db.Model):
    __tablename__ = "phone_details"
    phone_id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(50), nullable=False)
    mobile_number = db.Column(db.String(50), nullable=False)
    
    contacts = relationship("BookingContacts", back_populates="phone_numbers")


class BookingContacts(db.Model):
    __tablename__ = "contacts"
    contact_id = db.Column(db.Integer, primary_key=True)
    
    phone_id = db.Column(db.Integer, db.ForeignKey("phone_details.phone_id"), nullable=False)
    phone_numbers = relationship("ContactDetails", back_populates="contacts")
    
    booking_id = db.Column(db.Integer, db.ForeignKey("event_booking.booking_id"), nullable=False)
    booking = relationship("Event", back_populates="contacts")


#################### Venue Model #####################
class EventVenue(db.Model):
    __tablename__ = "event_venue"
    venue_id = db.Column(db.Integer, primary_key=True)
    street_address = db.Column(db.String(50), nullable=False)
    suburb = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(3), nullable=False)
    post_code = db.Column(db.Integer, nullable=False)
    
    booking = relationship("Event", back_populates="venue")


#################### Booking Model #####################
class Event(db.Model):
    __tablename__ = "event_booking"
    booking_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(50), nullable=True)
    lead_date = db.Column(db.DateTime, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Time, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    additional_information = db.Column(db.String(200), nullable=True)
    
    contacts = relationship("BookingContacts", back_populates="booking")
    comment = relationship("Comment", back_populates="booking")
    
    venue_id = db.Column(db.Integer, db.ForeignKey("event_venue.venue_id"), nullable=True)
    venue = relationship("EventVenue", back_populates="booking")
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="events")
    
    type_id = db.Column(db.Integer, db.ForeignKey("event_type.type_id"), nullable=False)
    type = relationship("EventType", back_populates="events")
    
    status_id = db.Column(db.Integer, db.ForeignKey("event_status.status_id"), nullable=False)
    status = relationship("EventStatus", back_populates="events")
    
    client_id = db.Column(db.Integer, db.ForeignKey("client.client_id"), nullable=False)
    client = relationship("Client", back_populates="events")


#################### Comment Model #####################
class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_action = db.Column(db.String(50), nullable=True)
    comment_reason = db.Column(db.String(50), nullable=True)
    
    booking_id = db.Column(db.Integer, db.ForeignKey("event_booking.booking_id"), nullable=False)
    booking = relationship("Event", back_populates="comment")
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="comment")


#################### Create Tables #####################
db.create_all()

#################### Insert to role table #####################
if not Role.query.all():
    admin, employee = (
        Role(
            role_name="Admin",
            role_description="Role to create, update, and delete records"
        ),
        Role(
            role_name="Employee",
            role_description="Role can create, delete events"
        ),
    )
    db.session.add(admin)
    db.session.add(employee)
    db.session.commit()

#################### Insert to User table #####################
if not db.session.query(User).filter_by(id=1).first():
    admin_user = User(
        username="Admin".lower(),
        role=db.session.query(Role).filter_by(role_name="Admin").first(),
        password=generate_password_hash("123456", method='pbkdf2:sha256', salt_length=8),
        job_description="Administrator/Owner"
    )
    db.session.add(admin_user)
    db.session.commit()

#################### Insert to Type table #####################
if not EventType.query.all():
    w_event, b_event, o_event, e_event = (
        EventType(
            event_type="Wedding"
        ),
        EventType(
            event_type="Birthday"
        ),
        EventType(
            event_type="Other"
        ),
        EventType(
            event_type="E-type"
        )
    )
    db.session.add(w_event)
    db.session.add(b_event)
    db.session.add(o_event)
    db.session.add(e_event)
    db.session.commit()

#################### Insert to Status table #####################
if not db.session.query(EventStatus).all():
    processing, approved, on_going, completed, canceled = (
        EventStatus(status="Waiting Approval"),
        EventStatus(status="Processing"),
        EventStatus(status="On Going"),
        EventStatus(status="Completed"),
        EventStatus(status="Canceled"),
    )
    db.session.add(processing)
    db.session.add(approved)
    db.session.add(on_going)
    db.session.add(completed)
    db.session.add(canceled)
    db.session.commit()
