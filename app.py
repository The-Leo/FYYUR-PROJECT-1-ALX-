#----------------------------------------------------------------------------#
# Imports 
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from sqlalchemy import func
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config. i connected the app to an instance of Migrate
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO:DONE connect to a local postgresql database - my db name is fyyurapp
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc@localhost:5432/fyyurapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
# TODO:DONE implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    website_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

def __repr__(self):
    return f'<Venue ID: {self.id} name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, genres: {self.genres}, {self.seeking_talent}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
 # TODO:DONE implement any missing fields, as a database migration using Flask-Migrate 
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String())

def __repr__(self):
    return f'<Artist ID: {self.id} name: {self.name}, city: {self.city}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}>'


# TODO:DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable= False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable= False)
    start_time = db.Column(db.DateTime, nullable= False)
    upcoming = db.Column(db.Boolean, nullable=False, default=True)
    

def __repr__(self):
        return f'<Show ID: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO:DONE replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  venues = Venue.query.all()
  data = []
  city_and_state = set() 
  for venue in venues:
    city_and_state.add( (venue.city, venue.state) )
  for place in city_and_state:
    list_of_venues = []
  
  for venue in venues:
    if( venue.city == place[0] and venue.state == place[1]):
      list_of_venues.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': 0
      })

    data.append({
      'city':place[0],
      'state': place[1],
      'venues': list_of_venues
      }
    )
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO:DONE implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  search_term = request.form.get('search_term', "")
  search_result = db.session.query(Venue).filter(Venue.name.ilike(f"%{search_term}%")).all()
  data = []

  for result in search_result:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==result.id).filter(Show.start_time > datetime.now()).all())
    })

  response={
    "count": len(search_result),
    "data": data,
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO:DONE replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)

  if not venue:
    return render_template('error/404.html')
    
  past_shows = []
  upcoming_shows = []
  shows = venue.shows
  for show in shows:
    show_info ={ "artist_id": show.artist_id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link,"start_time": str(show.start_time)
    }

    if(show.upcoming):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)

  data={
    "id": venue.id, "name": venue.name, "genres": venue.genres.split(','),"address": venue.address,
    "city": venue.city,"state": venue.state, "phone": venue.phone, "facebook_link": venue.facebook_link,"seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link, "past_shows": past_shows, "upcoming_shows": upcoming_shows, "past_shows_count": len(past_shows),"upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO:DONE insert form data as a new Venue record in the db, instead
  # TODO:DONE modify data to be the data object returned from db insertion
  new_venue = Venue()
  new_venue.name = request.form['name']
  new_venue.city = request.form['city']
  new_venue.state = request.form['state']
  new_venue.address = request.form['address']
  new_venue.phone = request.form['phone']
  new_venue.facebook_link = request.form['facebook_link']
  new_venue.genres = request.form['genres']
  new_venue.image_link = request.form['image_link']

  # on successful db insert, flash success
  try:
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue_id = request.form.get('venue_id')
  deleted_venue = Venue.query.get(venue_id)
  venueName = deleted_venue.name
  try:
    db.session.delete(deleted_venue)
    db.session.commit()
    flash('Venue ' + venueName + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('please try again. Venue ' + venueName + ' could not be deleted.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()

  response={ "count": len(results), "data": []
  }

  for artist in results:
    response['data'].append({ "id": artist.id, "name": artist.name, "num_upcoming_shows": artist.upcoming_shows_count,
      })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)

  if not artist:
    return render_template('error/404.html')

  past_shows = []
  upcoming_shows = []
  shows = artist.shows
  for show in shows:
    show_info ={ "venue_id": show.venue_id, "venue_name": show.venue.name, "venue_image_link": show.venue.image_link,"start_time": str(show.start_time)
    }

    if(show.upcoming):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)

  data={
    "id": artist.id, "name": artist.name, "genres": artist.genres.split(','),"address": artist.address,
    "city": artist.city,"state": artist.state, "phone": artist.phone, "facebook_link": artist.facebook_link,"seeking_talent": artist.seeking_talent,
    "image_link": artist.image_link, "past_shows": past_shows, "upcoming_shows": upcoming_shows, "past_shows_count": len(past_shows),"upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.instagram_link.data = artist.instagram_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_talent.data = artist.seeking_talent

 

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  artist = Artist.query.get(artist_id)

  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form.getlist('genres')
  artist.image_link = request.form['image_link']
  artist.facebook_link = request.form['facebook_link']
  artist.seeking_venue = True if "seeking_venue" in request.form else False
  artist.seeking_talent = True if "seeking_talent" in request.form else False
    
  try:
    db.session.commit()
    flash('Artist was successfully updated!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist could not be changed.')
    print(sys.exc_info())
  finally:
    db.session.close() 
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.genres.data = venue.genres
    form.seeking_talent.data = venue.seeking_talent

  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
 
    error = False
    venue = Venue.query.get(venue_id)

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = request.form.getlist('genres')
    venue.seeking_talent = True if "seeking_talent" in request.form else False

    try:
      db.session.commit()
      flash('Venue was successfully changed!')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue could not be changed.')
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  new_artist = Artist()
  new_artist.name = request.form['name']
  new_artist.city = request.form['city']
  new_artist.state = request.form['state']
  new_artist.phone = request.form['phone']
  new_artist.genres = request.form['genres']
  new_artist.image_link = request.form['image_link']
  new_artist.facebook_link = request.form['facebook_link']

  try:
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
  finally:
    db.session.close
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  all_shows = db.session.query(Show).join(Artist).join(Venue).all()
  data = []
  for show in all_shows:
    data.append({
      "artist_id": show.artist_id,
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  new_show = Show()

  new_show.artist_id = request.form['artist_id']

  new_show.venue_id = request.form['venue_id']
  
  dateAndTime = request.form['start_time'].split(' ')
  
  DTList = dateAndTime[0].split('-')
  DTList += dateAndTime[1].split(':') 

  for i in range(len(DTList)):
    DTList[i] = int(DTList[i])
  new_show.start_time = datetime(DTList[0],DTList[1],DTList[2],DTList[3],DTList[4],DTList[5])
  now = datetime.now()
  new_show.upcoming = (now < new_show.start_time)
  
  try:
    db.session.add(new_show)
    # update venue and artist table
    updated_artist = Artist.query.get(new_show.artist_id)
    updated_venue = Venue.query.get(new_show.venue_id)
    if(new_show.upcoming):
      updated_artist.upcoming_shows_count += 1;
      updated_venue.upcoming_shows_count += 1;
    else:
      updated_artist.past_shows_count += 1;
      updated_venue.past_shows_count += 1;
 # on successful db insert, flash success
      db.session.commit()
      flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
