#! /usr/bin/env python

from lxml import etree

from models import Session
from models.entry import Entry
from models.kana_element import KanaElement
from models.kanji_element import KanjiElement
from models.gloss import Gloss
from models.sense import Sense

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

                lang = 'eng'
                keys = elem.keys()
                # Should have 0 or 1
                if len(keys) > 0:
                    # Not calling directly because it's a full namespace
                    # this is easier
                    lang = elem.get(keys[0])

                gloss.lang = lang                    

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

