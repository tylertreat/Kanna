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


@patch('kanna.api.photos.photo.Photo.get_by_id')
class TestDelete(unittest.TestCase):

    def test_no_photo(self, get_by_id):
        """Verify delete returns a 404 code when there is no photo."""

        get_by_id.return_value = None
        photo_id = '123'

        resp, status = photos.delete(photo_id)

        get_by_id.assert_called_once_with(photo_id)
        self.assertEqual(404, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.get_session_user')
    def test_no_user(self, get_user, get_by_id):
        """Verify delete returns a 403 when there is no user."""

        get_by_id.return_value = Mock()
        get_user.return_value = None
        photo_id = '123'

        resp, status = photos.delete(photo_id)

        get_by_id.assert_called_once_with(photo_id)
        get_user.assert_called_once_with()
        self.assertEqual(403, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.get_session_user')
    def test_not_owner(self, get_user, get_by_id):
        """Verify delete returns a 403 when the user is not the photo owner."""

        get_by_id.return_value = Mock(owner='owner_key')
        get_user.return_value = Mock(key='key')
        photo_id = '123'

        resp, status = photos.delete(photo_id)

        get_by_id.assert_called_once_with(photo_id)
        get_user.assert_called_once_with()
        self.assertEqual(403, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.redirect')
    @patch('kanna.api.photos.get_session_user')
    def test_delete(self, get_user, redirect, get_by_id):
        """Verify delete deletes the photo entity."""

        key = 'key'
        photo_key = Mock()
        get_by_id.return_value = Mock(key=photo_key, owner=key)
        get_user.return_value = Mock(key=key)
        redirect.return_value = 'redirect'
        photo_id = '123'

        actual = photos.delete(photo_id)

        get_by_id.assert_called_once_with(photo_id)
        get_user.assert_called_once_with()
        get_by_id.return_value.key.delete.assert_called_once_with()
        self.assertEqual(redirect.return_value, actual)

