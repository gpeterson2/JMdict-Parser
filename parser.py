#! /usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree

from data import write_list_to_database, get_parts_of_speach

class ParsedObject(object):
    def __init__(self):
        self.entries = []
        self.kanas = []
        kanjis = []
        glosses = []

class Entry(object):
    def __init__(self):
        self.entry_seq = 0
        self.kanas = []
        self.kanjis = []
        self.glosses = []

class Parser(object):

    def __init__(self, infile):
        ''' Reads a JMDict file.
            
            :params infile: The JMDict input file.
        '''

        self.infile = infile
        self.kana_dict = set()

    def parse(self):
        ''' Performs the parsing of the file. '''

        xml = open(self.infile, 'r')

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events)

        # Set up the parts of speach, as I don't think there's
        # a way to read them directly from the file...
        pos_dict = get_parts_of_speach() 

        entries = set()
        kanas = set()
        kanjis = set()
        glosses = set()

        print('start reading')

        entry = Entry()
        for i, (action, elem) in enumerate(context):

            tag = elem.tag
            text = elem.text


            if not text:
                continue

            if tag == 'ent_seq' and action == 'start':
                ent_seq = elem.text
                entry = Entry()
        #        entries.add(ent_seq)

                entry.entry_seq = ent_seq 
                #print('{0} - {1}'.format(ent_seq, entry.entry_seq))

            if tag == 'reb' and action == 'start':
                kana = elem.text
                kanas.add(kana)

                entry.kanas.append(kana)

            if tag == 'keb' and action == 'start':
                kanji = elem.text
                kanjis.add(kanji)

                entry.kanjis.append(kanji)

            if tag == 'sense' and action == 'start':
                pass

            if tag == 'pos' and action == 'start':
                pos = None

                # Used in gloss
                pos_text = elem.text
                pos = pos_dict.get(pos_text, '')
                # Shouldn't happen, of course...
                #print('Can\'t find: %s %s' % (ent_seq, pos_text))

            if tag == 'gloss' and action == 'start':
                gloss = elem.text

                lang = 'eng'
                keys = elem.keys()

                # Should have 0 or 1
                if len(keys) > 0:
                    # This is easier than calling the namespace directly
                    lang = elem.get(keys[0])

                gloss = gloss.replace('"', '""'); 
                glosses.add((gloss, pos, lang))

                entry.glosses.append(gloss)

            # Not entirely sure this is even necessary...
            if tag == 'sense' and action == 'end':
                pass

            if tag == 'entry' and action == 'end':
                entries.add(entry)
                #print('{0}'.format(entry.entry_seq))

        print('done reading')
        print('start saving')

        parsed_object = ParsedObject()
        parsed_object.entries = list(entries)
        parsed_object.kanas = list(kanas)
        parsed_object.kanjis = list(kanjis)
        parsed_object.glosses = list(glosses)
        
        write_list_to_database(parsed_object)

        print('done saving')


