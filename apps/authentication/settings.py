import environ

env = environ.Env()
environ.Env.read_env()  # Carga variables de .env

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'CLIENT': {
            'host': env('DATABASE_URL'),
        }
    }
}


