#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    areas = Venue.get_venues_per_city()
    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        'count': len(venues),
        'data': [
            {
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': venue.get_num_upcoming_shows()
            } for venue in venues
        ]
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=venue.get_venue_with_shows_details())


#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = Venue(
            name=request.form.get('name', default=''),
            city=request.form.get('city'),
            state=request.form.get('state'),
            address=request.form.get('address', default=''),
            phone=request.form.get('phone', default=''),
            image_link=request.form.get('image_link', default=''),
            facebook_link=request.form.get('facebook_link', default='')
        )

        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        flash(
          'An error occurred. Venue ' 
          + request.form['name'] 
          + ' could not be listed.'
        )
    finally:
        db.session.close()
    if not error:
        redirect(url_for('venues'))
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash(
            'The venue with id '
            + venue_id
            + ' was successfully deleted.'
        )
    except:
        db.session.rollback()
        flash(
          'An error occurred. Venue ' 
          + request.form['name'] 
          + ' could not be deleted.'
        )
    finally:
        db.session.close()
    return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = [{'id': artist.id, 'name': artist.name} for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        'count': len(artists),
        'data': [
            {
                'id': artist.id,
                'name': artist.name,
                'num_upcoming_shows': artist.get_num_upcoming_shows()
            } for artist in artists
        ]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=artist.get_artist_with_shows_details())


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    artist.genres = artist.genres.split(',')
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.update_artist_in_db(request.form)
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        flash(
            'An error occurred. Artist '
            + request.form['name']
            + ' could not be updated.'
        )
    finally:
        db.session.close()
    if not error:
        redirect(url_for('artists'))
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.update_venue_in_db(request.form)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        flash(
            'An error occurred. Venue '
            + request.form['name']
            + ' could not be updated.'
        )
    finally:
        db.session.close()
    if not error:
        redirect(url_for('venues'))
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        print(request.form.get('genres', default=''))
        artist = Artist(
            name=request.form.get('name', default=''),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone', default=''),
            image_link=request.form.get('image_link', default=''),
            facebook_link=request.form.get('facebook_link', default=''),
            genres=request.form.get('genres', default='')
        )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + artist.name + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        flash(
            'An error occurred. Artist '
            + request.form['name']
            + ' could not be listed.'
        )
    finally:
        db.session.close()
    if not error:
        redirect(url_for('artists'))
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    return render_template('pages/shows.html', shows=Show.get_shows_with_venue_details())


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        show = Show(
            artist_id=request.form.get('artist_id'),
            venue_id=request.form.get('venue_id'),
            start_time=request.form.get('start_time')
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback()
        flash(
            'An error occurred. Show could not be listed.'
        )
    finally:
        db.session.close()
    if not error:
        redirect(url_for('shows'))
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
