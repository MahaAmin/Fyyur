from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy(app)

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
