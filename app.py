#----------------------------------------------------------------------------#
# Imports 
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import dateutil
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from sqlalchemy import func
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy import desc
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from operator import itemgetter
import sys
#----------------------------------------------------------------------------#
# App Config. 
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *

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

  new_venues = Venue.query.all()
  data = []
  cities_state = set() 
  for venue in new_venues:
    cities_state.add( (venue.city, venue.state) )

  cities_state = list(cities_state)
  cities_state.sort(key=itemgetter(1,0)) 
  now = datetime.now()
  for loc in cities_state:
    venues_list = []
    for venue in venues:
        if (venue.city == loc[0]) and (venue.state == loc[1]):

          venue_shows = Show.query.filter_by(venue_id=venue.id).all()
          num_upcoming = 0
          for show in venue_shows:
            if show.start_time > now:
              num_upcoming += 1

          venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming
                })

    data.append({
            "city": loc[0],
            "state": loc[1],
            "venues": venues_list
        })

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO:DONE implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  search_term = request.form.get('search_term', '').strip()
  search_response = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []
  now = datetime.now()
  for venue in search_response:
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming = 0
        for show in venue_shows:
            if show.start_time > now:
                num_upcoming += 1

            data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming
      })
  response = {
      "count": len(search_response),
      "data": data
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
  past_shows_count = 0
  upcoming_shows = []
  upcoming_shows_count = 0
  now = datetime.now()

  show = venue.shows
  for show in venue.shows:
    if show.start_time > now:
        upcoming_shows_count += 1
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

  data={
    "id": venue.id, 
    "name": venue.name, 
    "city": venue.city,
    "state": venue.state, 
    "address": venue.address,
    "phone": venue.phone, 
    "genres": venue.genres.split(','),
    "image_link": venue.image_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "website_link": venue.website_link,
    "past_shows": venue.past_shows, 
    "upcoming_shows": venue.upcoming_shows, 
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
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
  error = False
  form = VenueForm(request.values)

  if form.validate():
      venue = Venue(
        name = form.name.data.strip(),
        city = form.city.data.strip(),
        state = form.state.data,
        address = form.address.data.strip(),
        phone = form.phone.data,
        genres = form.genres.data,
        image_link = form.image_link.data.strip(),
        facebook_link = form.facebook_link.data.strip(),
        website_link = form.website_link.data,
        seeking_talent = True if form.seeking_talent.data == 'Yes' else False,
        seeking_description = form.seeking_description.data.strip()
      )
  if not form.validate():
    flash( 'An error occurred' )
    return redirect(url_for('create_venue_submission'))

  try: 
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error=True
    db.session.rollback()
# TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error=False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info(), encoding='utf-8')
  finally:
    db.session.close()
  if error:
    flash(f"An error occurred. Venue could not be deleted")
  if not error:
    flash(f"Venue was succesfully deleted.")

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #i want to render list of artists
  data=[]
  artists = db.session.query(Artist).order_by('id').all()
  for artist in artists:   
        data.append({
            "id":artist.id,
            "name":artist.name,
            })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #i want to search for artist using partial string search
    search_term = request.form.get('search_term', '').strip()
    search_result = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all() 
    artist_list = []
    now = datetime.now()
    for artist in search_result:
            artist_shows = Show.query.filter_by(artist_id=artist.id).all()
            num_upcoming = 0
            for show in artist_shows:
                if show.start_time > now:
                    num_upcoming += 1

            artist_list.append({
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": num_upcoming 
            })
            response = {
                "count": len(artists),
                "data": artist_list
            }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)

    if not artist:
      return render_template('error/404.html')

    if artist:

      print(artist)

    else:
        # genres needs to be a list of genre strings for the template
        genres = [ genre.name for genre in artist.genres ]
        
        past_shows = []
        past_shows_count = 0
        upcoming_shows = []
        upcoming_shows_count = 0
        now = datetime.now()
        for show in artist.shows:
            if show.start_time > now:
                upcoming_shows_count += 1
                upcoming_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
            if show.start_time < now:
                past_shows_count += 1
                past_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        data={
            "id": artist_id, 
            "name": artist.name, 
            "city": artist.city,
            "state": artist.state, 
            "address": artist.address,
            "phone": artist.phone, 
            "genres": artist.genres.split(','),
            "image_link": artist.image_link,
            "facebook_link": artist.facebook_link,
            "seeking_talent": artist.seeking_talent,
            "website_link": artist.website_link,
            "past_shows": artist.past_shows, 
            "upcoming_shows": artist.upcoming_shows, 
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
          }
    return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    #i want to retrieve artist data to edit the form
  form = ArtistForm()
  data = Artist.query.get(artist_id)
  artist={
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(", "),
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website_link": data.website,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.seeking_venue,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
  }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    data = Artist.query.get(artist_id)
    data.name = request.form.get('name')
    data.genres = ', '.join(request.form.getlist('genres'))
    data.city = request.form.get('city')
    data.state = request.form.get('state')
    data.phone = request.form.get('phone')
    data.facebook_link = request.form.get('facebook_link')
    data.image_link = request.form.get('image_link')
    data.website = request.form.get('website_link')
    data.seeking_venue = True if request.form.get('seeking_venue')!=None else False
    data.seeking_description = request.form.get('seeking_description')
    db.session.add(data)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info(), encoding='utf-8')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data = Venue.query.get(venue_id)
  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(", "),
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
  }
   # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
   # TODO: take values from the form submitted, and update existing
   # venue record with ID <venue_id> using the new attributes
  try:
      data = Venue.query.get(venue_id)

      data.name = request.form.get('name')
      data.genres = ', '.join(request.form.getlist('genres'))
      data.address = request.form.get('address')
      data.city = request.form.get('city')
      data.state = request.form.get('state')
      data.phone = request.form.get('phone')
      data.facebook_link = request.form.get('facebook_link')
      data.image_link = request.form.get('image_link')
      data.website = request.form.get('website_link')
      data.seeking_talent = True if request.form.get('seeking_talent')!= None else False
      data.seeking_description = request.form.get('seeking_description')
      db.session.add(data)
      db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info(), encoding='utf-8')
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
  error = False
  form = ArtistForm(request.values)
  if form.validate():
    try:
      artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
        )
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info(), encoding = 'utf-8')
    finally:
      db.session.close()
  else:
    print("error")
    error = True
  if not error:
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    abort(500)
  # TODO: on unsuccessful db insert, flash an error instead.

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": format_datetime(str(show.start_time))
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
  error=False
  try:
    data = Show()
    data.venue_id = request.form.get('venue_id')
    data.artist_id = request.form.get('artist_id')
    data.start_time = request.form.get('start_time')
    db.session.add(data)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info(), encoding='utf-8')
  finally:
    db.session.close()
    # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!')
  else:
# TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    abort(500)

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
