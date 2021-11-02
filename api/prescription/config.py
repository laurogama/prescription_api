import os
from logging import Logger

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    logger = Logger
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
