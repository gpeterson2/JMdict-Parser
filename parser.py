#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from lxml import etree

from data import write_list_to_database, get_parts_of_speach

class ParsedObject(object):
    ''' Convience object to hold multiple lists of items.
        
        Contains:
        entries - a list of all dictionary entries.
        kanas - a list of just unique kana entries.
        kanjis - a list of just unique kanji entries.
        glosses - a list of all translations. 
    '''
    def __init__(self):
        self.entries = []
        self.kanas = []
        kanjis = []
        glosses = []

class Entry(object):
    ''' An entry object.
        
        For a given entry contains all kana entries,
        all kanji entires, and all gloss entires.
    '''

    # TODO - should eventually be replaced by ORM

    def __init__(self):
        self.entry_seq = 0
        self.kanas = []
        self.kanjis = []
        self.glosses = []

    def __str__(self):
        return u'{0} [{1}] [{2}] {3}'.format(
            self.entry_seq, 
            u','.join(self.kanas), 
            u','.join(self.kanjis), 
            #u','.join(unicode(self.glosses))
            u','.join([g for g in self.glosses])
        )

class Parser(object):

    def __init__(self, infile, message_out=None):
        ''' Reads a JMDict file.
            
            :params infile: The JMDict input file.
            :params message_out: An output stream for parsing messages,
                defaults to none.
        '''

        # TODO - need to change the default output, maybe once I'm done it wont
        # be necessary?

        self.infile = infile
        self.kana_dict = set()

        self.message_out = message_out

    def __write_output(self, msg):
        ''' Writes and flushes a message to message_output. '''
        if not self.message_out:
            return

        #self.message_out.write(msg + u'\n')
        self.message_out.write(u'{0}\n'.format(msg).encode('utf-8'))
        self.message_out.flush()

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

        self.__write_output(u'start reading')

        entry = Entry()
        for i, (action, elem) in enumerate(context):

            tag = elem.tag
            text = elem.text

            if not text:
                continue

            # the starting element
            if tag == 'ent_seq' and action == 'start':
                ent_seq = elem.text
                entry = Entry()

                entry.entry_seq = ent_seq 

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

            # not used until it hits the gloss entry
            if tag == 'pos' and action == 'start':
                pos = None

                # Used in gloss
                pos_text = elem.text
                pos = pos_dict.get(pos_text, '')

                # Shouldn't happen, of course...
                # but write an error message if the text isn't found.
                if not pos:
                    self.__write_output(u'Error: Can\'t find: {0} {1}'.format(ent_seq, pos_text))

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

        self.__write_output(u'done reading')
        self.__write_output(u'start saving')

        #for entry in entries:
            #self.__write_output(unicode(entry))

        parsed_object = ParsedObject()
        parsed_object.entries = list(entries)
        parsed_object.kanas = list(kanas)
        parsed_object.kanjis = list(kanjis)
        parsed_object.glosses = list(glosses)
        
        write_list_to_database(parsed_object)

        self.__write_output(u'done saving')

