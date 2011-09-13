#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from lxml import etree

from data import write_list_to_database 

__all__ = ['Entry', 'Gloss', 'Parser']

# TODO - should ideally be replaced by an ORM
# TODO - at the least it should also be moved to a separate location
class Entry(object):
    ''' An entry object.

        For a given entry contains all kana entries,
        all kanji entires, and all gloss entires.
    '''

    def __init__(self, entry_seq=0, kanas=None, kanjis=None, glosses=None):

        if not kanas:
            kanas = []

        if not kanjis:
            kanjis = []

        if not glosses:
            glosses = []

        self.entry_seq = entry_seq
        self.kanas = kanas
        self.kanjis = kanjis
        self.glosses = glosses

    def __str__(self):
        gloss_str = u','.join([g.gloss for g in self.glosses])

        return u'{0} [{1}] [{2}] {3}'.format(
            unicode(self.entry_seq),
            u','.join(self.kanas),
            u','.join(self.kanjis),
            gloss_str
        )

    def __repr__(self):
        return 'Entry({0}, {0}, {0}, {0})'.format(
            self.entry_seq, ','.join(repr(self.kanas)),
            ','.join(repr(self.kanjis)), ','.join(repr(self.glosses))
        )

class Gloss(object):
    ''' Object to contain translations.

        :param gloss: The translated text.
        :param pos: The part of speech for the entry.
        :param lang: The language of the translation.
    '''

    def __init__(self, gloss='', pos='', lang=''):
        self.gloss = gloss
        self.pos = pos
        self.lang = lang

    def __str__(self):
        return u'{0} {1} {2}'.format(self.gloss, self.pos, self.lang)

    def __repr__(self):
        return "Gloss('{0}', '{1}', '{2}')".format(
            self.gloss, self.pos, self.lang
        )

    def __eq__(self, other):
        return self.gloss == other.gloss and self.pos == other.pos and self.lang == other.lang

    def __hash__(self):
        return hash(unicode(self.gloss) + unicode(self.pos) + unicode(self.lang))

class Parser(object):

    def __init__(self, infile=None, message_out=None):
        ''' Reads a JMDict file.

            :params infile: The JMDict input file.
            :params message_out: An output stream for parsing messages,
                defaults to none.
        '''

        # TODO - need to change the default output, maybe once I'm done it wont
        # be necessary?

        if infile:
            self.infile = infile

        self.kana_dict = set()

        self.message_out = message_out

    # TODO - should move this somewhere else.
    # At the very least it should follow an observer pattern, rather than writing and flushing now.
    def __write_output(self, msg):
        ''' Writes and flushes a message to message_output. '''

        if not self.message_out:
            return

        self.message_out.write(u'{0}\n'.format(msg).encode('utf-8'))
        self.message_out.flush()

    def parse_from_file(self, path=None):
        ''' Parse a JMDict file from the given a filepath.

            :param path: Path to a file to read.
        '''

        if not path:
            path = self.infile

        xml = open(path, 'r')
        return self.parse(xml)

    def parse_from_string(self, data):
        ''' Parse a JMDict string.

            :params data: The string to read.
        '''

        from StringIO import StringIO
        xml = StringIO(data)

        return self.parse(xml)

    def parse(self, xml):
        ''' Performs the parsing of the file. '''

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events)

        entries = []

        self.__write_output(u'start reading')

        pos = None

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

                entry.kanas.append(kana)

            if tag == 'keb' and action == 'start':
                kanji = elem.text

                entry.kanjis.append(kanji)

            if tag == 'sense' and action == 'start':
                pass

            # not used until it hits the gloss entry
            if tag == 'pos' and action == 'start':
                pos = None

                pos = elem.text

                # Shouldn't happen, of course...
                # but write an error message if the text isn't found.
                if not pos:
                    self.__write_output(u'Error: Can\'t find: {0} {1}'.format(ent_seq, pos_text))

            if tag == 'gloss' and action == 'start':
                gloss = elem.text

                lang = 'eng'
                keys = elem.keys()

                # Should have 0 or 1
                # This is easier than calling the namespace directly
                if len(keys) > 0:
                    lang = elem.get(keys[0])

                entry.glosses.append(Gloss(gloss, pos, lang))

            # Not entirely sure this is even necessary...
            if tag == 'sense' and action == 'end':
                pass

            if tag == 'entry' and action == 'end':
                entries.append(entry)

        self.__write_output(u'done reading')

        return entries

