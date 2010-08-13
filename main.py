#! /usr/bin/env python

from model import init_model, Session

from model.entry import Entry
from parser import Parser

def main():
    connection_string = 'sqlite:///test.db'
    init_model(connection_string, False)

    ses = Session()

    filename = 'test_files/JMdict'

    p = Parser()
    p.parse(filename) 

if __name__ == '__main__':
    main()
