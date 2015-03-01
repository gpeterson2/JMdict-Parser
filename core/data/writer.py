#! /usr/bin/env python
# -*- coding: utf-8 -*-

from core.utils.observer import Subject

class Writer(Subject):
    ''' Generic Writer class. '''

    def __init__(self, *args, **kwargs):
        super(Writer, self).__init__(*args, **kwargs)

    def write(self, data, *args, **kwargs):
        ''' Writes the data into the appropriate storage format. '''

        raise NotImplemented()
