#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from jmdict.parser.jmdict import Parser, Entry, Gloss

class TestJmdictParser(unittest.TestCase):
    def test_entry_to_string(self):
        entry_seq = 1
        kanas = [u'どうじょう']
        kanjis = [u'仝']
        glosses = [
            Gloss(u'"as above" mark', u'noun', u'eng'),
            Gloss(u'Abkürzung für "siehe oben"', u'noun', u'ger'),
        ]

        e = Entry(entry_seq, kanas, kanjis, glosses)

        expected = u'1 [どうじょう] [仝] "as above" mark,Abkürzung für "siehe oben"'
        result = unicode(e)

        #for g in glosses:
            #print(g.gloss)

        self.assertEqual(expected, result)

    def test_gloss_to_string(self):
        gloss = u'"as above" mark',
        pos = u'noun'
        lang = u'eng'

        g = Gloss(gloss, pos, lang)

        self.assertEqual(g.gloss, gloss)
        self.assertEqual(g.pos, pos)
        self.assertEqual(g.lang, lang)

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
        expected.glosses = [
            Gloss(u'"as above" mark', u'noun (common) (futsuumeishi)', u'eng'),
            Gloss(u'Abkürzung für "siehe oben"', u'noun (common) (futsuumeishi)', u'ger'),
        ]

        results = Parser().parse_from_string(xml)
        result = results[0]

        self.assertEqual(int(expected.entry_seq), int(result.entry_seq))
        self.assertEqual(expected.kanas, result.kanas)
        self.assertEqual(expected.kanjis, result.kanjis)

        self.assertEqual(expected.glosses[0].gloss, result.glosses[0].gloss)
        self.assertEqual(expected.glosses[0].lang, result.glosses[0].lang)
        self.assertEqual(expected.glosses[0].pos, result.glosses[0].pos)

        self.assertEqual(expected.glosses[1].gloss, result.glosses[1].gloss)
        self.assertEqual(expected.glosses[1].lang, result.glosses[1].lang)
        self.assertEqual(expected.glosses[1].pos, result.glosses[1].pos)

if __name__ == '__main__':
    unittest.main()
