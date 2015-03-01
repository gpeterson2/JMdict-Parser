#! /usr/bin/env python

import argparse
import codecs
import os
import sys

from jmdict.parser.jmdict import Parser as JmdParser
from kanjidic2.parser import Parser as KdParser
from jmdict.data import SqliteWriter, SqliteReader
from jmdict.utils.observer import ConsoleViewer

def main():
    parser = argparse.ArgumentParser(description='Import edict xml')
    parser.add_argument('--type', dest='parser_type', action='store',
        help='Type of file to import "jmdict" or "kanjidic2"')
    parser.add_argument('--list', dest='list_values', action='store_true',
        help='Display current dictionary')
    parser.add_argument('--import', '-i', dest='import_file',
        help='File to import')
    parser.add_argument('--verbose', '-v', action='store_true',
        help='Use verbose settings')

    args = parser.parse_args()

    is_verbose = args.verbose
    filename = args.import_file
    list_values = args.list_values
    parser_type = args.parser_type

    if parser_type not in ('jmdict', 'kanjidic2'):
        print('invalid type')
        exit(1)

    if filename:
        if not os.path.exists(filename):
            print('Invalid file name')
            exit(1)

        viewer = ConsoleViewer()
        parser = None

        if parser_type == 'jmdict':
            parser = JmdParser()
        else:
            parser = KdParser()

        parser.attach(viewer)

        values = parser.parse_from_file(filename)

        print(len(values))

        #writer = SqliteWriter()
        #writer.attach(viewer)
        #writer.write(entries)

    #if list_values:
        #reader = SqliteReader()
        #entries = reader.read()
        #
        #for entry in entries:
            #print(entry)

if __name__ == '__main__':
    main()

