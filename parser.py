#! /usr/bin/env python

import codecs
import os
import sqlite3

from lxml import etree

class Parser(object):

    def __init__(self, infile):
        self.infile = infile

    def parse(self):

        xml = open(self.infile, 'r')

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events)

        # Set up the parts of speach, as I don't think there's
        # a way to read them directly from the file...
        pos_dict = self.insert_parts_of_speech()

        entries = []
        kanas = set()
        kana_entries = []
        kanjis = set()
        kanji_entries = []
        glosses = []

        for i, (action, elem) in enumerate(context):

            tag = elem.tag

            #if tag == 'entry' and action == 'start':
                #entry = Entry()
                #ses.begin()

            if tag == 'ent_seq' and action == 'start':
                ent_seq = elem.text
                if ent_seq:
                    entries.append(ent_seq)

            if tag == 'reb' and action == 'start':

                kana = elem.text
                if kana and not kana in kanas:
                    kanas.add(kana)
                    kana_entries.append((ent_seq, kana))

            if tag == 'keb' and action == 'start':

                kanji = elem.text
                if kanji and not kanji in kanjis:
                    kanjis.add(kanji)
                    kanji_entries.append((ent_seq, kanji))

                #entry.kanji.append(kanji)

            if tag == 'sense' and action == 'start':
                #sense = Sense();
                pass

            if tag == 'pos' and action == 'start':
                pos = None

                pos_text = elem.text
                if pos_text:
                    try:
                        pos = pos_dict[pos_text]
                    except KeyError:
                        # Shouldn't happen, of course...
                        print('%s %s' % (ent_seq, pos_text))

                #sense.pos.append(pos)

            if tag == 'gloss' and action == 'start':
                gloss = elem.text

                lang = 'eng'
                keys = elem.keys()
                # Should have 0 or 1
                if len(keys) > 0:
                    # Not calling directly because it's a full namespace
                    # this is easier
                    lang = elem.get(keys[0])

                if gloss:
                    gloss = gloss.replace('"', '""'); 
                    glosses.append((gloss, lang))

                #sense.gloss.append(gloss)

            if tag == 'sense' and action == 'end':
                #entry.sense.append(sense)
                pass

            if tag == 'entry' and action == 'end':
                # to make testing easier
                #if i > 1000:
                    #break
                pass

        connection_string = 'test.db'
        if os.path.exists(connection_string):
            os.remove(connection_string)
        conn = sqlite3.connect(connection_string)

        cur = conn.cursor()

        # Unique tables
        table = "create table part_of_speach ( code varchar, text varchar);"
        sql = 'insert into part_of_speach(code, text) values(?, ?);'
        poss = [(v, k.replace("'", "\'")) for k, v in pos_dict.items()]
        self.write_from_list(conn, poss, sql, table)

        table = "create table entry ( entry );"
        sql = "insert into entry(entry) values(?);"
        # Was trying to iterate over text...
        self.write_from_list(conn, [(e,) for e in entries], sql, table)
            
        table = "create table kana ( kana varchar );"
        sql = "insert into kana(kana) values(?)"
        # Was trying to iterate over text...
        self.write_from_list(conn, [(k,) for k in kanas], sql, table)

        table = "create table kanji ( kanji varchar );"
        sql = "insert into kanji(kanji) values(?);"
        # Was trying to iterate over text...
        self.write_from_list(conn, [(k,) for k in kanjis], sql, table)

        table = "create table gloss ( gloss varchar, lang varchar );"
        sql = "insert into gloss(gloss, lang) values(?, ?);"
        self.write_from_list(conn, glosses, sql, table)

        # Join tables
        table = "create table kana_entry ( entry_id varchar, kana_id varchar );"
        sql = "insert into kana_entry(entry_id, kana_id) values(?, ?);"
        self.write_from_list(conn, kana_entries, sql, table)

        table = "create table kanji_entry ( entry_id varchar, kanji_id varchar );"
        sql = "insert into kanji_entry(entry_id, kanji_id) values(?, ?);"
        self.write_from_list(conn, kanji_entries, sql, table)

        conn.close()

    def write_from_list(self, conn, items, sql, table_sql=None):
        cur = conn.cursor()

        if table_sql:
            cur.execute(table_sql)

        try:
            cur.executemany(sql, items)
        except Exception as e:
            print('%s\n\n%s' % (table_sql, e))

        conn.commit()

    def insert_parts_of_speech(self):
        ''' Inserts parts of speach codes/text.

            These are in the xml file, but not easy to get at, so it 
            makes some sense to hardcode them here
        '''

        poss = [
            ('MA', 'martial arts term'),
            ('X', 'rude or X-rated term (not displayed in educational software)'),
            ('abbr', 'abbreviation'),
            ('adj-i', 'adjective (keiyoushi)'),
            ('adj-na', 'adjectival nouns or quasi-adjectives (keiyodoshi)'),
            ('adj-no', "nouns which may take the genitive case particle `no'"),
            ('adj-pn', 'pre-noun adjectival (rentaishi)'),
            ('adj-t', "`taru' adjective"),
            ('adj-f', 'noun or verb acting prenominally'),
            ('adj', 'former adjective classification (being removed)'),
            ('adv', 'adverb (fukushi)'),
            ('adv-to', "adverb taking the `to' particle"),
            ('arch', 'archaism'),
            ('ateji', 'ateji (phonetic) reading'),
            ('aux', 'auxiliary'),
            ('aux-v', 'auxiliary verb'),
            ('aux-adj', 'auxiliary adjective'),
            ('Buddh', 'Buddhist term'),
            ('chem', 'chemistry term'),
            ('chn', "children's language"),
            ('col', 'colloquialism'),
            ('comp', 'computer terminology'),
            ('conj', 'conjunction'),
            ('ctr', 'counter'),
            ('derog', 'derogatory'),
            ('eK', 'exclusively kanji'),
            ('ek', 'exclusively kana'),
            ('exp', 'Expressions (phrases, clauses, etc.)'),
            ('fam', 'familiar language'),
            ('fem', 'female term or language'),
            ('food', 'food term'),
            ('geom', 'geometry term'),
            ('gikun', 'gikun (meaning as reading)  or jukujikun (special kanji reading)'),
            ('hon', 'honorific or respectful (sonkeigo) language'),
            ('hum', 'humble (kenjougo) language'),
            ('iK', 'word containing irregular kanji usage'),
            ('id', 'idiomatic expression'),
            ('ik', 'word containing irregular kana usage'),
            ('int', 'interjection (kandoushi)'),
            ('io', 'irregular okurigana usage'),
            ('iv', 'irregular verb'),
            ('ling', 'linguistics terminology'),
            ('m-sl', 'manga slang'),
            ('male', 'male term or language'),
            ('male-sl', 'male slang'),
            ('math', 'mathematics'),
            ('mil', 'military'),
            ('n', 'noun (common) (futsuumeishi)'),
            ('n-adv', 'adverbial noun (fukushitekimeishi)'),
            ('n-suf', 'noun, used as a suffix'),
            ('n-pref', 'noun, used as a prefix'),
            ('n-t', 'noun (temporal) (jisoumeishi)'),
            ('num', 'numeric'),
            ('oK', 'word containing out-dated kanji'),
            ('obs', 'obsolete term'),
            ('obsc', 'obscure term'),
            ('ok', 'out-dated or obsolete kana usage'),
            ('on-mim', 'onomatopoeic or mimetic word'),
            ('pn', 'pronoun'),
            ('poet', 'poetical term'),
            ('pol', 'polite (teineigo) language'),
            ('pref', 'prefix'),
            ('prt', 'particle'),
            ('physics', 'physics terminology'),
            ('rare', 'rare'),
            ('sens', 'sensitive'),
            ('sl', 'slang'),
            ('suf', 'suffix'),
            ('uK', 'word usually written using kanji alone'),
            ('uk', 'word usually written using kana alone'),
            ('v1', 'Ichidan verb'),
            ('v2a-s', 'Nidan verb with 'u' ending (archaic)'),
            ('v4h', "Yondan verb with `hu/fu' ending (archaic)"),
            ('v4r', "Yondan verb with `ru' ending (archaic)"),
            ('v5', 'Godan verb (not completely classified)'),
            ('v5aru', 'Godan verb - -aru special class'),
            ('v5b', "Godan verb with `bu' ending"),
            ('v5g', "Godan verb with `gu' ending"),
            ('v5k', "Godan verb with `ku' ending"),
            ('v5k-s', "Godan verb - Iku/Yuku special class"),
            ('v5m', "Godan verb with `mu' ending"),
            ('v5n', "Godan verb with `nu' ending"),
            ('v5r', "Godan verb with `ru' ending"),
            ('v5r-i', "Godan verb with `ru' ending (irregular verb)"),
            ('v5s', "Godan verb with `su' ending"),
            ('v5t', "Godan verb with `tsu' ending"),
            ('v5u', "Godan verb with `u' ending"),
            ('v5u-s', "Godan verb with `u' ending (special class)"),
            ('v5uru', "Godan verb - Uru old class verb (old form of Eru)"),
            ('v5z', "Godan verb with `zu' ending"),
            ('vz', 'Ichidan verb - zuru verb (alternative form of -jiru verbs)'),
            ('vi', 'intransitive verb'),
            ('vk', 'Kuru verb - special class'),
            ('vn', 'irregular nu verb'),
            ('vr', 'irregular ru verb, plain form ends with -ri'),
            ('vs', 'noun or participle which takes the aux. verb suru'),
            ('vs-s', 'suru verb - special class'),
            ('vs-i', 'suru verb - irregular'),
            ('kyb', 'Kyoto-ben'),
            ('osb', 'Osaka-ben'),
            ('ksb', 'Kansai-ben'),
            ('ktb', 'Kantou-ben'),
            ('tsb', 'Tosa-ben'),
            ('thb', 'Touhoku-ben'),
            ('tsug', 'Tsugaru-ben'),
            ('kyu', 'Kyuushuu-ben'),
            ('rkb', 'Ryuukyuu-ben'),
            ('nab', 'Nagano-ben'),
            ('vt', 'transitive verb'),
            ('vulg', 'vulgar expression or word'),
        ]

        return dict([(text, code) for code, text in poss])

