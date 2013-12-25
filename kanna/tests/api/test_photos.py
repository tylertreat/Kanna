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

