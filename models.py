from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


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

    shows = db.relationship('Show', backref='venue', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Venue id: "{self.id}", name: "{self.name}">'

    def get_num_past_shows(self):
        return len(Show.query.filter(
            Show.start_time < datetime.now(),
            Show.venue_id == self.id
        ).all())

    def get_num_upcoming_shows(self):
        return len(Show.query.filter(
            Show.start_time > datetime.now(),
            Show.venue_id == self.id
        ).all())

    def get_venue(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': self.get_num_upcoming_shows()
        }

    def get_past_shows(self):
        return [
            show.get_artist_details() for show in
            Show.query.filter(
                Show.start_time < datetime.now(),
                Show.venue_id == self.id
            )
        ]

    def get_upcoming_shows(self):
        return [
            show.get_artist_details() for show in
            Show.query.filter(
                Show.start_time > datetime.now(),
                Show.venue_id == self.id
            )
        ]

    def get_venue_with_shows_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': [
                Artist.query.get(show.artist_id).genres for show in
                Show.query.filter_by(venue_id=7).all()
            ],
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'facebook_link': self.facebook_link,
            'image_link': self.image_link,
            'past_shows': self.get_past_shows(),
            'upcoming_shows': self.get_upcoming_shows(),
            'upcoming_shows_count': self.get_num_upcoming_shows(),
            'past_shows_count': self.get_num_past_shows()
        }

    def update_venue_in_db(self, form):
        self.name = form.get('name')
        self.city = form.get('city')
        self.state = form.get('state')
        self.address = form.get('address')
        self.phone = form.get('phone')
        self.facebook_link = form.get('facebook_link')
        self.image_link = form.get('image_link')
        return self

    @staticmethod
    def get_venues_per_city():
        return [
            {
                'city': area.city,
                'state': area.state,
                'venues': [
                    venue.get_venue() for venue in Venue.query.filter(
                        Venue.city == area.city,
                        Venue.state == area.state).all()
                ]
            } for area in Venue.query.distinct('city').all()
        ]


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Artist id: "{self.id}", name: "{self.name}">'

    def get_num_upcoming_shows(self):
        return len(Show.query.filter(
            Show.start_time > datetime.now(),
            Show.artist_id == self.id
        ).all())

    def get_num_past_shows(self):
        return len(Show.query.filter(
            Show.start_time < datetime.now(),
            Show.artist_id == self.id
        ).all())

    def get_past_shows(self):
        return [
            show.get_venue_details() for show in
            Show.query.filter(
                Show.start_time < datetime.now(),
                Show.artist_id == self.id
            )
        ]

    def get_upcoming_shows(self):
        return [
            show.get_venue_details() for show in
            Show.query.filter(
                Show.start_time > datetime.now(),
                Show.artist_id == self.id
            )
        ]

    def get_artist_with_shows_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(', '),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'past_shows': self.get_past_shows(),
            'upcoming_shows': self.get_upcoming_shows(),
            'upcoming_shows_count': self.get_num_upcoming_shows(),
            'past_shows_count': self.get_num_past_shows()
        }

    def update_artist_in_db(self, form):
        self.name = form.get('name')
        self.city = form.get('city')
        self.state = form.get('state')
        self.phone = form.get('phone')
        self.genres = ', '.join(form.getlist('genres'))
        self.facebook_link = form.get('facebook_link')
        self.image_link = form.get('image_link')
        return self


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    start_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Show id: "{self.id}", artist_id: "{self.artist_id}", venue_id: "{self.venue_id}">'

    def get_artist_details(self):
        artist = Artist.query.get(self.artist_id)
        return {
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }

    def get_venue_details(self):
        venue = Venue.query.get(self.venue_id)
        return {
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }

    @staticmethod
    def get_shows_with_venue_details():
        return [
            {
                'venue_id': show.venue_id,
                'venue_name': Venue.query.get(show.venue_id).name,
                'artist_id': show.artist_id,
                'artist_name': Artist.query.get(show.artist_id).name,
                'artist_image_link': Artist.query.get(show.artist_id).image_link,
                'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            } for show in Show.query.all()
        ]
