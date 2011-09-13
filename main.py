#! /usr/bin/env python

import argparse
import codecs
import os
import sys

from JMdictParser import Parser
from data import write_list_to_database

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

        print('start reading')
        entries = Parser(filename, sys.stdout).parse_from_file()
        print('done reading')
        print('start saving')
        write_list_to_database(entries)
        print('done saving')

    if list_values:
        print('Not implemented')

if __name__ == '__main__':
    main()
