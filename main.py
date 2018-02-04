#! /usr/bin/env python

import argparse
import os

from jmdict.parser.jmdict import JmdictParser
from jmdict.data.sql.base import Writer, Reader
from jmdict.utils.observer import ConsoleViewer
import settings


def main():
    parser = argparse.ArgumentParser(description='Import edict xml')
    parser.add_argument('--list', dest='list_values', action='store_true',
                        help='Display current dictionary')
    parser.add_argument('--import', '-i', dest='import_file',
                        help='File to import')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Use verbose settings')

    args = parser.parse_args()

    # is_verbose = args.verbose
    filename = args.import_file
    list_values = args.list_values

    connection_string = settings.CONNECTION_URI

    if filename:
        if not os.path.exists(filename):
            print('Invalid file name')
            exit(1)

        viewer = ConsoleViewer()
        jmdict_parser = JmdictParser()
        jmdict_parser.attach(viewer)

        entries = jmdict_parser.parse_from_file(filename)

        jmdict_writer = Writer(connection_string, drop_tables=True)
        jmdict_writer.attach(viewer)
        jmdict_writer.write(entries)

    if list_values:
        reader = Reader(connection_string)
        entries = reader.read()

        for entry in entries:
            print(entry)


if __name__ == '__main__':
    main()
