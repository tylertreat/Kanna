from StringIO import StringIO

from google.appengine.api import files
from google.appengine.api import images
from google.appengine.ext import ndb

from PIL import Image
from werkzeug.utils import secure_filename

from kanna import exif
from kanna import settings


class Photo(ndb.Model):

    # User name of the photo, defaults to filename
    name = ndb.StringProperty(required=True)

    # When was I uploaded?
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)

    # User description of the photo
    description = ndb.TextProperty()

    # Uploader
    owner = ndb.KeyProperty(kind='User', required=True)

    # BlobKey for the photo in the blobstore
    blob_key = ndb.BlobKeyProperty()

    # Latitude/Longitude coordinates of the photo
    coordinates = ndb.GeoPtProperty()

    # A short description of where the photo was taken
    location = ndb.StringProperty(indexed=False)

    def serving_url(self, size=settings.MAP_THUMBNAIL_SIZE):
        return images.get_serving_url(self.blob_key, size=size)


def upload(upload_file, image_data, user):
    """Upload a photo to the blobstore and create a photo entity to index it.

    Args:
        upload_file: the file the user uploaded.
        image_data: the raw file data to be stored as a blob.
        user: the user who uploaded the file.

    Returns:
        the photo entity for the uploaded file.
    """

    file_name = secure_filename(upload_file.filename)
    blob_io = files.blobstore.create(
        mime_type=upload_file.content_type,
        _blobinfo_uploaded_filename=file_name)

    with files.open(blob_io, 'a') as f:
        f.write(image_data)

    files.finalize(blob_io)
    blob_key = files.blobstore.get_blob_key(blob_io)

    image = Image.open(StringIO(image_data))
    lat, lon = exif.get_lat_lon(exif.get_exif_data(image))
    coordinates = None if not lat or not lon else ndb.GeoPt(lat, lon)

    photo = Photo(name=file_name, owner=user.key, blob_key=blob_key,
                  coordinates=coordinates)
    photo.put()

    return photo

