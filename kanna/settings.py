import os


DEBUG = False

# Auto-set debug mode based on App Engine dev environ
if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
    DEBUG = True


# Flask-Cache settings
CACHE_TYPE = 'gaememcached'

# Application settings
MAPS_API_KEY = 'AIzaSyD0h4NaBtpIz6GaYXJz_BUacxRq6SdxEVg'
MAP_THUMBNAIL_SIZE = 75

try:
    import settingslocal
except ImportError:
    settingslocal = None

if settingslocal:
    for setting in dir(settingslocal):
        globals()[setting.upper()] = getattr(settingslocal, setting)

