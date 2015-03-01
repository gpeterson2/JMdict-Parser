#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from kanjidic2.parser import Parser, Kanji, Reading, Meaning


class TestJmdictParser(unittest.TestCase):

    def test_from_string(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <kanjidic2>
                <!-- Entry for Kanji: 亜 -->
                <character>
                    <literal>亜</literal>
                    <codepoint>
                        <cp_value cp_type="ucs">4e9c</cp_value>
                        <cp_value cp_type="jis208">16-01</cp_value>
                    </codepoint>
                    <radical>
                        <rad_value rad_type="classical">7</rad_value>
                        <rad_value rad_type="nelson_c">1</rad_value>
                    </radical>
                    <misc>
                        <grade>8</grade>
                        <stroke_count>7</stroke_count>
                        <variant var_type="jis208">48-19</variant>
                        <freq>1509</freq>
                        <jlpt>1</jlpt>
                    </misc>
                    <dic_number>
                        <dic_ref dr_type="nelson_c">43</dic_ref>
                        <dic_ref dr_type="nelson_n">81</dic_ref>
                        <dic_ref dr_type="halpern_njecd">3540</dic_ref>
                        <dic_ref dr_type="halpern_kkld">2204</dic_ref>
                        <dic_ref dr_type="heisig">1809</dic_ref>
                        <dic_ref dr_type="gakken">1331</dic_ref>
                        <dic_ref dr_type="oneill_names">525</dic_ref>
                        <dic_ref dr_type="oneill_kk">1788</dic_ref>
                        <dic_ref dr_type="moro" m_vol="1" m_page="0525">272</dic_ref>
                        <dic_ref dr_type="henshall">997</dic_ref>
                        <dic_ref dr_type="sh_kk">1616</dic_ref>
                        <dic_ref dr_type="jf_cards">1032</dic_ref>
                        <dic_ref dr_type="tutt_cards">1092</dic_ref>
                        <dic_ref dr_type="kanji_in_context">1818</dic_ref>
                        <dic_ref dr_type="kodansha_compact">35</dic_ref>
                        <dic_ref dr_type="maniette">1827</dic_ref>
                    </dic_number>
                    <query_code>
                        <q_code qc_type="skip">4-7-1</q_code>
                        <q_code qc_type="sh_desc">0a7.14</q_code>
                        <q_code qc_type="four_corner">1010.6</q_code>
                        <q_code qc_type="deroo">3273</q_code>
                    </query_code>
                    <reading_meaning>
                        <rmgroup>
                            <reading r_type="pinyin">ya4</reading>
                            <reading r_type="korean_r">a</reading>
                            <reading r_type="korean_h">아</reading>
                            <reading r_type="ja_on">ア</reading>
                            <reading r_type="ja_kun">つ.ぐ</reading>
                            <meaning>Asia</meaning>
                            <meaning>rank next</meaning>
                            <meaning>come after</meaning>
                            <meaning>-ous</meaning>
                            <meaning m_lang="fr">Asie</meaning>
                            <meaning m_lang="fr">suivant</meaning>
                            <meaning m_lang="fr">sub-</meaning>
                            <meaning m_lang="fr">sous-</meaning>
                            <meaning m_lang="es">pref. para indicar</meaning>
                            <meaning m_lang="es">venir después de</meaning>
                            <meaning m_lang="es">Asia</meaning>
                            <meaning m_lang="pt">Ásia</meaning>
                            <meaning m_lang="pt">próxima</meaning>
                            <meaning m_lang="pt">o que vem depois</meaning>
                            <meaning m_lang="pt">-ous</meaning>
                        </rmgroup>
                        <nanori>や</nanori>
                        <nanori>つぎ</nanori>
                        <nanori>つぐ</nanori>
                    </reading_meaning>
                </character>
            </kanjidic2>
        '''

        expected = Kanji()
        expected.literal = u'亜'
        expected.grade = u'8'
        expected.stroke_count = u'7'
        expected.freq = u'1509'
        expected.jlpt = u'1'

        readings = [
            (u'pinyin', u'ya4'),
            (u'korean_r', u'a'),
            (u'korean_h', u'아'),
            (u'ja_on', u'ア'),
            (u'ja_kun', u'つ.ぐ'),
        ]
        for r_type, reading in readings:
            r = Reading(reading=reading, r_type=r_type)
            expected.readings.append(r)

        meanings = [
            (None, u'Asia'),
            (None, u'rank next'),
            (None, u'come after'),
            (None, u'-ous'),
            (u'fr', u'Asie'),
            (u'fr', u'suivant'),
            (u'fr', u'sub-'),
            (u'fr', u'sous-'),
            (u'es', u'pref. para indicar'),
            (u'es', u'venir después de'),
            (u'es', u'Asia'),
            (u'pt', u'Ásia'),
            (u'pt', u'próxima'),
            (u'pt', u'o que vem depois'),
            (u'pt', u'-ous'),
        ]
        for m_lang, meaning in meanings:
            m = Meaning(meaning=meaning, m_lang=m_lang)
            expected.meanings.append(m)

        results = Parser().parse_from_string(xml)
        result = results[0]

        assert expected.literal == result.literal
        assert expected.grade == result.grade
        assert expected.stroke_count == result.stroke_count
        assert expected.freq == result.freq
        assert expected.jlpt == result.jlpt

        # TODO - check more of these.
        assert len(expected.readings) == len(result.readings)

        assert len(expected.meanings) == len(result.meanings)

if __name__ == '__main__':
    unittest.main()
