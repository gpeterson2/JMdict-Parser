#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
    Misc,
    PartOfSpeech,
    Session,
    init_model,
)


class JMdictDataSqlBase(unittest.TestCase):

    def setUp(self):
        super(JMdictDataSqlBase, self).setUp()

        self.connection_string = os.path.join(tempfile.tempdir, 'test.db')

        uri = 'sqlite:///{0}'.format(self.connection_string)
        self.meta = init_model(uri)
        self.meta.create_all()

        self.session = Session()

        self.xml = '''<?xml version="1.0" encoding="UTF-8"?>
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

        # TODO - test this as well
        # <entry>
        #     <ent_seq>1000260</ent_seq>
        #     <k_ele>
        #         <keb>悪どい</keb>
        #         <ke_inf>&iK;</ke_inf>
        #     </k_ele>
        #     <r_ele>
        #         <reb>あくどい</reb>
        #     </r_ele>
        #     <sense>
        #         <pos>&adj-i;</pos>
        #         <misc>&uk;</misc>
        #         <gloss>gaudy</gloss>
        #         <gloss>showy</gloss>
        #         <gloss>excessive</gloss>
        #     </sense>
        #     <sense>
        #         <gloss>crooked</gloss>
        #         <gloss>vicious</gloss>
        #         <gloss xml:lang="ger">aufgedonnert</gloss>
        #         <gloss xml:lang="ger">schreiend</gloss>
        #         <gloss xml:lang="ger">grell</gloss>
        #         <gloss xml:lang="ger">aufgeputzt</gloss>
        #         <gloss xml:lang="ger">schwer</gloss>
        #     </sense>
        #     <sense>
        #         <gloss xml:lang="ger">übel</gloss>
        #         <gloss xml:lang="ger">schlimm</gloss>
        #         <gloss xml:lang="ger">arglistig</gloss>
        #     </sense>
        #     <sense>
        #         <gloss xml:lang="ger">ermüdend</gloss>
        #     </sense>
        # </entry>

    def tearDown(self):
        self.meta.drop_all()

        os.remove(self.connection_string)


# TODO - update to use sqlachemy
class TestEntry(JMdictDataSqlBase):

    def test_write_entries(self):
        entries = Parser().parse_from_string(self.xml)

        viewer = ConsoleViewer()
        writer = SqliteWriter(self.connection_string)
        writer.attach(viewer)
        writer.write_entries(entries)

        results = self.session.query(Entry).all()

        assert len(results) == 1
        assert results[0].ent_seq == 1000050

    def test_write_parts_of_speech(self):
        viewer = ConsoleViewer()
        writer = SqliteWriter(self.connection_string)
        writer.attach(viewer)

        writer.write_parts_of_speech(PARTS_OF_SPEECH)

        results = self.session.query(PartOfSpeech).all()

        # TODO - add more tests
        assert len(results) > 1

    def test_write_kanas(self):
        entries = Parser().parse_from_string(self.xml)

        viewer = ConsoleViewer()
        writer = SqliteWriter(self.connection_string)
        writer.attach(viewer)

        kanas, _, _, _, _ = writer.split_entries(entries)

        writer.write_kanas(kanas)

        results = self.session.query(KanaElement).all()

        assert len(results) == 1
        assert results[0].kana == 'どうじょう'

    # TODO - actually test this.
    def test_write_miscs(self):
        entries = Parser().parse_from_string(self.xml)

        viewer = ConsoleViewer()
        writer = SqliteWriter(self.connection_string)
        writer.attach(viewer)

        _, _, _, _, miscs = writer.split_entries(entries)

        writer.write_miscs(miscs)

        results = self.session.query(Misc).all()

        assert len(results) == 0
        # assert results[0].misc == ''

    def test_write_kanjis(self):
        entries = Parser().parse_from_string(self.xml)

        viewer = ConsoleViewer()
        writer = SqliteWriter(self.connection_string)
        writer.attach(viewer)

        _, kanjis, _, _, _ = writer.split_entries(entries)

        writer.write_kanjis(kanjis)

        results = self.session.query(KanjiElement).all()

        assert len(results) == 1
        assert results[0].kanji == '仝'

    # FIXME - this should actually include a "Sense" element with multiple
    # glosses under it.
    def test_write_glosses(self):
        entries = Parser().parse_from_string(self.xml)

        viewer = ConsoleViewer()
        writer = SqliteWriter(self.connection_string)
        writer.attach(viewer)

        _, _, _, glosses, _ = writer.split_entries(entries)

        writer.write_glosses(glosses)

        results = self.session.query(Gloss).order_by(Gloss.lang).all()

        # FIXME - when sense is available add check for pos.

        assert len(results) == 2
        assert results[0].lang == 'eng'
        assert results[0].gloss == '"as above" mark'

        assert results[1].lang == 'ger'
        assert results[1].gloss == 'Abkürzung für "siehe oben"'
