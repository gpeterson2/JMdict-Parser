#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
        gloss_entries = [] # Not sure you really need a "sense" entry...

        # really stupid idea...athough inserting an id works with sqlite.
        # basically doing it to make defining join tables easier.
        # 0 so that the value can be incremented first off and stay the same
        # throuhout the life of the entry element...it feels so bad to depend
        # on what are practically global values...oh well.
        entry_id = 0
        gloss_id = 0
        kana_id = 0
        kanji_id = 0

        kana_dict = {}
        kanji_dict = {}
        gloss_dict = {}

        for i, (action, elem) in enumerate(context):

            tag = elem.tag
            text = elem.text
            if not text:
                continue

            if tag == 'ent_seq' and action == 'start':
                ent_seq = elem.text

                entry_id += 1
                entries.append((entry_id, ent_seq))

            if tag == 'reb' and action == 'start':

                kana = elem.text

                if kana in kana_dict:
                    kana_entries.append((entry_id, kana_dict[kana]))
                else:
                    kana_id += 1
                    kana_dict[kana] = kana_id

                if entry_id == 33775:
                    print(kana.encode('utf-8'))
                    print(kana_id)
                    print(kana_dict[kana])

            if tag == 'keb' and action == 'start':

                kanji = elem.text

                if kanji in kanji_dict:
                    kanji_entries.append((entry_id, kanji_dict[kanji]))
                else:
                    kanji_id += 1
                    kanji_dict[kanji] = kanji_id
                    #if u'上' in unicode(kanji):
                        #print(kanji.encode('utf-8'))

            if tag == 'sense' and action == 'start':
                pass

            if tag == 'pos' and action == 'start':
                pos = None

                # Used in gloss
                pos_text = elem.text
                pos = pos_dict.get(pos_text, '')
                # Shouldn't happen, of course...
                #print('Can\'t find: %s %s' % (ent_seq, pos_text))

            if tag == 'gloss' and action == 'start':
                gloss = elem.text

                lang = 'eng'
                keys = elem.keys()

                # Should have 0 or 1
                if len(keys) > 0:
                    # This is easier than calling the namespace directly
                    lang = elem.get(keys[0])

                if gloss:
                    gloss_id += 1
                    gloss = gloss.replace('"', '""'); 
                    glosses.append((gloss_id, gloss, pos, lang))
                    gloss_entries.append((entry_id, gloss_id))

            # Not entirely sure this is even necessary...
            if tag == 'sense' and action == 'end':
                pass

            if tag == 'entry' and action == 'end':
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

        table = "create table entry ( id integer primary key, entry );"
        sql = "insert into entry(id, entry) values(?, ?);"
        self.write_from_list(conn, entries, sql, table)
            
        table = "create table kana ( id integer primary key, kana varchar );"
        sql = "insert into kana(id, kana) values(?, ?)"
        # blah
        kanas = [(v, k) for (k, v) in kana_dict.items()]
        kanas.sort(lambda x, y: x[0] - y[0])
        self.write_from_list(conn, kanas, sql, table)

        table = "create table kanji ( id integer primary key, kanji varchar );"
        sql = "insert into kanji(id, kanji) values(?, ?);"
        kanjis = [(v, k) for (k, v) in kanji_dict.items()]
        kanjis.sort(lambda x, y: x[0] - y[0])
        self.write_from_list(conn, kanjis, sql, table)

        table = "create table gloss ( id integer primary key, gloss varchar, pos, lang varchar );"
        sql = "insert into gloss(id, gloss, pos, lang) values(?, ?, ?, ?);"
        self.write_from_list(conn, glosses, sql, table)

        # Join tables
        table = "create table kana_entry ( entry_id varchar, kana_id varchar );"
        sql = "insert into kana_entry(entry_id, kana_id) values(?, ?);"
        self.write_from_list(conn, kana_entries, sql, table)

        table = "create table kanji_entry ( entry_id varchar, kanji_id varchar );"
        sql = "insert into kanji_entry(entry_id, kanji_id) values(?, ?);"
        self.write_from_list(conn, kanji_entries, sql, table)

        table = "create table gloss_entry ( entry_id, gloss_id );"
        sql = """insert into gloss_entry(entry_id, gloss_id) values(?, ?);"""
        self.write_from_list(conn, gloss_entries, sql, table)

        cur = conn.cursor()
        sql = """
            create view list_all as
            select entry.entry, kana.kana, kanji.kanji
            from entry
            join kana_entry on entry.id = kana_entry.entry_id
            join kanji_entry on entry.id = kanji_entry.entry_id
            left join kana on kana_entry.kana_id = kana.id
            left join kanji on kanji_entry.kanji_id = kanji.id;
        """
        cur.execute(sql)
        conn.commit()

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

