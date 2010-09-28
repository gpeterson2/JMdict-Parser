#! /usr/bin/env python

from lxml import etree

from model import Session
from model.entry import Entry
from model.r_ele import R_ele

class Parser(object):

    def parse(self, filename):
        #'test_files/JMdict'

        xml = open(filename, 'r')

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events)

        ses = Session()

        print('start reading')

        ses.begin()

        entry = Entry()

        # looks like there 142665 total r_ele
        # still taking forever...
        # OK, putting everything in a dict, and then inserting sped things up
        # I don't really want that to be the overall pattern, though
        for i, (action, elem) in enumerate(context):

            tag = elem.tag

            if tag == 'entry' and action == 'start':
                entry = Entry()

            if tag == 'ent_seq' and action == 'start':
                entry.ent_seq = elem.text
                print('%s' % elem.text)

            if tag == 'reb' and action == 'start':

                reb = R_ele()
                reb.reb = elem.text
                entry.r_ele.append(reb)

            if tag == 'entry' and action == 'end':
                ses.add(entry)

        ses.commit()

        print('done reading')

