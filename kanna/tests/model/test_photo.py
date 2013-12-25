import unittest

from mock import Mock
from mock import patch

from kanna.model import photo


class TestUpload(unittest.TestCase):

    @patch('kanna.model.photo.Photo')
    @patch('kanna.model.photo.exif.get_lat_lon')
    @patch('kanna.model.photo.exif.get_exif_data')
    @patch('kanna.model.photo.Image.open')
    @patch('kanna.model.photo.files')
    def test_happy_path(self, files, image_open, get_exif_data, get_lat_lon,
                        new_photo):
        """Verify upload saves the photo to the blobstore and creates a new
        Photo entity.
        """
        from google.appengine.ext import ndb

        mock_user_key = 'key'
        mock_user = Mock(key=mock_user_key)
        mock_file = Mock(filename='foo.jpg')
        mock_file.read.return_value = 'abc'

        files.blobstore.create.return_value = Mock()
        mock_key = Mock()
        files.blobstore.get_blob_key.return_value = mock_key
        mock_image = Mock()
        image_open.return_value = mock_image
        get_exif_data.return_value = {}
        get_lat_lon.return_value = (42.0169444444, -93.6438888889)
        mock_photo = Mock()
        new_photo.return_value = mock_photo

        actual = photo.upload(mock_file, mock_file.read(), mock_user)

        files.open.assert_called_once_with(
            files.blobstore.create.return_value, 'a')
        files.finalize.assert_called_once_with(
            files.blobstore.create.return_value)
        files.blobstore.get_blob_key.assert_called_once_with(
            files.blobstore.create.return_value)

        get_exif_data.assert_called_once_with(image_open.return_value)
        get_lat_lon.assert_called_once_with(get_exif_data.return_value)
        new_photo.assert_called_once_with(
            name=mock_file.filename, owner=mock_user_key, blob_key=mock_key,
            coordinates=ndb.GeoPt(*get_lat_lon.return_value))
        mock_photo.put.assert_called_once_with()

        self.assertEqual(mock_photo, actual)

