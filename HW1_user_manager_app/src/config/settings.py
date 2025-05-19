from decouple import config

# Configuración de la aplicación
APP_NAME = config('APP_NAME', default='User Management System')
DEBUG = config('DEBUG', default=False, cast=bool)
DEFAULT_DATA_FILE = config('DEFAULT_DATA_FILE', default='data/users.json')