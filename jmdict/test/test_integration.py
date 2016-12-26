#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from jmdict.parser.jmdict import Parser, Entry, Gloss, Sense


class TestJmdictParser(unittest.TestCase):

    def test_entry_to_string(self):
        entry_seq = 1
        kanas = [u'どうじょう']
        kanjis = [u'仝']

        sense = Sense()
        sense.glosses = [
            Gloss(u'"as above" mark', u'noun', u'eng'),
            Gloss(u'Abkürzung für "siehe oben"', u'noun', u'ger'),
        ]
        senses = [sense]

        e = Entry(entry_seq, kanas, kanjis, senses)

        expected = u'1 [どうじょう] [仝] "as above" mark,Abkürzung für "siehe oben"'
        result = str(e)

        assert expected == result

    def test_gloss_to_string(self):
        gloss = u'"as above" mark',
        lang = u'eng'

        g = Gloss(gloss=gloss, lang=lang)

        assert g.gloss == gloss
        assert g.lang == lang

    def test_from_string(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE JMdict [
            <!ENTITY n "noun (common) (futsuumeishi)">
            ]>
            <JMdict>
                <entry>
                    <ent_seq>1000050</ent_seq>
                    <k_ele>
                        <keb>仝</keb>
                    </k_ele>
                    <r_ele>
                        <reb>どうじょう</reb>
                    </r_ele>
                    <sense>
                        <pos>&n;</pos>
                        <gloss>"as above" mark</gloss>
                        <gloss xml:lang="ger">Abkürzung für "siehe oben"</gloss>
                    </sense>
                </entry>
            </JMdict>
        '''

        expected = Entry()
        expected.entry_seq = 1000050
        expected.kanas = [u'どうじょう']
        expected.kanjis = [u'仝']

        expected_sense = Sense()
        expected_sense.poses = [
            u'noun (common) (futsuumeishi)'
        ]
        expected_sense.glosses = [
            Gloss(gloss=u'"as above" mark', lang=u'eng'),
            Gloss(gloss=u'Abkürzung für "siehe oben"',  lang=u'ger'),
        ]
        expected.senses.append(expected_sense)

        results = Parser().parse_from_string(xml)
        result = results[0]

        assert int(expected.entry_seq) == int(result.entry_seq)
        assert expected.kanas == result.kanas
        assert expected.kanjis == result.kanjis

        sense = result.senses[0]

        parts_of_speech = sense.poses
        assert len(parts_of_speech) == 1
        assert expected_sense.poses[0] == parts_of_speech[0]

        glosses = expected_sense.glosses
        print(glosses)
        assert expected_sense.glosses[0].gloss == glosses[0].gloss
        assert expected_sense.glosses[0].lang == glosses[0].lang

        assert expected_sense.glosses[1].gloss == glosses[1].gloss
        assert expected_sense.glosses[1].lang == glosses[1].lang
