#! /usr/bin/env python

from lxml import etree

from model import Session
from model.entry import Entry
from model.kana_element import KanaElement
from model.kanji_element import KanjiElement
from model.gloss import Gloss
from model.sense import Sense

class Parser(object):

    def parse(self, filename):
        #'test_files/JMdict'

        xml = open(filename, 'r')

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events)

        ses = Session()
        #ses.begin()

        entry = Entry()

        print('start reading')

        # looks like there 142665 total r_ele
        # still taking forever...
        # OK, putting everything in a dict, and then inserting sped things up
        # I don't really want that to be the overall pattern, though
        for i, (action, elem) in enumerate(context):

            tag = elem.tag

            if tag == 'entry' and action == 'start':
                entry = Entry()
                ses.begin()

            if tag == 'ent_seq' and action == 'start':
                entry.ent_seq = elem.text

            if tag == 'reb' and action == 'start':

                kana = KanaElement()
                kana.element = elem.text
                entry.kana.append(kana)

            if tag == 'keb' and action == 'start':

                kanji = KanjiElement()
                kanji.element = elem.text
                entry.kanji.append(kanji)

            if tag == 'sense' and action == 'start':
                sense = Sense();

            if tag == 'gloss' and action == 'start':
                gloss = Gloss()
                gloss.gloss = elem.text;
                sense.gloss.append(gloss)

            if tag == 'sense' and action == 'end':
                entry.sense.append(sense)

            if tag == 'entry' and action == 'end':
                ses.add(entry)
                ses.commit()

                # to make testing easier
                if i > 1000:
                    break

        print('done reading')
        print('commiting')

        #ses.commit()

        print('done commiting')

