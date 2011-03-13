#! /usr/bin/env python

import codecs
import os
import sqlite3

def write_from_list(conn, items, sql, table_sql=None):
    ''' General function to write lists of items to table.

        Optionally creates a table as well.

        :param conn: The connection object
        :param items: A list of type items to write.
        :param sql: The sql statement to run.
        :param table_sql: SQL statement to create a table if necessary.
    '''

    cur = conn.cursor()

    if table_sql:
        cur.execute(table_sql)

    try:
        cur.executemany(sql, items)
    except Exception as e:
        print('%s\n\n%s' % (table_sql, e))

    conn.commit()

def get_parts_of_speach():
    ''' Gets parts of speach codes/text.

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

def convert_to_tuple_list(items):
    ''' Converts single item lists to list of tuples.

        A convience function.
        
        :param items: A list of items to convert.
    '''
    return [(i,) for i in items]

def create_dict_from_sql(conn, sql):
    ''' For the given sql returns an entry/id dictionary
        
        Convience function - Basically to allow searching for id's based on 
        items.

        The sql statemen should be in the form of:
        SELECT id, item FROM table
    '''
    cur = conn.cursor()
    cur.execute(sql)

    d = {}
    for row in cur.fetchall():
        id = row[0]
        entry = row[1]
        d[entry] = id

    return d

# TODO - this should probably be an object which can be sub classed.
# So that it can more easily be switched between database types.
# Or it should use an ORM, which was the original plan before running
# it meant waiting three hours...
def write_list_to_database(parsed_object):
    ''' Writes the various lists to a database. 
    
        :param parsed_object: An object containing lists of items to insert.
        Entries - the dictionary entries.
        kanas - list of unique kana entries.
        kanji - list of unique kanji entires.
        glosses - list of unique translation entries.
    '''

    connection_string = 'test.db'

    if os.path.exists(connection_string):
        os.remove(connection_string)

    conn = sqlite3.connect(connection_string)

    cur = conn.cursor()

    # Unique tables
    pos_dict = get_parts_of_speach()

    table = "create table part_of_speach ( code varchar, text varchar);"
    sql = 'insert into part_of_speach(code, text) values(?, ?);'
    poss = [(v, k.replace("'", "\'")) for k, v in pos_dict.items()]
    write_from_list(conn, poss, sql, table)

    table = "create table entry ( id integer primary key, entry );"
    sql = "insert into entry(entry) values(?);"
    items = [(i.entry_seq,) for i in parsed_object.entries]
    write_from_list(conn, items, sql, table)
        
    table = "create table kana ( id integer primary key, kana varchar );"
    sql = "insert into kana(kana) values(?)"
    items = convert_to_tuple_list(parsed_object.kanas)
    write_from_list(conn, items, sql, table)

    table = "create table kanji ( id integer primary key, kanji varchar );"
    sql = "insert into kanji(kanji) values(?);"
    items = convert_to_tuple_list(parsed_object.kanjis)
    write_from_list(conn, items, sql, table)

    table = "create table gloss ( id integer primary key, gloss varchar, pos, lang varchar );"
    sql = "insert into gloss(gloss, pos, lang) values(?, ?, ?);"
    items = parsed_object.glosses
    write_from_list(conn, items, sql, table)

    table = "create table warehouse (id integer primary key, entry int, kana varchar, kanji varchar, gloss varchar); "
    sql = "insert into warehouse(entry, kana, kanji, gloss) values(?, ?, ?, ?)"
    items = [
        (
            entry.entry_seq, 
            u','.join(entry.kanas),
            u','.join(entry.kanjis), 
            u','.join([g for g in entry.glosses])
        ) 
        for entry in parsed_object.entries]
    write_from_list(conn, items, sql, table)

    # Join tables
    sql = "select id, entry from entry"
    entry_dict = create_dict_from_sql(conn, sql) 

    sql = "select id, kana from kana"
    kana_dict = create_dict_from_sql(conn, sql) 

    items = []
    for entry in parsed_object.entries:
        for kana in entry.kanas:
            items.append((entry_dict.get(entry.entry_seq, 0), kana_dict.get(kana, 0)))

    table = "create table kana_entry ( entry_id varchar, kana_id varchar );"
    sql = "insert into kana_entry(entry_id, kana_id) values(?, ?);"
    write_from_list(conn, items, sql, table)

    sql = "select id, kanji from kanji"
    kanji_dict = create_dict_from_sql(conn, sql)

    items = []
    for entry in parsed_object.entries:
        for kana in entry.kanjis:
            items.append((entry_dict.get(entry.entry_seq, 0), kanji_dict.get(kana, 0)))

    table = "create table kanji_entry (entry_id varchar, kanji_id varchar );"
    sql = "insert into kanji_entry(entry_id, kanji_id) values(?, ?);"
    write_from_list(conn, items, sql, table)

    #table = "create table gloss_entry ( entry_id, gloss_id );"
    #sql = """insert into gloss_entry(entry_id, gloss_id) values(?, ?);"""
    #write_from_list(conn, gloss_entries, sql, table)

    cur = conn.cursor()
    sql = """
        create view list_all as
        select 
            entry.entry, 
            kana.id as kana_id,
            kana.kana, 
            kanji.id as kanji_id,
            kanji.kanji
        from 
            entry
            join kana_entry 
                on entry.id = kana_entry.entry_id
            join kanji_entry 
                on entry.id = kanji_entry.entry_id
            left join kana 
                on kana_entry.kana_id = kana.id
            left join kanji 
                on kanji_entry.kanji_id = kanji.id;
    """
    cur.execute(sql)
    conn.commit()

    conn.close()

