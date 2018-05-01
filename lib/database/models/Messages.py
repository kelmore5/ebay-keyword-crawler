import os.path
import sys
from .Posts import Posts
from .BaseModel import BaseModel
from peewee import *
from typing import Sequence

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(os.path.join(dir_path, '../../..'))

sys.path.append(dir_path)

# noinspection PyPep8Naming
from lib.utilities.lib.Jsons import Jsons as jsons


class MessagesKeys(object):
    title = 'title'
    link = 'link'
    page_num = 'page_num'
    message_num = 'message_num'
    message = 'message'

    keys = [title, link, page_num, message_num, message]


class Messages(BaseModel):
    title = ForeignKeyField(Posts, to_field="title")
    link = ForeignKeyField(Posts, to_field="link")
    page_num = IntegerField()
    message_num = IntegerField()
    message = TextField()

    @staticmethod
    def initialize(params: dict) -> 'Messages':
        MK = MessagesKeys
        message = Messages()

        if MK.title in params:
            message.title = params[MK.title]

        if MK.link in params:
            message.link = params[MK.link]

        if MK.page_num in params:
            message.page_num = params[MK.page_num]

        if MK.message_num in params:
            message.message_num = params[MK.message_num]

        if MK.message in params:
            message.message = params[MK.message]

        return message

    def __str__(self):
        return str(jsons.create_dict(MessagesKeys.keys, self.values()))

    def __repr__(self):
        return str(jsons.create_dict(MessagesKeys.keys, self.values()))

    def values(self):
        try:
            title = self.title
        except DoesNotExist:
            title = None

        try:
            link = self.link
        except DoesNotExist:
            link = None

        return [title, link, self.page_num, self.message_num, self.message]

    def to_dict(self):
        MK = MessagesKeys
        output = dict()

        if self.title is not None:
            output[MK.title] = self.title.title

        if self.link is not None:
            output[MK.link] = self.link.link

        if self.page_num is not None:
            output[MK.page_num] = self.page_num

        if self.message_num is not None:
            output[MK.message_num] = self.message_num

        if self.message is not None:
            output[MK.message] = self.message

        return output

    def upload_many(self, upload: Sequence['Messages']):
        if len(upload) > 0:
            self.insert_many([x.to_dict() for x in upload]).on_conflict('replace').execute()

    class Meta:
        indexes = ((("title", "page_num", "message_num"), True), (("link",), False))
