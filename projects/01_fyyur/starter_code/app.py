#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import datetime as dt
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_genres = db.Table('venue_ganres', 
      db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key = True),
      db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key = True)
)

artist_genres = db.Table('artist_ganres', 
      db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key = True),
      db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key = True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False, unique = True)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120),  unique = True)
    genres = db.relationship('Genre', secondary=venue_genres, 
                             backref = db.backref('venues', lazy = True))
    image_link = db.Column(db.String(500), unique = True)
    facebook_link = db.Column(db.String(120), unique = True)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    created = db.Column(db.DateTime)
    shows = db.relationship('Show', back_populates='venue', cascade='delete')
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False, unique = True)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), unique = True)
    genres = db.relationship('Genre', secondary=artist_genres, 
                             backref = db.backref('artists', lazy = True))
    image_link = db.Column(db.String(500), unique = True)
    facebook_link = db.Column(db.String(120), unique = True)
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    created = db.Column(db.DateTime)
    shows = db.relationship('Show', back_populates='artist', cascade='delete')
    

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    start_time = db.Column(db.DateTime, nullable = False)
    venue = db.relationship(Venue, back_populates='shows')
    artist = db.relationship(Artist, back_populates='shows')

class Genre(db.Model):
  __tablename__ = 'Genre'

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(120), nullable = False)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Utils
#----------------------------------------------------------------------------#

def populate_model(model, data):
    model.name = data['name']
    model.city = data['city']
    model.state = data['state']
    if len(data['phone']) > 0:
      model.phone = data['phone']
    for genre_name in data.getlist('genres'):
      genre = Genre.query.filter(Genre.name == genre_name).first()
      if genre is None:
        genre = Genre(name=genre_name)
      model.genres.append(genre)  
    if len(data['facebook_link']) > 0:
      model.facebook_link = data['facebook_link']
    if len(data['image_link']) > 0:
      model.image_link = data['image_link']
    if len(request.form['website']) > 0:
      model.website = data['website']
    model.seeking_description = data['seeking_description']
    model.created = dt.datetime.now()

