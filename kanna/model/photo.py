from google.appengine.ext import ndb


class Photo(ndb.Model):

    name = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    description = ndb.TextProperty()
    owner = ndb.KeyProperty(kind='User', required=True)
    blob_key = ndb.BlobKeyProperty()
    location = ndb.GeoPtProperty()

