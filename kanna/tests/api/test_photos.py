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


@patch('kanna.api.photos.photo.ndb.Key')
class TestDelete(unittest.TestCase):

    def test_no_photo(self, key):
        """Verify delete returns a 404 code when there is no photo."""

        mock_key = Mock()
        mock_key.get.return_value = None
        key.return_value = mock_key
        photo_key = '123'

        resp, status = photos.delete(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        self.assertEqual(404, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.get_session_user')
    def test_no_user(self, get_user, key):
        """Verify delete returns a 403 when there is no user."""

        mock_key = Mock()
        mock_key.get.return_value = Mock(owner='owner_key')
        key.return_value = mock_key
        get_user.return_value = None
        photo_key = '123'

        resp, status = photos.delete(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        get_user.assert_called_once_with()
        self.assertEqual(403, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.get_session_user')
    def test_not_owner(self, get_user, key):
        """Verify delete returns a 403 when the user is not the photo owner."""

        mock_key = Mock()
        mock_key.get.return_value = Mock(owner='owner_key')
        key.return_value = mock_key
        get_user.return_value = Mock(key='key')
        photo_key = '123'

        resp, status = photos.delete(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        get_user.assert_called_once_with()
        self.assertEqual(403, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.redirect')
    @patch('kanna.api.photos.get_session_user')
    def test_delete(self, get_user, redirect, key):
        """Verify delete deletes the photo entity."""

        mock_key = Mock()
        mock_photo_key = Mock()
        mock_key.get.return_value = Mock(key=mock_photo_key, owner='owner_key')
        key.return_value = mock_key
        get_user.return_value = Mock(key='owner_key')
        redirect.return_value = 'redirect'
        photo_key = '123'

        actual = photos.delete(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        get_user.assert_called_once_with()
        mock_photo_key.delete.assert_called_once_with()
        self.assertEqual(redirect.return_value, actual)


@patch('kanna.api.photos.ndb.Key')
class TestUpdate(unittest.TestCase):

    def test_no_photo(self, key):
        """Verify update returns a 404 code when there is no photo."""

        mock_key = Mock()
        mock_key.get.return_value = None
        key.return_value = mock_key
        photo_key = '123'

        resp, status = photos.update(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        self.assertEqual(404, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.get_session_user')
    def test_no_user(self, get_user, key):
        """Verify update returns a 403 when there is no user."""

        mock_key = Mock()
        mock_key.get.return_value = Mock()
        key.return_value = mock_key
        get_user.return_value = None
        photo_key = '123'

        resp, status = photos.update(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        get_user.assert_called_once_with()
        self.assertEqual(403, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.get_session_user')
    def test_not_owner(self, get_user, key):
        """Verify update returns a 403 when the user is not the photo owner."""

        mock_key = Mock()
        mock_key.get.return_value = Mock(owner='owner_key')
        key.return_value = mock_key
        get_user.return_value = Mock(key='key')
        photo_key = '123'

        resp, status = photos.update(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        get_user.assert_called_once_with()
        self.assertEqual(403, status)
        self.assertEqual('', resp)

    @patch('kanna.api.photos.redirect')
    @patch('kanna.api.photos.request')
    @patch('kanna.api.photos.get_session_user')
    def test_update(self, get_user, request, redirect, key):
        """Verify update updates the entity."""

        mock_key = Mock()
        mock_key.get.return_value = Mock(owner='owner_key')
        key.return_value = mock_key
        get_user.return_value = Mock(key='owner_key')
        photo_key = '123'
        type(request).form = PropertyMock(return_value={'name': 'foo',
                                                        'description': 'bar',
                                                        'location': 'baz'})
        redirect.return_value = 'redirect'

        actual = photos.update(photo_key)

        key.assert_called_once_with(urlsafe=photo_key)
        mock_key.get.assert_called_once_with()
        get_user.assert_called_once_with()
        mock_key.get.return_value.put.assert_called_once_with()
        self.assertEqual(redirect.return_value, actual)

