#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gzip

from lxml import etree

from jmdict.utils.observer import Subject

# TODO - for all this really accomplishes, I could find a xml to object project
# and just use that. Technically you could get away with making these dicts
# for the short term and only upgrading them when necssary.

class CodePoint(object):
    def __init__(self, cp_value=None, cp_type=None):
        self.cp_type = cp_type
        self.cp_value = cp_value

class Radical(object):
    def __init__(self, rad_value=None, rad_type=None):
        self.rad_type = rad_type
        self.rad_value = rad_value

class DictNumber(object):
    def __init__(self, dict_ref=None, dr_type=None):
        self.dict_ref = dict_ref
        self.dr_type = dr_type

class QueryCode(object):
    def __init__(self, q_code=None, qc_type=None):
        self.q_code = q_code
        self.qc_type = qc_type

class Reading(object):
    def __init__(self, reading=None, r_type=None):
        self.reading = reading
        self.r_type = r_type

class Meaning(object):
    def __init__(self, meaning=None, m_lang='en'):
        self.meaning = meaning
        self.m_lang = m_lang

class Nanori(object):
    def __init__(self, meaning=None, m_lang='en'):
        self.meaning = meaning
        self.m_lang = m_lang

class Kanji(object):
    def __init__(self, literal=None, codepoints=None, radicals=None,
                 grade=None, stroke_count=None, freq=None, jlpt=None,
                 dict_numbers=None, query_codes=None, readings=None,
                 meanings=None, nanoris=None):

        if not codepoints:
            codepoints = []

        if not radicals:
            radicals = []

        if not dict_numbers:
            dict_numbers = []

        if not query_codes:
            query_codes = []

        if not readings:
            readings = []

        if not meanings:
            meanings = []

        if not nanoris:
            nanoris = []

        self.literal = literal
        self.codepoints = codepoints
        self.radicals = radicals

        # TODO - to match xml thse should be in "misc", although not sure if I care
        self.grade = grade
        self.stroke_count = stroke_count
        self.freq = freq
        self.jlpt = jlpt

        self.dict_numbers = dict_numbers
        self.query_codes = query_codes
        self.readings = readings
        self.meanings = meanings
        self.nanoris = nanoris

    def __str__(self):
        return u'{}'.format(self.literal)

    def __repr__(self):
        return 'Kanji({})'.format(self.literal)

class Parser(Subject):
    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)

    def parse_from_file(self, path=None):
        ''' Parse a KanjiDic2 file from the given a filepath.

            :param path: Path to a file to read.
        '''

        f = None
        if path.endswith('.gz'):
            f = gzip.open(path, 'r')
        else:
            # assume xml
            f = open(path, 'r')
        return self.parse(f)

    def parse_from_string(self, data):
        ''' Parse a KanjiDic2 string.

            :params data: The string to read.
        '''

        from StringIO import StringIO
        xml = StringIO(data)

        return self.parse(xml)

    def parse(self, xml):
        ''' Performs the parsing of the file. '''

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events, encoding='utf-8')

        kanji = None
        kanjis = []

        self.notify(u'start reading')

        for i, (action, elem) in enumerate(context):
            tag = elem.tag
            text = elem.text

            if not text:
                continue

            if tag == 'character':
                if action == 'start':
                    kanji = Kanji()
                else:
                    kanjis.append(kanji)

            if action == 'start':
                if tag == 'literal':
                    kanji.literal = text

                if tag == 'cp_value':
                    cp_type = elem.get('cp_type', None)
                    cp = CodePoint(text, cp_type)
                    kanji.codepoints.append(cp)

                if tag == 'radical':
                    rad_type = elem.get('rad_type', None)
                    rad  = Radical(text, rad_type )
                    kanji.radicals.append(rad)

                if tag == 'grade':
                    kanji.grade = text

                if tag == 'stroke_count':
                    kanji.stroke_count = text

                if tag == 'freq':
                    kanji.freq = text

                if tag == 'jlpt':
                    kanji.jlpt = text

                if tag == 'dic_ref':
                    dr_type = elem.get('dr_type', None)
                    dn = DictNumber(text, dr_type)
                    kanji.dict_numbers.append(dn)

                if tag == 'q_code':
                    qc_type = elem.get('qc_type', None)
                    qc = QueryCode(text, qc_type)
                    kanji.dict_numbers.append(qc)

                if tag == 'reading':
                    r_type = elem.get('r_type', None)
                    reading = Reading(text, r_type)
                    kanji.readings.append(reading)

                if tag == 'meaning':
                    m_lang = elem.get('m_lang', 'en')
                    meaning = Meaning(text, m_lang)
                    kanji.meanings.append(meaning)

        self.notify(u'done reading')

        return kanjis

