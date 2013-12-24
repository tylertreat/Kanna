from google.appengine.api import images
from google.appengine.ext import ndb

from kanna import settings


class Photo(ndb.Model):

    name = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    description = ndb.TextProperty()
    owner = ndb.KeyProperty(kind='User', required=True)
    blob_key = ndb.BlobKeyProperty()
    location = ndb.GeoPtProperty()

    def serving_url(self, size=settings.MAP_THUMBNAIL_SIZE):
        return images.get_serving_url(self.blob_key, size=size)

