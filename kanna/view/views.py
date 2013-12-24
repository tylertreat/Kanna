from flask import render_template

from kanna import settings
from kanna.auth import get_session_user
from kanna.model.photo import Photo
from kanna.view.blueprint import blueprint


# Error handlers
@blueprint.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@blueprint.route('/')
def index():
    """Render the index page."""

    user = get_session_user()

    return render_template('index.html', photos=user.photos,
                           api_key=settings.MAPS_API_KEY,
                           map_thumbnail_size=settings.MAP_THUMBNAIL_SIZE)


@blueprint.route('/upload')
def upload():
    """Render the upload page."""

    return render_template('upload.html')


@blueprint.route('/view/<int:photo_id>')
def view(photo_id):
    """Render the photo view page."""

    photo = Photo.get_by_id(photo_id)

    if not photo:
        return render_template('404.html'), 404

    return render_template('photo.html', photo=photo)

