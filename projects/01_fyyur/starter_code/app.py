#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    genres = db.relationship('Genre_Venue', backref='venue_genre')
    shows = db.relationship('Show', backref='show_venue')

    def __repr__(self):
      return f'''<Venue {self.id},
      name: {self.name}, city: {self.city}, state: {self.state},
      address: {self.address}, phone: {self.phone}, image_link: {self.image_link},
      facebook_link: {self.facebook_link}, website_link: {self.website_link}, 
      seeking_talent: {self.seeking_talent}>'''


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref='show_artist', lazy=True)
    genres = db.relationship('Genre_Artist', backref='artist_genre')

    def __repr__(self):
      return f'''<Artist {self.id}, name: {self.name}, city: {self.city}, 
      state: {self.state}, phone: {self.phone}, image_link: {self.image_link}, 
      facebook_link: {self.facebook_link}, website_link: {self.website_link}, 
      seeking_venue: {self.seeking_venue}>'''


class Show(db.Model):
  __tablename__ = "shows"

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.String(120))

  def __repr__(self):
    return f'''<Show {self.id}: venue_id: {self.venue_id}, artist_id: {self.artist_id}, start_time: {self.start_time}>'''


class Genre(db.Model):
  __tablename__ = "genres"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  genres_venues = db.relationship('Genre_Venue', backref='genre_venue')
  genres_artists = db.relationship('Genre_Artist', backref='genre_artist')


  def __repr__(self):
    return f'''<Genre {self.id}: genre_id: {self.id}, genre_name: {self.name}>'''


class Genre_Venue(db.Model):
  __tablename__ = "genres_venues"

  id = db.Column(db.Integer, primary_key=True)
  genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

  def __repr__(self):
    return f'''<Row_ID {self.id}: genre_id: {self.genre_id}, venue_id: {self.venue_id}>'''


class Genre_Artist(db.Model):
  __tablename__ = "genres_artists"

  id = db.Column(db.Integer, primary_key=True)
  genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

  def __repr__(self):
    return f'''<Row_ID {self.id}: genre_id: {self.genre_id}, artist_id: {self.artist_id}>'''


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
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  cities_states=Venue.query.with_entities(Venue.city,Venue.state).distinct()
  venues=Venue.query.all()
  return render_template('pages/venues.html', venues=venues, cities_states=cities_states);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  venue_genres_list = Genre_Venue.query.filter_by(venue_id=venue.id)
  genres = []

  for genre in venue_genres_list:
    genres.append(Genre.query.get(genre.genre_id).name)

  #get all shows of current venue
  all_shows_list = Show.query.filter_by(venue_id=venue_id).all()

  # format current datetime
  now = str(datetime.now())
  now = format_datetime(now)

  upcoming_shows = []
  upcoming_shows_count = 0

  past_shows = []
  past_shows_count = 0

  for show in all_shows_list:
    if show.start_time > now:
      upcoming_shows.append(show)
      upcoming_shows_count += 1
    else:
      past_shows.append(show)
      past_shows_count += 1

  return render_template('pages/show_venue.html', venue=venue, genres=genres, upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count,
  past_shows=past_shows, past_shows_count=past_shows_count)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  new_venue = Venue()
  new_venue.name = request.get_json()['name']
  new_venue.state = request.get_json()['state']
  new_venue.city = request.get_json()['city']
  new_venue.address = request.get_json()['address']
  new_venue.phone = request.get_json()['phone']
  new_venue.facebook_link = request.get_json()['facebook_link']

  # insert venue except genre
  try:
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
  finally:
    db.session.close()

  # insert genre
  genre_venue = request.get_json()['genres']

  available_genres = Genre.query.all()
  new_venue = Venue.query.order_by(Venue.id.desc()).first()

  genreMatch = False

  for genre in available_genres:
    if genre.name == genre_venue:
      genreMatch = True
      new_genre_venue = Genre_Venue(genre_id=genre.id, venue_id=new_venue.id)
      break
  
  if not genreMatch:
    new_genre = Genre(name=genre_venue)
    db.session.add(new_genre)
    db.session.commit()

    available_genres = Genre.query.all()
    for genre in available_genres:
      if genre.name == genre_venue:
        genreMatch = True
        new_genre_venue = Genre_Venue(genre_id=genre.id, venue_id=new_venue.id)
        break

  try:
    db.session.add(new_genre_venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):  
  try:
    # delete venue's shows
    Show.query.filter_by(venue_id=venue_id).delete()
    # delete genres_venues
    Genre_Venue.query.filter_by(venue_id=venue_id).delete()
    # delete venues
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists=Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  genres_artists = Genre_Artist.query.filter_by(artist_id=artist_id).all()
  genres = []

  for genre in genres_artists:
    genres.append(Genre.query.get(genre.genre_id).name)

  #get all shows of current venue
  all_shows_list = Show.query.filter_by(artist_id=artist_id).all()

  # format current datetime
  now = str(datetime.now())
  now = format_datetime(now)

  upcoming_shows = []
  upcoming_shows_count = 0

  past_shows = []
  past_shows_count = 0

  for show in all_shows_list:
    if show.start_time > now:
      upcoming_shows.append(show)
      upcoming_shows_count += 1
    else:
      past_shows.append(show)
      past_shows_count += 1

  return render_template('pages/show_artist.html', artist=artist, genres=genres, upcoming_shows=upcoming_shows,
  upcoming_shows_count=upcoming_shows_count, past_shows=past_shows, past_shows_count=past_shows_count)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
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
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
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
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  new_artist = Artist()
  new_artist.name = request.get_json()['name']
  new_artist.state = request.get_json()['state']
  new_artist.city = request.get_json()['city']
  new_artist.phone = request.get_json()['phone']
  new_artist.facebook_link = request.get_json()['facebook_link']

  try:
    db.session.add(new_artist)
    db.session.commit()
    print('success')
    flash('Artist ' + new_artist.name + ' was successfully listed!')
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # insert genre
  genre_artist = request.get_json()['genres']

  available_genres = Genre.query.all()
  new_artist = Artist.query.order_by(Artist.id.desc()).first()

  genreMatch = False

  for genre in available_genres:
    if genre.name == genre_artist:
      genreMatch = True
      new_genre_artist = Genre_Artist(genre_id=genre.id, artist_id=new_artist.id)
      break
  
  if not genreMatch:
    new_genre = Genre(name=genre_artist)
    db.session.add(new_genre)
    db.session.commit()

    available_genres = Genre.query.all()
    for genre in available_genres:
      if genre.name == genre_artist:
        genreMatch = True
        new_genre_artist = Genre_Artist(genre_id=genre.id, artist_id=new_artist.id)
        break

  try:
    db.session.add(new_genre_artist)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    tmp = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time
    }
    data.append(tmp)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  new_show = Show()
  new_show.artist_id = request.get_json()['artist_id']
  new_show.venue_id = request.get_json()['venue_id']
  new_show.start_time = request.get_json()['start_time']

  try:
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
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
