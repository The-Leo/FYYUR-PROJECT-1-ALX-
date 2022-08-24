#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------# 
from flask_sqlalchemy import SQLAlchemy


# TODO:DONE connect to a local postgresql database - my db name is fyyurapp

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(120))
# TODO:DONE implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=False)
    website_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")
    # shows = db.relationship('Show', backref='Venue', lazy=True)
  
def __repr__(self):
    return f'<Venue ID: {self.id} name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, genres: {self.genres}, {self.seeking_talent}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
 # TODO:DONE implement any missing fields, as a database migration using Flask-Migrate 
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), nullable=False)
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")

    # shows = db.relationship('Show', backref='Artist', lazy=True)

def __repr__(self):
    return f'<Artist ID: {self.id} name: {self.name}, city: {self.city}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}>'


# TODO:DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable= False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable= False)
    start_time = db.Column(db.DateTime, nullable= False) 
    

def __repr__(self):
        return f'<Show ID: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}>'