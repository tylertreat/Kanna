import json
from StringIO import StringIO

from google.appengine.api import files
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import ndb

from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
from werkzeug.utils import secure_filename

from kanna import exif
from kanna import settings


class Album(ndb.Model):
    """A collection of photos that are somehow related."""

    owner = ndb.KeyProperty(kind='User', required=True)
    name = ndb.StringProperty(required=True)
    description = ndb.TextProperty()


class Photo(ndb.Model):
    """Models a photo uploaded by a user. This entity acts as an index into
    the blobstore since that's where the photos are stored, but it also
    holds the metadata for the photo.
    """

    # User name of the photo, defaults to filename
    name = ndb.StringProperty(required=True)

    # When was I uploaded?
    uploaded = ndb.DateTimeProperty(required=True, auto_now_add=True)

    # User description of the photo
    description = ndb.TextProperty()

    # Uploader
    owner = ndb.KeyProperty(kind='User', required=True)

    # BlobKey for the photo in the blobstore
    primary_blob_key = ndb.BlobKeyProperty()

    # BlobKey for the circle thumbnail in the blobstore
    thumb_blob_key = ndb.BlobKeyProperty()

    # Latitude/Longitude coordinates of the photo
    coordinates = ndb.GeoPtProperty()

    # A short description of where the photo was taken
    location = ndb.StringProperty(indexed=False)

    # When the photo was taken
    timestamp = ndb.DateTimeProperty()

    # The album this photo belongs to
    album = ndb.KeyProperty(kind='Album')

    @classmethod
    def _pre_delete_hook(cls, key):
        """Clean up blobstore files."""

        photo = key.get()
        if photo:
            primary_blob = photo.primary_blob_key
            thumb_blob = photo.thumb_blob_key
            blobstore.delete([primary_blob, thumb_blob])

    def primary_serving_url(self, size=settings.MAP_THUMBNAIL_SIZE):
        """Return the serving url for the photo."""

        return images.get_serving_url(self.primary_blob_key, size=size)

    def thumbnail_serving_url(self, size=settings.MAP_THUMBNAIL_SIZE):
        """Return the serving url for the photo thumbnail."""

        return images.get_serving_url(self.thumb_blob_key, size=size)

    def json(self, size=settings.MAP_THUMBNAIL_SIZE):
        """Return the Photo as a json string."""
        from kanna.utils import to_dict

        entity_dict = to_dict(self)
        entity_dict['thumbnail'] = self.primary_serving_url(size=size)
        return json.dumps(entity_dict)


def upload(upload_file, image_data, user):
    """Upload a photo to the blobstore and create a photo entity to index it.

    Args:
        upload_file: the file the user uploaded.
        image_data: the raw file data to be stored as a blob.
        user: the user who uploaded the file.

    Returns:
        the photo entity for the uploaded file.
    """

    filename = secure_filename(upload_file.filename)
    blob_key = _write_to_blobstore(filename, image_data,
                                   upload_file.content_type)

    image = Image.open(StringIO(image_data))

    thumbnail = _create_circle_thumbnail(image)
    thumb_filename = secure_filename('%s_thumb' % upload_file.filename)
    thumb_key = _write_to_blobstore(thumb_filename, thumbnail, 'image/png')

    exif_data = exif.get_exif_data(image)
    lat, lon = exif.get_lat_lon(exif_data)
    coordinates = None if not lat or not lon else ndb.GeoPt(lat, lon)
    timestamp = exif.get_datetime(exif_data)

    photo = Photo(name=filename, owner=user.key, primary_blob_key=blob_key,
                  thumb_blob_key=thumb_key, coordinates=coordinates,
                  timestamp=timestamp)
    photo.put()

    return photo


def _write_to_blobstore(filename, data, content_type):
    """Write the given file data to the blobstore.

    Args:
        filename: the name to assign the blobstore file.
        data: the data to write to the blobstore.
        content_type: the file mime type.

    Returns:
        BlobKey for the saved blobstore file.
    """

    blob_io = files.blobstore.create(
        mime_type=content_type,
        _blobinfo_uploaded_filename=filename)

    with files.open(blob_io, 'a') as f:
        f.write(data)

    files.finalize(blob_io)

    return files.blobstore.get_blob_key(blob_io)


def _create_circle_thumbnail(image, size=(512, 512)):
    """Create a circle thumbnail for the given image.

    Args:
        image: the image to create the thumbnail for.
        size: the dimensions of the thumbnail.

    Returns:
        image data as a string.
    """

    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    buff = StringIO()
    output.save(buff, format='PNG')
    return buff.getvalue()

