import os.path
import sys
from .BaseModel import BaseModel
from peewee import *
from typing import Sequence

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(os.path.join(dir_path, '../../..'))

sys.path.append(dir_path)

# noinspection PyPep8Naming
from lib.utilities.lib.Jsons import Jsons as jsons


class PostsKeys(object):
    title = 'title'
    link = 'link'
    total_pages = 'total_pages'
    total_comments = 'total_comments'
    creation_date = 'creation_date'
    last_post_date = 'last_post_date'

    keys = [title, link, total_pages, total_comments, creation_date, last_post_date]


class Posts(BaseModel):
    title = CharField(max_length=1000)
    link = CharField(max_length=1200, unique=True)
    total_pages = IntegerField()
    total_comments = IntegerField()
    creation_date = DateField()
    last_post_date = DateField()

    @staticmethod
    def initialize(params: dict) -> 'Posts':
        PK = PostsKeys
        post = Posts()

        if PK.title in params:
            post.title = params[PK.title]

        if PK.link in params:
            post.link = params[PK.link]

        if PK.total_pages in params:
            post.total_pages = params[PK.total_pages]

        if PK.total_comments in params:
            post.total_comments = params[PK.total_comments]

        if PK.creation_date in params:
            post.creation_date = params[PK.creation_date]

        if PK.last_post_date in params:
            post.last_post_date = params[PK.last_post_date]

        return post

    def __str__(self):
        return str(jsons.create_dict(PostsKeys.keys, self.values()))

    def __repr__(self):
        return str(jsons.create_dict(PostsKeys.keys, self.values()))

    def values(self):
        return [self.title, self.link, self.total_pages, self.total_comments, self.creation_date, self.last_post_date]

    def to_dict(self):
        PK = PostsKeys
        output = dict()

        if self.title is not None:
            output[PK.title] = self.title

        if self.link is not None:
            output[PK.link] = self.link

        if self.total_pages is not None:
            output[PK.total_pages] = self.total_pages

        if self.total_comments is not None:
            output[PK.total_comments] = self.total_comments

        if self.creation_date is not None:
            output[PK.creation_date] = self.creation_date

        if self.last_post_date is not None:
            output[PK.last_post_date] = self.last_post_date

        return output

    def upload_many(self, upload: Sequence['Posts']):
        self.insert_many([x.to_dict() for x in upload]).on_conflict('replace').execute()

    class Meta:
        indexes = ((("title",), True), (("title", "total_pages"), True),)
