from google.appengine.ext.webapp import blobstore_handlers

from flask import render_template

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

    return render_template('index.html', photos=user.photos)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

