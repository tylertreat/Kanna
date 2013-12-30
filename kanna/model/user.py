from google.appengine.ext import ndb

from kanna.model.photo import Album
from kanna.model.photo import Photo


class User(ndb.Model):

    email = ndb.StringProperty()
    name = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)

    @property
    def photos(self):
        return Photo.gql('WHERE owner = :1', self.key)

    @property
    def albums(self):
        return Album.gql('WHERE owner = :1', self.key)