def edit_model(model, data):
    model.name = data['name']
    model.city = data['city']
    model.state = data['state']
    if len(data['phone']) > 0:
      model.phone = data['phone']
    else:
      model.phone = None
    for genre_name in data.getlist('genres'):
      genre = Genre.query.filter(Genre.name == genre_name).first()
      if genre is None:
        genre = Genre(name=genre_name)
      model.genres.append(genre)  
    if len(data['facebook_link']) > 0:
      model.facebook_link = data['facebook_link']
    else:
      model.facebook_link = None
    if len(data['image_link']) > 0:
      model.image_link = data['image_link']
    else:
      model.image_link = None
    if len(request.form['website']) > 0:
      model.website = data['website']
    else:
      model.website = None
    model.seeking_description = data['seeking_description']

  


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.order_by(Artist.created.desc()).limit(10).all()
  venues = Venue.query.order_by(Venue.created.desc()).limit(10).all()
  return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  """
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }] 
  """
  cities = db.session.query(Venue.city, Venue.state).distinct()
  data = []
  for city, state in cities:
    city_data = {'city' : city, 'state' : state, 'venues' : []}

    for venue in Venue.query.filter(Venue.city==city, Venue.state==state).all():
      venue_data ={'id' : venue.id, 'name' : venue.name}
      shows = venue.shows
      upcoming_shows = [show for show in shows if show.start_time > dt.datetime.now()]
      venue_data['num_upcoming_shows'] = len(upcoming_shows)
      city_data['venues'].append(venue_data)

    data.append(city_data)
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  """
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
    }
    """
  search_term = request.form['search_term']
  city = request.form['search_by_city']
  state = request.form['search_by_state']

  results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  if len(city)>0:
     results = results.filter(Venue.city == city)
  if len(state)>0:
     results = results.filter(Venue.state == state)
  results = results.all()
  response = {'count' : len(results), 'data' : []}
  for venue in results:
    venue_data = {'id' : venue.id, 'name' : venue.name}
    upcoming_shows = [show for show in venue.shows if show.start_time > dt.datetime.now()]
    venue_data['num_upcoming_shows'] = len(upcoming_shows)
    response['data'].append(venue_data)
  
  return render_template('pages/search_venues.html', results=response, 
                search_term=f'{search_term} {city} {state}'.strip())

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  """ data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  } 
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  """
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": [genre.name for genre in venue.genres],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  data['upcoming_shows'] = []
  data['past_shows'] = []
  for show in venue.shows:
    show_data = {}
    show_data['artist_id'] = show.artist_id
    show_data['artist_name'] = show.artist.name
    show_data['start_time'] = str(show.start_time)
    show_data['artist_image_link'] = show.artist.image_link
    if(show.start_time >= dt.datetime.now()):
      data['upcoming_shows'].append(show_data)
    else:
      data['past_shows'].append(show_data)

  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  data['past_shows_count'] = len(data['past_shows'])
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  form.validate_on_submit()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    print(request.form)
    venue = Venue()
    populate_model(venue, request.form)
    venue.address = request.form['address']

    venue.seeking_talent = ('seeking_talent' in request.form.keys() and (request.form['seeking_talent'] == 'y' or request.form['seeking_talent'] == 'on'))

    
    
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  finally:
    db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue_id + ' successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  """ data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }] """
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({'id': artist.id, 'name': artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  """
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  """
 
  search_term = request.form['search_term']
  city = request.form['search_by_city']
  state = request.form['search_by_state']


  results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  if len(city)>0:
     results = results.filter(Artist.city == city)
  if len(state)>0:
     results = results.filter(Artist.state == state)
  results = results.all()

  response = {'count' : len(results), 'data' : []}

  for artist in results:
    artist_data = {'id' : artist.id, 'name' : artist.name}
    upcoming_shows = [show for show in artist.shows if show.start_time > dt.datetime.now()]
    artist_data['num_upcoming_shows'] = len(upcoming_shows)
    response['data'].append(artist_data)

  return render_template('pages/search_artists.html', results=response, 
                search_term=f'{search_term} {city} {state}'.strip())

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  """ data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  } 
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  """
  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": [genre.name for genre in artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":  artist.seeking_description,
    "image_link": artist.image_link
  }
  data['upcoming_shows'] = []
  data['past_shows'] = []
  for show in artist.shows:
    show_data = {}
    show_data['venue_id'] = show.venue_id
    show_data['venue_name'] = show.venue.name
    show_data['start_time'] = str(show.start_time)
    show_data['venue_image_link'] = show.venue.image_link
    if(show.start_time >= dt.datetime.now()):
      data['upcoming_shows'].append(show_data)
    else:
      data['past_shows'].append(show_data)

  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  data['past_shows_count'] = len(data['past_shows'])
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  """
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=f"ormat&fit=crop&w=300&q=80
  }
  """
  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": [genre.name for genre in artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone or "",
    "website": artist.website or "",
    "facebook_link": artist.facebook_link or "",
    "seeking_venue": artist.seeking_venue,
    "seeking_description":  artist.seeking_description,
    "image_link": artist.image_link or ""
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    edit_model(artist, request.form)
    artist.seeking_venue = ('seeking_venue' in request.form.keys() and (request.form['seeking_venue'] == 'y' or request.form['seeking_venue'] == 'on'))
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  """
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  """
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": [genre.name for genre in venue.genres],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone or "",
    "website": venue.website or "",
    "facebook_link": venue.facebook_link or "",
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link or "",
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    edit_model(venue, request.form)
    venue.address = request.form['address']
    venue.seeking_talent = ('seeking_talent' in request.form.keys() and (request.form['seeking_talent'] == 'y' or request.form['seeking_talent'] == 'on'))
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
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
  try:
    artist = Artist()
    populate_model(artist, request.form)
    artist.seeking_venue = ('seeking_venue' in request.form.keys() and request.form['seeking_venue'] == 'y')

    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  finally:
    db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  """
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  """
  data =[]
  for show in Show.query.filter(Show.start_time >= dt.datetime.now()):
    show_data ={
    'venue_id' : show.venue_id, 
    'artist_id' : show.artist_id, 
    'start_time' : str(show.start_time),
    'artist_name': show.artist.name,
    'venue_name': show.venue.name,
    'artist_image_link': show.artist.image_link
    }
    data.append(show_data)

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
  try:
    show = Show()
    show.venue_id = request.form['venue_id']
    show.artist_id = request.form['artist_id']
    show.start_time = request.form['start_time'] 
    db.session.add(show)
    db.session.commit()  
    # on successful db insert, flash success
    flash('Show was successfully listed!') 
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
