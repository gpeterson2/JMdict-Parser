#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
import StringIO

class BaseXMLParser(object):
    ''' Base XML Parser, implentations are expected to override "parse". '''

    def parse_from_file(self, path=None):
        ''' Parse a XML file from the given a filepath.

            :param path: Path to a file to read.
        '''

        f = None
        if path.endswith('.gz'):
            f = gzip.open(path, 'r')
        else:
            # assume xml
            f = open(path, 'r')
        return self.parse(f)

    def parse_from_string(self, data):
        ''' Parse a XML string.

            :params data: The string to read.
        '''

        xml = StringIO.StringIO(data)
        return self.parse(xml)

    def parse(self, xml):
        raise NotImplemented()
