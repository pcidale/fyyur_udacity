import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
fyyur_usr = os.getenv('fyyur_usr')
fyyur_pwd = os.getenv('fyyur_pwd')
SQLALCHEMY_DATABASE_URI = f'postgresql://{fyyur_usr}:{fyyur_pwd}@localhost:5432/fyyur'

# Track modifications
SQLALCHEMY_TRACK_MODIFICATIONS = False
