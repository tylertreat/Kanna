import unittest

from mock import Mock
from mock import patch
from mock import PropertyMock

from kanna.api import photos


@patch('kanna.api.photos.request')
@patch('kanna.api.photos.get_session_user')
class TestUpload(unittest.TestCase):

    def test_no_user(self, get_session_user, request):
        """Verify upload returns a 403 code when there is no session user."""

        get_session_user.return_value = None

        resp, status = photos.upload()

        self.assertEqual(403, status)
        self.assertEqual('', resp)

    def test_no_data(self, get_session_user, request):
        """Verify upload returns a 403 code when there is no image data."""

        get_session_user.return_value = Mock()
        mock_file = Mock()
        mock_file.read.return_value = None
        type(request).files = PropertyMock(return_value={'file': mock_file})

        resp, status = photos.upload()

        self.assertEqual(403, status)
        self.assertEqual('', resp)

    def test_bad_file(self, get_session_user, request):
        """Verify upload returns a 403 code when the uploaded file type is not
        allowed.
        """

        get_session_user.return_value = Mock()
        mock_file = Mock(filename='foo.pdf')
        mock_file.read.return_value = 'abc'
        type(request).files = PropertyMock(return_value={'file': mock_file})

        resp, status = photos.upload()

        self.assertEqual(403, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.redirect')
    @patch('kanna.api.photos.Photo')
    @patch('kanna.api.photos.exif.get_lat_lon')
    @patch('kanna.api.photos.exif.get_exif_data')
    @patch('kanna.api.photos.Image.open')
    @patch('kanna.api.photos.files.blobstore.get_blob_key')
    @patch('kanna.api.photos.files.finalize')
    @patch('kanna.api.photos.files.open')
    @patch('kanna.api.photos.files.blobstore.create')
    def test_happy_path(self, create, fopen, finalize, get_blob_key,
                        image_open, get_exif_data, get_lat_lon, photo,
                        redirect, get_session_user, request):
        """Verify upload saves the photo to the blobstore and creates a new
        Photo entity.
        """
        from google.appengine.ext import ndb

        mock_user_key = 'key'
        mock_user = Mock(key=mock_user_key)
        get_session_user.return_value = mock_user
        mock_file = Mock(filename='foo.jpg')
        mock_file.read.return_value = 'abc'
        type(request).files = PropertyMock(return_value={'file': mock_file})

        create.return_value = Mock()
        mock_key = Mock()
        get_blob_key.return_value = mock_key
        mock_image = Mock()
        image_open.return_value = mock_image
        get_exif_data.return_value = {}
        get_lat_lon.return_value = (42.0169444444, -93.6438888889)
        mock_photo = Mock()
        photo.return_value = mock_photo
        redirect.return_value = 'redirect', 200

        resp, status = photos.upload()

        fopen.assert_called_once_with(create.return_value, 'a')
        finalize.assert_called_once_with(create.return_value)
        get_blob_key.assert_called_once_with(create.return_value)
        get_exif_data.assert_called_once_with(image_open.return_value)
        get_lat_lon.assert_called_once_with(get_exif_data.return_value)
        photo.assert_called_once_with(name=mock_file.filename,
                                      owner=mock_user_key, blob_key=mock_key,
                                      location=ndb.GeoPt(
                                          *get_lat_lon.return_value))
        mock_photo.put.assert_called_once_with()

        self.assertEqual(200, status)
        self.assertEqual('redirect', resp)

