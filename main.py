#! /usr/bin/env python

from model import init_model, Session

from model.entry import Entry
from parser import Parser

def main():
    connection_string = 'sqlite:///test.db'
    init_model(connection_string, True)

    ses = Session()

    filename = 'test_files/JMdict'

    # Just to ensure the database stuff is run
    entries = ses.query(Entry).first();
    p = Parser()
    p.parse(filename) 

if __name__ == '__main__':
    main()
