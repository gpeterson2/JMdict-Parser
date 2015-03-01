#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json

import pymongo

from core.data.writer import Writer

class MongoWriter(Writer):
    ''' Mongo Writer. '''

    # TODO - allow you to change databse, collection, whatever later.
    def __init__(self, uri, database, collection, *args, **kwargs):
        ''' Initializes a mongo writer.

            :params uri: A pymongo uri.
            :params database: The database to write to.
        '''

        super(MongoWriter, self).__init__(*args, **kwargs)

        self.client = pymongo.MongoClient(uri)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def write(self, data):
        ''' Inserts the data into mongo. '''

        # TODO - this is a hack to get this work, when time permits update
        # this, or more likely the class definitions.
        s = json.dumps(data, default=lambda x : x.__dict__)
        values = json.loads(s)


        # TODO - not much in the way of notifications here.
        self.collection.insert(values)
