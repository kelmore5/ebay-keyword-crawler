from peewee import *
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(os.path.join(dir_path, '..'))

db = SqliteDatabase(dir_path + '/ebay.db', pragmas=(('foreign_keys', 'on'),))


class BaseModel(Model):
    db = db

    class Meta:
        database = db
