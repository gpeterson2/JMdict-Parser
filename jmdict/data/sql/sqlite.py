#! /usr/bin/env python

import os
import sqlite3

from jmdict.data.parts_of_speech import PARTS_OF_SPEECH
from jmdict.utils.observer import Subject
from jmdict.data.sql.models import (
    Entry,
    Gloss,
    KanaElement,
    KanjiElement,
    Misc,
    PartOfSpeech,
    Session,
    Warehouse,
    init_model,
)


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
        try:
            cur.execute(table_sql)
        except sqlite3.OperationalError:
            pass

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

    # TODO - this performs bulk entries, which we probably want for each item type.
    # But as is the bulk insert will not handle any connections between these items.
    #
    # Also when this was initially designed:
    # 1. Sqlalchemy was slow, so it ended up being faster to use direct bulk inserts
    # 2. sqlite does not handle joins very well.
    #
    # 1 should no longer be an issue, sqlalchemy now has a bulk insert.
    # 2 is the reason behind there being a "warehouse" attempt. Which was still
    #   supposed to have links to the bulk tables, ideally.
    #
    # So still to do:
    # - Insert the connections (which probably requires adding join tables to
    #   models).

    def __init__(self, connection_string='test.db', *args, **kwargs):
        super(SqliteWriter, self).__init__(*args, **kwargs)

        # New sqlalchemy queries
        uri = 'sqlite:///{0}'.format(connection_string)
        self.meta = init_model(uri)
        self.meta.create_all()

        # Probably should be created separately for each function
        self.session = Session()

    def write_entries(self, entries):
        self.notify('start writing entries')

        # FIXME - Will need to update this with connections later.
        items = [Entry(ent_seq=e.entry_seq) for e in entries]
        self.session.bulk_save_objects(items)

    # Why don't I have this again? Was this the hard-coded part?
    def write_parts_of_speech(self, poses):
        self.notify('start writing parts of speech')

        items = [PartOfSpeech(code=code, text=text) for code, text in poses]
        self.session.bulk_save_objects(items)

    def write_kanas(self, kanas):
        self.notify('start writing kana')

        items = [KanaElement(kana=k) for k in kanas]
        self.session.bulk_save_objects(items)

    def write_kanjis(self, kanjis):
        self.notify('start writing kanji')

        items = [KanjiElement(kanji=k) for k in kanjis]
        self.session.bulk_save_objects(items)

    # FIXME - Technically these are parts of speech, but in a separate category.
    def write_miscs(self, miscs):
        self.notify('start writing misc')

        # FIXME - pos should be on the sense element.
        items = [Misc(misc=m) for m in miscs]
        self.session.bulk_save_objects(items)

    # FIXME - write Sense entry as well. Doesn't necessarily have to be here.
    def write_glosses(self, glosses):
        self.notify('start writing glosses')

        # FIXME - pos should be on the sense element.
        items = [Gloss(gloss=g.gloss, lang=g.lang) for g in glosses]
        self.session.bulk_save_objects(items)

    def write_warehouse(self, entries):

        self.notify('start writing warehouse')

        items = []
        for entry in entries:
            w = Warehouse()
            w.entry_id = entry.entry_seq
            w.kana = u','.join(entry.kanas)
            w.kanji = u','.join(entry.kanjis)

            poses = set()
            glosses = set()
            miscs = set()
            langs = set()

            for sense in entry.senses:
                for pos in sense.poses:
                    poses.add(pos)

                for misc in sense.miscs:
                    miscs.add(pos)

                for gloss in sense.glosses:
                    glosses.add(gloss.gloss)
                    langs.add(gloss.lang)

            # FIXME - use another separator to join these.
            w.pos = u','.join(poses)
            w.misc = u','.join(miscs)
            w.lang = u','.join(langs)
            w.gloss = u','.join(glosses)

            items.append(w)

        self.session.bulk_save_objects(items)

    # TODO - fix the return value on this.
    def split_entries(self, entries):

        # Need to pull this information out of the main list. Should be in a
        # generic class, or done while reading it - although I imaging that
        # some writeable formats won't need it.
        poses = set()
        kanas = set()
        kanjis = set()
        miscs = set()
        glosses = set()

        for entry in entries:
            for kana in entry.kanas:
                kanas.add(kana)

            for kanji in entry.kanjis:
                kanjis.add(kanji)

            for sense in entry.senses:
                for pos in sense.poses:
                    poses.add(pos)

                for misc in sense.miscs:
                    miscs.add(misc)

                for gloss in sense.glosses:
                    glosses.add(gloss)

        return kanas, kanjis, poses, glosses, miscs

    def write(self, entries):
        ''' Writes the various lists to a database.

            :param entries: A list of entries objects.
        '''

        self.notify('start saving')

        # Unique tables

        # TODO - this is taking far too much time, probably go back to
        # getting this when reading.
        self.notify('start reading unique values')

        kanas, kanjis, pos, glosses, miscs = self.split_entries(entries)

        self.write_entries(entries)
        self.write_kanas(kanas)
        self.write_kanjis(kanjis)
        self.write_miscs(miscs)
        self.write_glosses(glosses)
        self.write_parts_of_speech(PARTS_OF_SPEECH)

        self.write_warehouse(entries)

        # self.session.commit()

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
                entry_id
                , kana
                , kanji
                , pos
                , misc
                , gloss
                , lang
            from warehouse
            where 'eng' in lang
        """

        cur.execute(sql)

        entries = []
        for row in cur.fetchall():
            entry_id = row['entry_id']
            kanas = row['kana'].split(',')
            kanjis = row['kanji'].split(',')
            pos = row['pos'].split(',')
            gloss = row['gloss'].split(',')
            lang = row['lang'].split(',')

            entry = (u'{} [{}] ({}) {} {} {}'.format(
                entry_id,
                ', '.join(kanas),
                ', '.join(kanjis),
                ', '.join(pos),
                ', '.join(gloss),
                ', '.join(lang)))

            entries.append(entry.strip())

        return entries
