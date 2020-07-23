# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from flask import render_template, request, flash, redirect, url_for, jsonify, abort
import logging
from logging import Formatter, FileHandler
from forms import *
import sys
from models import *
from utils import *
from sqlalchemy import text

app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    venues = Venue.query.all()
    venueCity = set()
    data = []
    for venue in venues:
        venueCity.add((venue.city, venue.state))
    for city in venueCity:
        data.append({
            "city": city[0],
            "state": city[1],
            "venues": []
        })
    for venue in venues:
        currentDate = datetime.now()
        upcoming = Show.query.filter_by(venueId=venue.id).filter(Show.start_time > currentDate).count()
        for loc in data:
            if venue.state == loc['state'] and venue.city == loc['city']:
                loc['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": upcoming
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    srch = request.form.get('search_term', '')
    searchSql = text('SELECT * FROM "Venue" WHERE name ILIKE ' + f"'%{srch}%'")
    res = db.engine.execute(searchSql)
    names = [row for row in res]
    response = {
        "count": len(names),
        "data": names
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        return abort(404)

    currentDate = datetime.now()
    upcoming_shows = Show.query.filter_by(venueId=venue.id).filter(Show.start_time > currentDate)
    past_shows = Show.query.filter_by(venueId=venue.id).filter(Show.start_time < currentDate)
    u = []
    p = []
    for n in upcoming_shows:
        data = {
            "artist_id": n.artistId,
            "artist_name": n.artist.name,
            "artist_image_link": n.artist.image_link,
            "start_time": format_datetime(str(n.start_time))
        }
        u.append(data)
    for n in past_shows:
        data = {
            "artist_id": n.artistId,
            "artist_name": n.artist.name,
            "artist_image_link": n.artist.image_link,
            "start_time": format_datetime(str(n.start_time))
        }
        p.append(data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": p,
        "upcoming_shows": u,
        "past_shows_count": len(p),
        "upcoming_shows_count": len(u)
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
    form = VenueForm()
    try:
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                      phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
                      facebook_link=form.facebook_link.data, seeking_description=form.seeking_description.data,
                      website=form.website.data, seeking_talent=form.seeking_talent.data)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
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
    artists = Artist.query.all()
    data = []
    for a in artists:
        data.append({
            "id": a.id,
            "name": a.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    sch = request.form.get('search_term', '')
    searchSql = text('SELECT * FROM "Artist" WHERE name ILIKE ' + f"'%{sch}%'")
    res = db.engine.execute(searchSql)
    names = [row for row in res]
    response = {
            "count": len(names),
            "data": names
        }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return abort(404)
    currentDate = datetime.now()
    upcoming_shows = Show.query.filter_by(artistId=artist.id).filter(Show.start_time > currentDate)
    past_shows = Show.query.filter_by(artistId=artist.id).filter(Show.start_time < currentDate)
    ud = []
    pd = []
    for u in upcoming_shows:
        data = {
            "venue_id": u.venueId,
            "venue_name": u.venue.name,
            "venue_image_link": u.venue.image_link,
            "start_time": format_datetime(str(u.start_time))
        }
        ud.append(data)
    for p in past_shows:
        data = {
            "venue_id": p.venueId,
            "venue_name": p.venue.name,
            "venue_image_link": p.venue.image_link,
            "start_time": format_datetime(str(p.start_time))
        }
        pd.append(data)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": pd,
        "upcoming_shows": ud,
        "past_shows_count": len(pd),
        "upcoming_shows_count": len(ud)
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm()
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.phone = form.phone.data
        artist.state = form.state.data
        artist.city = form.city.data
        artist.genres = form.genres.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        db.session.commit()
        flash("The Artist: " + request.form['name'] + " has been edited successfully!!")
    except:
        db.session.rollback()
        flash("The Artist: " + request.form['name'] + ' has a problem in editing')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Artist.query.get(venue_id)
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
        flash("The Venue: " + request.form['name'] + " has been edited successfully!!")
    except:
        db.session.rollback()
        flash("The Venue: " + request.form['name'] + ' has a problem in editing')
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
    form = ArtistForm()
    try:
        artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data,
                        phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
                        facebook_link=form.facebook_link.data)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    shows = Show.query.order_by(db.desc(Show.start_time))
    data = []
    for s in shows:
        data.append({
            "venue_id": s.venueId,
            "venue_name": s.venue.name,
            "artist_id": s.artistId,
            "artist_name": s.artist.name,
            "artist_image_link": s.artist.image_link,
            "start_time": format_datetime(str(s.start_time))
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    try:
        show = Show(artistId=form.artist_id.data, venueId=form.venue_id.data, start_time=form.start_time.data)
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
# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#
# Default port:
if __name__ == '__main__':
    app.run()
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
