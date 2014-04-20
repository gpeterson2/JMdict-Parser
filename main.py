#! /usr/bin/env python

import argparse
import codecs
import os
import sys

from jmdict.parser.jmdict import Parser
from jmdict.data import SqliteWriter, SqliteReader
from jmdict.utils.observer import ConsoleViewer

def main():
    parser = argparse.ArgumentParser(description='Import edict xml')
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

    if filename:
        if not os.path.exists(filename):
            print('Invalid file name')
            exit(1)

        viewer = ConsoleViewer()
        parser = Parser()
        parser.attach(viewer)

        entries = parser.parse_from_file(filename)

        writer = SqliteWriter()
        writer.attach(viewer)
        writer.write(entries)

    if list_values:
        reader = SqliteReader()
        entries = reader.read()

        for entry in entries:
            print(entry)

if __name__ == '__main__':
    main()

