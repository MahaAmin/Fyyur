#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import ( 
  Flask, render_template, request, Response, 
  flash, redirect, url_for, jsonify
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app,db)
db.init_app(app)

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
  search_term = request.form.get('search_term')
  venues = Venue.query.all()

  response_data = []
  for venue in venues:
    if search_term.lower() in venue.name.lower():
      response_data.append(venue)

  results_count = len(response_data)
  
  return render_template('pages/search_venues.html', results=response_data, results_count=results_count, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  venue_genres_list = Genre_Venue.query.filter_by(venue_id=venue.id)
  genres = []

  for genre in venue_genres_list:
    genres.append(Genre.query.get(genre.genre_id).name)

  # format current datetime
  now = str(datetime.now())
  now = format_datetime(now)

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
    Show.venue_id == venue_id,
    Show.artist_id == Artist.id,
    Show.start_time > now
  ).all()

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
    Show.venue_id == venue_id,
    Show.artist_id == Artist.id,
    Show.start_time < now
  ).all()

  data = {
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'website_link': venue.website_link,
    'seeking_talent': venue.seeking_talent,
    'past_shows': [{
        'artist_id': artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
    } for artist, show in past_shows],
    'upcoming_shows': [{
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time
    } for artist, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }



  return render_template('pages/show_venue.html', venue=data, genres=genres)

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
  new_venue.website_link = request.get_json()['website_link']


  form = VenueForm(request.form)

  # insert venue except genre
  try:
    form.populate_obj(new_venue)
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  except ValueError as e:
    print(e)
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
  search_term = request.form.get('search_term')
  artists = Artist.query.all()

  response_data = []
  for artist in artists:
    if search_term.lower() in artist.name.lower():
      response_data.append(artist)

  results_count = len(response_data)
  return render_template('pages/search_artists.html', results=response_data, search_term=search_term, results_count=results_count)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  genres_artists = Genre_Artist.query.filter_by(artist_id=artist_id).all()
  genres = []

  for genre in genres_artists:
    genres.append(Genre.query.get(genre.genre_id).name)

  # format current datetime
  now = str(datetime.now())
  now = format_datetime(now)

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
    Show.venue_id == Venue.id,
    Show.artist_id == artist_id,
    Show.start_time > now
  ).all()

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
    Show.venue_id == Venue.id,
    Show.artist_id == artist_id,
    Show.start_time < now
  ).all()

  data = {
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'website_link': artist.website_link,
    'past_shows': [{
        'artist_id': artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
    } for artist, show in past_shows],
    'upcoming_shows': [{
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time
    } for artist, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data, genres=genres)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artist.name = request.get_json()['name']
  artist.city = request.get_json()['city']
  artist.state = request.get_json()['state']
  artist.phone = request.get_json()['phone']
  artist.facebook_link = request.get_json()['facebook_link']
  artist.website_link = request.get_json()['website_link']

  form = ArtistForm(request.form)
  try:
    form.populate_obj(artist)
    print(artist)
    db.session.add(artist)
    db.session.commit()
    print('successssssss')
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  venue.name = request.get_json()['name']
  venue.state = request.get_json()['state']
  venue.city = request.get_json()['city']
  venue.address = request.get_json()['address']
  venue.phone = request.get_json()['phone']
  venue.facebook_link = request.get_json()['facebook_link']
  venue.website_link = request.get_json()['website_link']

  form = VenueForm(request.form)

  try:
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
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
  new_artist = Artist()
  new_artist.name = request.get_json()['name']
  new_artist.state = request.get_json()['state']
  new_artist.city = request.get_json()['city']
  new_artist.phone = request.get_json()['phone']
  new_artist.facebook_link = request.get_json()['facebook_link']
  new_artist.website_link = request.get_json()['website_link']

  form = ArtistForm(request.form)
  try:
    form.populate_obj(new_artist)
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
