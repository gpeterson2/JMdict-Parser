#! /usr/bin/env python

import os

import argparse

from models import init_model, Session
from models.entry import Entry
from parser import Parser

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
 
    connection_string = 'sqlite:///test.db'
    models = init_model(connection_string, is_verbose)

    ses = Session()

    if filename:
        if not os.path.exists(filename):
            print('Invalid file name')
            exit(1)

        models.drop_all()
        models.create_all()

        Parser(filename).parse()

    if list_values:
        entries = ses.query(Entry).all()
        for entry in entries:
            print(unicode(entry))

if __name__ == '__main__':
    main()
