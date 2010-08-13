#! /usr/bin/env python

from model import init_model, Session

def main():
    connection_string = 'sqlite:///test.db'
    init_model(connection_string, False)

    ses = Session()

if __name__ == '__main__':
    main()
