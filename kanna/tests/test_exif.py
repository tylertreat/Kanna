import datetime
import unittest

from mock import Mock

from kanna import exif


EXIF_DATA = {
    'LightSource': 0, 'YResolution': (72, 1), 'ResolutionUnit': 2,
    41987: 0, 41988: (0, 1000000), 41989: 28, 41990: 0, 41991: 0,
    41992: 0, 41993: 0, 'Make': 'HTC', 'Flash': 24, 41986: 0,
    'GPSInfo': {
        'GPSTimeStamp': ((0, 1), (3, 1), (25, 1)),
        'GPSLongitude': ((93, 1), (38, 1), (590167, 10000)),
        'GPSLatitudeRef': 'N', 29: '2013:12:17',
        'GPSAltitude': (0, 1000),
        'GPSLatitude': ((42, 1), (1, 1), (66046, 10000)),
        27: 'ASCII\x00\x00\x00NETWORK', 'GPSLongitudeRef': 'W',
        'GPSAltitudeRef': 0
    },
    'MeteringMode': 255, 'XResolution': (72, 1),
    'ExposureProgram': 2, 'ColorSpace': 1, 'ExifImageWidth': 1520,
    'DateTimeDigitized': '2013:12:16 18:03:45',
    'DateTimeOriginal': '2013:12:16 18:03:45', 41994: 0,
    'CompressedBitsPerPixel': (7658800, 4085760),
    'FNumber': (2000000, 1000000), 41985: 0,
    'ApertureValue': (2000000, 1000000), 'FocalLength': (382, 100),
    'SubsecTimeOriginal': '319',
    'ComponentsConfiguration': '\x01\x02\x03\x00', 'ExifOffset': 354,
    'ExifImageHeight': 2688, 'ISOSpeedRatings': 640,
    'Model': 'HTC6500LVW', 'DateTime': '2013:12:16 18:03:45',
    'Orientation': 1, 'ExposureTime': (66668, 1000000),
    'MaxApertureValue': (2000000, 1000000),
    'ExifInteroperabilityOffset': 1432, 'FlashPixVersion': '0100',
    'YCbCrPositioning': 1, 'ExifVersion': '0220'
}


class TestGetExifData(unittest.TestCase):

    def test_get_exif_data(self):
        """Verify get_exif_data returns a dict with Exif data."""

        mock_image = Mock()
        mock_image._getexif.return_value = EXIF_DATA

        actual = exif.get_exif_data(mock_image)

        mock_image._getexif.assert_called_once_with()
        self.assertEqual(EXIF_DATA, actual)


class TestGetLatLon(unittest.TestCase):

    def test_no_coords(self):
        """Verify get_lat_lon returns (None, None) when GPS coordinates are
        not available in the Exif data.
        """

        actual = exif.get_lat_lon(dict())

        self.assertEqual((None, None), actual)

    def test_get_coords(self):
        """Verify get_lat_lon returns the GPS coordinates contained in the Exif
        data.
        """

        lat, lon = exif.get_lat_lon(EXIF_DATA)

        self.assertEqual(42.01694444444444, lat)
        self.assertEqual(-93.6438888888889, lon)


class TestGetDateTime(unittest.TestCase):

    def test_no_datetime(self):
        """Verify get_datetime returns None when the date/time is not available
        in the Exif data.
        """

        actual = exif.get_datetime(dict())

        self.assertIsNone(actual)

    def test_get_datetime(self):
        """Verify get_datetime returns the DateTime contained in the Exif data.
        """

        actual = exif.get_datetime(EXIF_DATA)

        self.assertEqual(datetime.datetime(2013, 12, 16, 18, 3, 45), actual)
