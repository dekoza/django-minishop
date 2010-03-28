import os
# Django settings for biolander project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('admin', 'admin@email.com'),
)

SHOP_STAFF_EMAILS = ('staff@email.com',)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'db_name'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl_PL'

SITE_ID = 1


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

FORCE_SCRIPT_NAME=""
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'e)@lym0d(re)9y-c++*zjd@c)9g#l3to1hjg6-_78^*4n+d(!_'

# List of callables that know how to import templates from various sources.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    "django.core.context_processors.request",
    "grappelli.context_processors.admin_url",
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'orders.context_processors.shopping_cart',
    'products.context_processors.manufacturers',
    'context_processors.current_url',
    'session_messages.context_processors.session_messages',

)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'biolander.ssl_middleware.SSLRedirect',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
CACHE_MIDDLEWARE_SECONDS = 120
CACHE_MIDDLEWARE_KEY_PREFIX = 'biol_pl_'

ROOT_URLCONF = 'biolander.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.comments',
    'biolander.mptt',
    'biolander.imaging',
    'biolander.products',
    'biolander.customers',
    'biolander.orders',
    'biolander.discounts',
    'biolander.blog',
    'biolander.tinymce',
    'biolander.session_messages',
    'biolander.voting',
    'sorl.thumbnail',
    'biolander.newsletter',
    'biolander.grappelli',
    'biolander.chartstats',
    'biolander.seoredirect',
    'biolander.stock',
#    'biolander.debug_toolbar',
)

IMAGING_SETTINGS = {
'image_sizes' : [
  { 
  'name':'small_thumb', 
  'width': 33,
  'height': 33,
  'aspect': True, 
  'suffix': '_thb'
  },
  { 
  'name':'medium_thumb', 
  'width': 150,
  'height': 150,
  'aspect': True, 
  'suffix': '_med_thb'
  },
  { 
  'name':'large_thumb', 
  'width': 190,
  'height': 190,
  'aspect': True, 
  'suffix': '_big_thb'
  },
  ],
'image_dir' : 'product_photos',
    }

TINYMCE_DEFAULT_CONFIG = {
    #'plugins': "advlink",
    'theme': "advanced",
    'theme_advanced_buttons1' : "bold,italic,underline,bullist,numlist,link,unlink,anchor,cleanup,code,formatselect",
    'theme_advanced_buttons2' : "",
    'theme_advanced_buttons3' : "",
    'theme_advanced_disable': "style,help",
    'theme_advanced_toolbar_location' : "top",
    }

AUTH_PROFILE_MODULE = 'customers.Customer'
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_URL = '/uzytkownicy/zaloguj/'

DEBUG_TOOLBAR_PANELS = (
#    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
)

DOTPAY = {
    'id': 00000,
    'currency': 'PLN',
    'lang': 'pl',
    'channel': None,
    'block': None,
    }

PRODUCTS_PER_PAGE = 12 
