from StringIO import StringIO

from google.appengine.api import files
from google.appengine.ext import ndb

from flask import redirect
from flask import request
from PIL import Image
from werkzeug.utils import secure_filename

from kanna import exif
from kanna.api.blueprint import blueprint
from kanna.auth import get_session_user
from kanna.model.photo import Photo

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@blueprint.route("/v1/upload", methods=["POST"])
def upload():
    upload_file = request.files.get('file')
    image_data = upload_file.read()

    user = get_session_user()
    if not user:
        return '', 403

    if not image_data or not allowed_file(upload_file.filename):
        return '', 403

    file_name = secure_filename(upload_file.filename)
    blob_io = files.blobstore.create(
        mime_type=upload_file.content_type,
        _blobinfo_uploaded_filename=file_name)

    with files.open(blob_io, 'a') as f:
        f.write(image_data)

    files.finalize(blob_io)
    blob_key = files.blobstore.get_blob_key(blob_io)

    image = Image.open(StringIO(image_data))
    lat_lon = exif.get_lat_lon(exif.get_exif_data(image))
    location = None if not lat_lon else ndb.GeoPt(*lat_lon)

    Photo(name=file_name, owner=user.key, blob_key=blob_key,
          location=location).put()

    return redirect('/')

