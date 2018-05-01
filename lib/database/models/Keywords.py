import os.path
import sys
from .BaseModel import BaseModel
from .Posts import Posts
from peewee import *
from typing import Sequence

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(os.path.join(dir_path, '../../..'))

sys.path.append(dir_path)

# noinspection PyPep8Naming
from lib.utilities.lib.Jsons import Jsons as jsons


class KeywordsKeys(object):
    title = 'title'
    link = 'link'
    group = 'group'
    keywords_in_title = 'keywords_in_title'
    keywords_in_message = 'keywords_in_message'

    keys = [title, link, group, keywords_in_title, keywords_in_message]


class Keywords(BaseModel):
    title = ForeignKeyField(Posts, to_field="title")
    link = ForeignKeyField(Posts, to_field="link")
    group = CharField(max_length=255)
    keywords_in_title = TextField()
    keywords_in_message = TextField()

    @staticmethod
    def initialize(params: dict) -> 'Keywords':
        KK = KeywordsKeys
        keywords = Keywords()

        if KK.title in params:
            keywords.title = params[KK.title]

        if KK.link in params:
            keywords.link = params[KK.link]

        if KK.group in params:
            keywords.group = params[KK.group]

        if KK.keywords_in_title in params:
            keywords.keywords_in_title = params[KK.keywords_in_title]

        if KK.keywords_in_message in params:
            keywords.keywords_in_message = params[KK.keywords_in_message]

        return keywords

    def __str__(self):
        return str(jsons.create_dict(KeywordsKeys.keys, self.values()))

    def __repr__(self):
        return str(jsons.create_dict(KeywordsKeys.keys, self.values()))

    def values(self):
        try:
            title = self.title
        except DoesNotExist:
            title = None

        try:
            link = self.link
        except DoesNotExist:
            link = None

        return [title, link, self.group, self.keywords_in_title, self.keywords_in_message]

    def to_dict(self):
        KK = KeywordsKeys
        output = dict()

        if self.title is not None:
            output[KK.title] = self.title.title

        if self.link is not None:
            output[KK.link] = self.link.link

        if self.group is not None:
            output[KK.group] = self.group

        if self.keywords_in_title is not None:
            output[KK.keywords_in_title] = self.keywords_in_title

        if self.keywords_in_message is not None:
            output[KK.keywords_in_message] = self.keywords_in_message

        return output

    def upload_many(self, upload: Sequence['Keywords']):
        self.insert_many([x.to_dict() for x in upload]).on_conflict('replace').execute()

    class Meta:
        indexes = ((("title", "group"), True),)
