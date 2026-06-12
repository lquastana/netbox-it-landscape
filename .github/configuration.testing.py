# NetBox configuration used by the CI test workflow.
DATABASE = {
    'NAME': 'netbox',
    'USER': 'netbox',
    'PASSWORD': 'netbox',
    'HOST': 'localhost',
    'PORT': '',
    'CONN_MAX_AGE': 300,
}

# NetBox ≥ 4.3 also accepts the DATABASES dict; DATABASE remains supported.

REDIS = {
    'tasks': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,
        'SSL': False,
    },
}

SECRET_KEY = 'ci-testing-secret-key-0123456789-0123456789-0123456789-abcdef'

ALLOWED_HOSTS = ['*']

PLUGINS = ['netbox_it_landscape']

DEFAULT_LANGUAGE = 'en-us'
