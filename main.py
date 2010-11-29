#! /usr/bin/env python

import argparse

from model import init_model, Session

from model.entry import Entry
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
    init_model(connection_string, is_verbose)

    ses = Session()

    # Just to ensure the database stuff is run
    entries = ses.query(Entry).first()

    if filename:
        #filename = 'test_files/JMdict'

        p = Parser()
        p.parse(filename) 

    if list_values:
        entries = ses.query(Entry).all()
        for entry in entries:
            print(unicode(entry))

if __name__ == '__main__':
    main()
