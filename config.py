TIMEZONE = 'Europe/Kiev'
BASE_URL = 'https://auto.ria.com/uk/search/used/'
URL = 'https://auto.ria.com/uk/search/used/?page={page}&size=100'
DEVELOP = False

DUMPS_FOLDER = '/scrapper/dumps'
LOG_FOLDER = "/scrapper/log"
DB_USER = "scraper"
DB_PASSWORD = "12345678"
DB_HOST = "db"
DB_PORT = '5432'
DB_NAME = "scraper_db"

if DEVELOP:
    DUMPS_FOLDER = 'dumps'
    LOG_FOLDER = "log"
    DB_USER = "test"
    DB_PASSWORD = "test"
    DB_HOST = "localhost"
    DB_PORT = '5432'
    DB_NAME = "scraper_db"


DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
