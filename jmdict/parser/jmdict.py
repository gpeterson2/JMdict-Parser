#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
from io import BytesIO

from lxml import etree

from jmdict.utils.observer import Subject

__all__ = ['Entry', 'Gloss', 'Parser']


class JmdictParserException(Exception):
    pass


# TODO - at the least it should also be moved to a separate location
class Entry(object):
    ''' An entry object.

        For a given entry contains all kana entries,
        all kanji entires, and all gloss entires.
    '''

    def __init__(self, entry_seq=0, kanas=None, kanjis=None, senses=None):

        if not kanas:
            kanas = []

        if not kanjis:
            kanjis = []

        if not senses:
            senses = []

        self.entry_seq = entry_seq
        self.kanas = kanas
        self.kanjis = kanjis
        self.senses = senses

    def __str__(self):
        glosses = []
        for sense in self.senses:
            for gloss in sense.glosses:
                glosses.append(gloss.gloss)

        return u'{0} [{1}] [{2}] {3}'.format(
            self.entry_seq,
            u','.join(self.kanas),
            u','.join(self.kanjis),
            u','.join(glosses),
        )

    def __repr__(self):
        return 'Entry({0}, {0}, {0}, {0})'.format(
            self.entry_seq,
            ','.join(repr(self.kanas)),
            ','.join(repr(self.kanjis)),
            ','.join(repr(self.senses.glosses))
        )


class Sense(object):
    ''' Object to contain gloss information. '''

    def __init__(self, poses=None, miscs=None, glosses=None):
        if not poses:
            poses = []

        if not miscs:
            miscs = []

        if not glosses:
            glosses = []

        self.poses = poses
        self.miscs = miscs
        self.glosses = glosses

    def __str__(self):
        return '{} {} {}'.format(
            u','.join(self.poses),
            u','.join(self.miscs),
            u','.join(self.glosses),
        )


class Gloss(object):
    ''' Object to contain translations.

        :param gloss: The translated text.
        :param pos: The part of speech for the entry.
        :param lang: The language of the translation.
    '''

    def __init__(self, gloss='', pos='', lang=''):
        self.gloss = gloss
        self.lang = lang

    def __str__(self):
        return u'{} {}'.format(self.gloss, self.lang)

    def __repr__(self):
        return "Gloss('{}', '{}')".format(self.gloss, self.lang)

    def __eq__(self, other):
        return self.gloss == other.gloss and self.lang == other.lang

    def __hash__(self):
        return hash(self.gloss + self.lang)


class Parser(Subject):

    def __init__(self, *args, **kwargs):
        ''' Reads a JMDict file.

            :params infile: The JMDict input file.
            :params message_out: An output stream for parsing messages,
                defaults to none.
        '''
        super(Parser, self).__init__(*args, **kwargs)

    def parse_from_file(self, path=None):
        ''' Parse a JMDict file from the given a filepath.

            :param path: Path to a file to read.
        '''

        f = None
        if path.endswith('.gz'):
            f = gzip.open(path, 'r')
        elif path.endswith('xml'):
            f = open(path, 'r')
        else:
            raise JmdictParserException('Invalid file type')

        return self.parse(f)

    def parse_from_string(self, data):
        ''' Parse a JMDict string.

            :params data: The string to read.
        '''

        xml = BytesIO(bytes(data, 'utf-8'))

        return self.parse(xml)

    def parse(self, xml):
        ''' Performs the parsing of the file. '''

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events, encoding='utf-8')

        entries = []

        self.notify(u'start reading')

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
                sense = Sense()

            if tag == 'misc' and action == 'start':
                sense.miscs.append(elem.text)

            # not used until it hits the gloss entry
            # FIXME - Can also contain "misc" element
            # FIXME - There can be mutliple "pos" elements
            #
            #
            #   ...
            #    <ent_seq>1000225</ent_seq>
            #   ...
            #    <sense>
            #    <pos>&adj-na;</pos>
            #    <pos>&adj-no;</pos>
            #    <misc>&uk;</misc>
            #    <gloss>plain</gloss>
            #    <gloss>frank</gloss>
            #    <gloss>candid</gloss>
            #    <gloss>open</gloss>
            #    <gloss>direct</gloss>
            #    <gloss>straightforward</gloss>
            #    <gloss>unabashed</gloss>
            #    <gloss>blatant</gloss>
            #    <gloss>flagrant</gloss>
            #    </sense>
            if tag == 'pos' and action == 'start':
                pos = elem.text.replace("`", "'")

                # Shouldn't happen, of course...
                # but write an error message if the text isn't found.
                if not pos:
                    self.notify(u'Error: Can\'t find: {0} {1}'.format(ent_seq, pos))
                else:
                    sense.poses.append(pos)

            if tag == 'gloss' and action == 'start':
                gloss = elem.text

                lang = 'eng'
                keys = elem.keys()

                # Should have 0 or 1
                # This is easier than calling the namespace directly
                if len(keys) > 0:
                    lang = elem.get(keys[0])

                sense.glosses.append(Gloss(gloss=gloss, lang=lang))

            if tag == 'sense' and action == 'end':
                entry.senses.append(sense)

            if tag == 'entry' and action == 'end':
                entries.append(entry)

        self.notify(u'done reading')

        return entries
