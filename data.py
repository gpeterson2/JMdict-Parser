#! /usr/bin/env python

import codecs
import os
import sqlite3

from observer import Subject

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

class Writer(Subject):
    def __init__(self, *args, **kwargs):
        super(Writer, self).__init__(*args, **kwargs)

    def write(self):
        pass

# TODO - this should probably be an object which can be sub classed.
# So that it can more easily be switched between database types.
# Or it should use an ORM, which was the original plan before running
# it meant waiting three hours...
class SqliteWriter(Writer):

    def write(self, entries):
        ''' Writes the various lists to a database.

            :param entries: A list of entries objects.
        '''

        self.notify('start saving')
        connection_string = 'test.db'

        if os.path.exists(connection_string):
            os.remove(connection_string)

        conn = sqlite3.connect(connection_string)

        cur = conn.cursor()

        # Unique tables

        # Need to pull this infromation out of the main list. Should be in a generic class,
        # or done while reading it - although I imaging that some writeable formats
        # won't need it.
        pos = set()
        kanas = set()
        kanjis = set()
        glosses = set()

        # TODO - this is taking far too much time, proably go back to getting this when reading.
        self.notify('start reading unique values')
        length = float(len(entries))
        for i, entry in enumerate(entries):
            #self.notify('{0}: {1:.0%}'.format(entry.entry_seq, i / length))
            for kana in entry.kanas:
                kanas.add(kana)

            for kanji in entry.kanjis:
                kanjis.add(kanji)

            for gloss in entry.glosses:
                pos.add(gloss.pos)
                glosses.add(gloss)

        # TODO - need to figure this out from what I'm passing in now.
        #table = "create table part_of_speach ( code varchar, text varchar);"
        #sql = 'insert into part_of_speach(code, text) values(?, ?);'
        #poss = [(v, k.replace("'", "\'")) for k, v in pos_dict.items()]
        #write_from_list(conn, poss, sql, table)

        self.notify('start writing entries')
        table = "create table entry ( id integer primary key, entry );"
        sql = "insert into entry(entry) values(?);"
        items = [(i.entry_seq,) for i in entries]
        write_from_list(conn, items, sql, table)

        self.notify('start writing kana')
        table = "create table kana ( id integer primary key, kana varchar );"
        sql = "insert into kana(kana) values(?)"
        items = convert_to_tuple_list(kanas)
        write_from_list(conn, items, sql, table)

        self.notify('start writing kanji')
        table = "create table kanji ( id integer primary key, kanji varchar );"
        sql = "insert into kanji(kanji) values(?);"
        items = convert_to_tuple_list(kanjis)
        write_from_list(conn, items, sql, table)

        self.notify('start writing glosses')
        table = "create table gloss ( id integer primary key, gloss varchar, pos, lang varchar );"
        sql = "insert into gloss(gloss, pos, lang) values(?, ?, ?);"
        items = [(g.gloss, g.pos, g.lang) for g in glosses]
        write_from_list(conn, items, sql, table)

        self.notify('start writing warehouse')
        table = "create table warehouse (id integer primary key, entry int, kana varchar, kanji varchar, gloss varchar); "
        sql = "insert into warehouse(entry, kana, kanji, gloss) values(?, ?, ?, ?)"
        items = [
            (
                entry.entry_seq,
                u','.join(entry.kanas),
                u','.join(entry.kanjis),
                u','.join([g.gloss for g in entry.glosses])
            )
            for entry in entries]
        write_from_list(conn, items, sql, table)

        # Join tables
        sql = "select id, entry from entry"
        entry_dict = create_dict_from_sql(conn, sql)

        sql = "select id, kana from kana"
        kana_dict = create_dict_from_sql(conn, sql)

        items = []
        for entry in entries:
            for kana in entry.kanas:
                items.append((entry_dict.get(entry.entry_seq, 0), kana_dict.get(kana, 0)))

        self.notify('start writing kana entry join table')
        table = "create table kana_entry ( entry_id varchar, kana_id varchar );"
        sql = "insert into kana_entry(entry_id, kana_id) values(?, ?);"
        write_from_list(conn, items, sql, table)

        sql = "select id, kanji from kanji"
        kanji_dict = create_dict_from_sql(conn, sql)

        items = []
        for entry in entries:
            for kana in entry.kanjis:
                items.append((entry_dict.get(entry.entry_seq, 0), kanji_dict.get(kana, 0)))

        self.notify('start writing kanji entry join table')
        table = "create table kanji_entry (entry_id varchar, kanji_id varchar );"
        sql = "insert into kanji_entry(entry_id, kanji_id) values(?, ?);"
        write_from_list(conn, items, sql, table)

        self.notify('start writing gloss entry join table')
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

        self.notify('done saving')

