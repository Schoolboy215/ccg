# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'data.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "a9djf45AMF1"

# Secret key for signing cookies
SECRET_KEY = "secret"

# Image upload settings
UPLOAD_FOLDER = "/var/www/ccg/static/cardImages"
ALLOWED_EXTENSIONS = set(['png'])

# Card visualization
TEXT_BACKGROUND='#e5e3da'
BORDER_COLOR='#877324'
CARDS_PER_ROW=4

# Card draw numbers
HOLO_CHANCE = 50
