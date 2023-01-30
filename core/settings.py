import datetime
import time

from os import environ
from dotenv import load_dotenv

load_dotenv()


class Settings:

    BOT_TOKEN: str = environ['BOT_TOKEN']

    # DB Setup
    DB_USER: str = environ['DB_USER']
    DB_PASSWORD: str = environ['DB_PASSWORD']
    DB_SERVER: str = environ['DB_SERVER']
    DB_PORT: str = environ['DB_PORT']
    DB_NAME: str = environ['DB_NAME']
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

    # DB Test Setup
    DB_TEST_USER: str = environ['DB_TEST_USER']
    DB_TEST_PASSWORD: str = environ['DB_TEST_PASSWORD']
    DB_TEST_SERVER: str = environ['DB_TEST_SERVER']
    DB_TEST_PORT: str = environ['DB_TEST_PORT']
    DB_TEST_NAME: str = environ['DB_TEST_NAME']
    DATABASE_TEST_URL: str = f"postgresql://{DB_TEST_USER}:{DB_TEST_PASSWORD}@{DB_TEST_SERVER}:{DB_TEST_PORT}/{DB_TEST_NAME}"


settings = Settings()
