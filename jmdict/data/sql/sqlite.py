#! /usr/bin/env python

import codecs
import os
import sqlite3

from core.data.writer import Writer
from core.utils.observer import Subject

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
        item_id = row[0]
        entry = row[1]
        d[entry] = item_id

    return d

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

        # TODO - this is taking far too much time, proably go back to
        # getting this when reading.
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
        table = """
            create table warehouse (
                id integer primary key,
                entry int,
                kana varchar,
                kanji varchar,
                gloss varchar,
                pos varchar,
                lang varchar
            );
        """
        sql = """
            insert into warehouse(
                entry,
                kana,
                kanji,
                gloss,
                pos,
                lang
            ) values(?, ?, ?, ?, ?, ?)
        """
        items = [
            (
                entry.entry_seq,
                u','.join(entry.kanas),
                u','.join(entry.kanjis),
                u','.join(set([g.gloss for g in entry.glosses])),
                u','.join(set([g.pos for g in entry.glosses])),
                u','.join(set([g.lang for g in entry.glosses])),
            )
            for entry in entries]
        write_from_list(conn, items, sql, table)

        # Join tables
        sql = "select id, entry from entry"
        entry_dict = create_dict_from_sql(conn, sql)

        sql = "select id, kana from kana"
        kana_dict = create_dict_from_sql(conn, sql)

        sql = "select id, kanji from kanji"
        kanji_dict = create_dict_from_sql(conn, sql)

        sql = "select id, gloss from gloss"
        gloss_dict = create_dict_from_sql(conn, sql)

        # TODO - Do this for glosses?
        kana_items = []
        kanji_items = []
        gloss_items = []
        for entry in entries:
            entry_seq = entry_dict.get(entry.entry_seq, 0)

            for kana in entry.kanas:
                kana_id = kana_dict.get(kana, 0)
                kana_items.append((entry_seq, kana_id))

            for kana in entry.kanjis:
                kanji_id = kanji_dict.get(kanji, 0)
                kanji_items.append((entry_seq, kanji_id))

            for gloss in entry.glosses:
                gloss_id = gloss_dict.get(kana, 0)
                gloss_items.append((entry_seq, gloss_id))

        # set up a join table for kanas
        self.notify('start writing kana entry join table')
        table = "create table kana_entry ( entry_id varchar, kana_id varchar );"
        sql = "insert into kana_entry(entry_id, kana_id) values(?, ?);"
        write_from_list(conn, kana_items, sql, table)

        # set up a join table for kanjis.
        self.notify('start writing kanji entry join table')
        table = "create table kanji_entry (entry_id varchar, kanji_id varchar );"
        sql = "insert into kanji_entry(entry_id, kanji_id) values(?, ?);"
        write_from_list(conn, kanji_items, sql, table)

        # set up a join table for glosses.
        self.notify('start writing gloss entry join table')
        table = "create table gloss_entry ( entry_id, gloss_id );"
        sql = """insert into gloss_entry(entry_id, gloss_id) values(?, ?);"""
        write_from_list(conn, gloss_items, sql, table)

        # Second attempt at a warehouse
        # pros: unique gloss/lang/pos entries
        # cons: duplicate kana/kanji
        self.notify('start writing warehouse2')
        table = """
            create table warehouse2 (
                id integer primary key,
                entry int,
                kana varchar,
                kanji varchar,
                gloss varchar,
                pos varchar,
                lang varchar,
                kana_count,
                kanji_count
            );
        """
        sql = """
            insert into warehouse2 (
                entry,
                kana,
                kanji,
                gloss,
                pos,
                lang,
                kana_count,
                kanji_count
            ) values(?, ?, ?, ?, ?, ?, ?, ?)
        """
        items = []
        for entry in entries:
            for g in entry.glosses:
                items.append((
                    entry.entry_seq,
                    u','.join(entry.kanas),
                    u','.join(entry.kanjis),
                    g.gloss,
                    g.pos,
                    g.lang,
                    len(entry.kanas),
                    len(entry.kanjis),
                ))
        write_from_list(conn, items, sql, table)

        # third attempt at a warehouse
        # pros: no duplication/comma separated values
        # cons: difficult to recreate an entry
        self.notify('start writing warehouse3')
        table = """
            create table warehouse3 (
                id integer primary key,
                entry int,
                kana varchar,
                kanji varchar,
                gloss varchar,
                pos varchar,
                lang varchar,
                kana_count,
                kanji_count
            );
        """
        sql = """
            insert into warehouse3 (
                entry,
                kana,
                kanji,
                gloss,
                pos,
                lang,
                kana_count,
                kanji_count
            ) values(?, ?, ?, ?, ?, ?, ?, ?)
        """
        items = []
        for entry in entries:
            kana_len = len(entry.kanas)
            kanji_len = len(entry.kanjis)

            kanas = [('a', k) for k in entry.kanas]
            kanjis = [('j', k) for k in entry.kanjis]

            both = kanas + kanjis

            for t, b in both:
                a = b if t == 'a' else ''
                j = b if t == 'j' else ''

                for g in entry.glosses:
                    items.append((
                        entry.entry_seq,
                        a,
                        j,
                        g.gloss,
                        g.pos,
                        g.lang,
                        kana_len,
                        kanji_len,
                    ))

        write_from_list(conn, items, sql, table)

        # TODO - this takes too long to query.
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

class Reader(object):
    pass

class SqliteReader(Reader):
    def read(self):
        connection_string = 'test.db'

        if not os.path.exists(connection_string):
            # TODO make this a specific exception, and pass this in.
            raise Exception('Databse not found.')

        conn = sqlite3.connect(connection_string)

        cur = conn.cursor()

        sql = """
            select
                entry,
                kana,
                kanji,
                gloss,
                pos,
                lang,
                kana_count,
                kanji_count
            from warehouse3
            where lang = 'eng'
        """

        cur.execute(sql)

        entries = []
        for row in cur.fetchall():
            entry_id = row[0]
            kanas = unicode(row[1]).split(',')
            kanjis = unicode(row[2]).split(',')
            gloss = row[3]
            pos = row[4]
            lang = row[5]

            entry = (u'{0} [{1}] ({2}) {3} {4}'
                .format(', '.join(kanas), ', '.join(kanjis), pos, gloss, lang))

            entries.append(entry.strip())

        return entries
