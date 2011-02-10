import os
import meghanurback
ROOT_URLCONF = 'urls'  # Replace 'project.urls' with just 'urls'

DEBUG = False
OFFLINE = False

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.doc.XViewMiddleware',
## the below are not supported on app engine
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sites',
## the below are not supported on app engine
    #    'django.contrib.auth',
    #    'django.contrib.sessions',
)

ROOT_PATH = os.path.dirname(meghanurback.__file__)
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".  Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT_PATH + '/templates',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'meghanurback.context_processors.navigation',
)
