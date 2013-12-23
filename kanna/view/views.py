from google.appengine.ext.webapp import blobstore_handlers

from flask import render_template

from kanna import settings
from kanna.auth import get_session_user
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


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

