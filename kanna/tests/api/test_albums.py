import unittest

from mock import Mock
from mock import patch
from mock import PropertyMock

from kanna.api import albums


@patch('kanna.api.albums.request')
@patch('kanna.api.albums.get_session_user')
class TestNewAlbum(unittest.TestCase):

    def test_no_user(self, get_session_user, request):
        """Verify new_album returns a 403 code when there is no session user.
        """

        get_session_user.return_value = None

        resp, status = albums.new_album()

        self.assertEqual(403, status)
        self.assertEqual('', resp)
        get_session_user.assert_called_once_with()

    @patch('kanna.api.albums.Album')
    def test_already_exists(self, album, get_session_user, request):
        """Verify new_album returns a 409 code when there is already an album
        with the provided name.
        """

        mock_key = Mock()
        mock_id = '123'
        mock_key.id.return_value = mock_id
        get_session_user.return_value = Mock(key=mock_key)
        album.get_by_id.return_value = Mock()
        name = 'foo'
        type(request).form = PropertyMock(return_value={'name': name})

        resp, status = albums.new_album()

        self.assertEqual(409, status)
        self.assertEqual('', resp)
        album.get_by_id.assert_called_once_with('%s_%s' % (mock_id, name))
        get_session_user.assert_called_once_with()

    @patch('kanna.api.albums.redirect')
    @patch('kanna.api.albums.Album')
    def test_new_album(self, album, redirect, get_session_user, request):
        """Verify new_album creates a new album entity."""

        mock_key = Mock()
        mock_id = '123'
        mock_key.id.return_value = mock_id
        get_session_user.return_value = Mock(key=mock_key)
        album.get_by_id.return_value = None
        name = 'foo'
        type(request).form = PropertyMock(return_value={'name': name})
        album.return_value = Mock()
        redirect.return_value = 'redirect'

        actual = albums.new_album()

        self.assertEqual(redirect.return_value, actual)
        album.get_by_id.assert_called_once_with('%s_%s' % (mock_id, name))
        get_session_user.assert_called_once_with()
        album.return_value.put.assert_called_once_with()

