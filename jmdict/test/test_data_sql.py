#! /usr/bin/env python
# -*- coding: utf-8 -*-

# TODO ke_inf

import os
import tempfile
import unittest

from jmdict.utils.observer import ConsoleViewer
from jmdict.parser.jmdict import Parser
from jmdict.data.parts_of_speech import PARTS_OF_SPEECH
from jmdict.data.sql.sqlite import SqliteWriter
from jmdict.data.sql.models import (
    Entry,
    Gloss,
    KanaElement,
    KanjiElement,
    PartOfSpeech,
    Session,
    init_model,
)


class JMdictDataSqlBase(unittest.TestCase):

    def setUp(self):
        super(JMdictDataSqlBase, self).setUp()

        self.connection_string = os.path.join(tempfile.tempdir, 'test.db')

        uri = 'sqlite:///{0}'.format(self.connection_string)
        echo = False
        self.meta = init_model(uri, echo=echo)
        self.meta.create_all()

        self.session = Session()

        viewer = ConsoleViewer()
        writer = SqliteWriter(self.connection_string)
        writer.attach(viewer)
        self.writer = writer

        self.xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE JMdict [
            <!ENTITY adj-i "adjective (keiyoushi)">
            <!ENTITY adj-t "`taru' adjective">
            <!ENTITY adv-to "adverb taking the `to' particle">
            <!ENTITY iK "word containing irregular kanji usage">
            <!ENTITY n "noun (common) (futsuumeishi)">
            <!ENTITY uK "word usually written using kanji alone">
            <!ENTITY uk "word usually written using kana alone">
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

                <entry>
                    <ent_seq>1000260</ent_seq>
                    <k_ele>
                        <keb>悪どい</keb>
                        <ke_inf>&iK;</ke_inf>
                    </k_ele>
                    <r_ele>
                        <reb>あくどい</reb>
                    </r_ele>
                    <sense>
                        <pos>&adj-i;</pos>
                        <misc>&uk;</misc>
                        <gloss>gaudy</gloss>
                        <gloss>showy</gloss>
                        <gloss>excessive</gloss>
                    </sense>
                    <sense>
                        <gloss>crooked</gloss>
                        <gloss>vicious</gloss>
                        <gloss xml:lang="ger">aufgedonnert</gloss>
                        <gloss xml:lang="ger">schreiend</gloss>
                        <gloss xml:lang="ger">grell</gloss>
                        <gloss xml:lang="ger">aufgeputzt</gloss>
                        <gloss xml:lang="ger">schwer</gloss>
                    </sense>
                    <sense>
                        <gloss xml:lang="ger">übel</gloss>
                        <gloss xml:lang="ger">schlimm</gloss>
                        <gloss xml:lang="ger">arglistig</gloss>
                    </sense>
                    <sense>
                        <gloss xml:lang="ger">ermüdend</gloss>
                    </sense>
                </entry>

                <entry>
                    <ent_seq>1005450</ent_seq>
                    <k_ele>
                        <keb>悄悄</keb>
                    </k_ele>
                    <k_ele>
                        <keb>悄々</keb>
                    </k_ele>
                    <r_ele>
                        <reb>しおしお</reb>
                    </r_ele>
                    <r_ele>
                        <reb>しょうしょう</reb>
                    </r_ele>
                    <r_ele>
                        <reb>すごすご</reb>
                    </r_ele>
                    <sense>
                        <pos>&adj-t;</pos>
                        <pos>&adv-to;</pos>
                        <misc>&uk;</misc>
                        <gloss>in low spirits</gloss>
                        <gloss>dejected</gloss>
                        <gloss>sad</gloss>
                        <gloss xml:lang="ger">bedrückt</gloss>
                        <gloss xml:lang="ger">niedergeschlagen</gloss>
                        <gloss xml:lang="ger">entmutigt</gloss>
                        <gloss xml:lang="ger">mutlos</gloss>
                        <gloss xml:lang="ger">verzagt</gloss>
                    </sense>
                </entry>
            </JMdict>
        '''

    def tearDown(self):
        self.meta.drop_all()

        os.remove(self.connection_string)


class TestEntry(JMdictDataSqlBase):

    def test_write_entries(self):
        entries = Parser().parse_from_string(self.xml)

        self.writer.write(entries)

        entry = self.session.query(Entry).first()

        assert entry.ent_seq == 1000050

        assert len(entry.kana) == 1
        assert entry.kana[0].kana == 'どうじょう'

        assert len(entry.kanji) == 1
        assert entry.kanji[0].kanji == '仝'

        assert len(entry.sense) == 1
        sense = entry.sense[0]

        assert len(sense.pos) == 1
        pos = sense.pos[0]

        assert pos.code == 'n'

        assert len(sense.gloss) == 2
        gloss1 = sense.gloss[0]
        gloss2 = sense.gloss[1]

        assert gloss1.lang == 'eng'
        assert gloss1.gloss == '"as above" mark'

        assert gloss2.lang == 'ger'
        assert gloss2.gloss == 'Abkürzung für "siehe oben"'

    def test_write_parts_of_speech(self):
        self.writer.write_parts_of_speech(PARTS_OF_SPEECH)

        results = self.session.query(PartOfSpeech).all()

        assert len(results) > 1

    def test_write_kanas(self):
        entries = Parser().parse_from_string(self.xml)

        kanas, _, _, _, _ = self.writer.split_entries(entries)

        self.writer.write_kanas(kanas)

        assert len(kanas) == self.session.query(KanaElement).count()

    def test_write_kanjis(self):
        entries = Parser().parse_from_string(self.xml)

        _, kanjis, _, _, _ = self.writer.split_entries(entries)

        self.writer.write_kanjis(kanjis)

        assert len(kanjis) == self.session.query(KanjiElement).count()

    def test_write_glosses(self):
        entries = Parser().parse_from_string(self.xml)

        _, _, _, glosses, _ = self.writer.split_entries(entries)

        self.writer.write_glosses(glosses)

        assert len(glosses) == self.session.query(Gloss).count()

    def test_write_entries_multiple_senses(self):
        entries = Parser().parse_from_string(self.xml)

        self.writer.write(entries)

        entry = self.session.query(Entry).filter(Entry.ent_seq==1000260).first()

        assert len(entry.sense) == 4
        senses = entry.sense

        sense1 = senses[0]
        assert len(sense1.pos) == 1
        assert len(sense1.misc) == 1
        assert len(sense1.gloss) == 3

    def test_write_entries_part_of_speech_normalization(self):
        entries = Parser().parse_from_string(self.xml)

        self.writer.write(entries)

        entry = self.session.query(Entry).filter(Entry.ent_seq==1005450).first()

        assert len(entry.sense) == 1
        sense = entry.sense[0]

        assert len(sense.pos) == 2

        pos1 = sense.pos[0]
        pos2 = sense.pos[1]

        assert pos1.code == 'adj-t'
        assert pos1.text == "'taru' adjective"

        assert pos2.code == 'adv-to'
        assert pos2.text == "adverb taking the 'to' particle"
