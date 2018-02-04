from core.utils.observer import Subject
from jmdict.data.parts_of_speech import PARTS_OF_SPEECH
from jmdict.data.sql.models import (
    Entry,
    Gloss,
    KanaElement,
    KanjiElement,
    PartOfSpeech,
    Sense,
    Warehouse,
    init_model,
    Session,
)


class Writer(Subject):

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

    def __init__(self, connection_string='test.db', drop_tables=False, *args, **kwargs):
        super(Writer, self).__init__(*args, **kwargs)

        self.meta = init_model(connection_string)

        if drop_tables:
            self.meta.drop_all()
        self.meta.create_all()

        self.session = Session()

    def write_entries(self, entries):
        ''' Write entries

            This assumes that other bulk queries have already been run.
        '''
        self.notify('start writing entries')

        # NOTE - This is horribly memory intensive. Ideally all of the bulk
        # inserted values would not have to be queried in full as dictionaries
        # but this then avoids a lookup for each individual item.
        #
        # Also, the relationships as currently defined can't be bulk inserted,
        # they would have to be defined as stand alone classes for that.
        #
        # Because of that this is also still slow as well.

        self.notify('start reading bulk queries')

        kana_query = self.session.query(KanaElement).all()
        kana_dict = {k.kana: k for k in kana_query}

        kanji_query = self.session.query(KanjiElement).all()
        kanji_dict = {k.kanji: k for k in kanji_query}

        pos_query = self.session.query(PartOfSpeech).all()
        pos_dict = {p.text: p for p in pos_query}

        gloss_key = lambda x: x.lang + '|' + x.gloss
        gloss_query = self.session.query(Gloss).all()
        gloss_dict = {gloss_key(g): g for g in gloss_query}

        self.notify('finish reading bulk queries')

        self.notify('start composing entries')

        items = []
        for entry in entries:
            item = Entry(ent_seq=entry.entry_seq)

            for kana in entry.kanas:
                kana_item = kana_dict[kana]
                item.kana.append(kana_item)

            for kanji in entry.kanjis:
                kanji_item = kanji_dict[kanji]
                item.kanji.append(kanji_item)

            for sense in entry.senses:
                sense_item = Sense()

                for pos in sense.poses:
                    pos_item = pos_dict.get(pos)
                    if pos_item:
                        sense_item.pos.append(pos_item)
                    else:
                        print('invalid part of speech: {} {}'.format(entry.entry_seq, pos))

                for misc in sense.miscs:
                    misc_item = pos_dict.get(misc)
                    sense_item.misc.append(misc_item)

                for gloss in sense.glosses:
                    key = gloss_key(gloss)
                    gloss_item = gloss_dict.get(key)
                    sense_item.gloss.append(gloss_item)

                item.sense.append(sense_item)

            items.append(item)

        self.notify('finish composing entries')

        #self.session.bulk_save_objects(items)

        self.notify('start entry save')

        self.session.begin()
        self.session.add_all(items)
        self.session.commit()

        self.notify('finish entry save')

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

    def write_glosses(self, glosses):
        self.notify('start writing glosses')

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
            # sqlite uses "|" for visual identification, so ideally something
            # other than that.

            w.pos = w.sep.join(poses)
            w.misc = w.sep.join(miscs)
            w.lang = w.sep.join(langs)
            w.gloss = w.sep.join(glosses)

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

        self.notify('start reading unique values')

        # Bulk unique tables
        kanas, kanjis, pos, glosses, miscs = self.split_entries(entries)

        self.write_kanas(kanas)
        self.write_kanjis(kanjis)
        self.write_glosses(glosses)
        self.write_parts_of_speech(PARTS_OF_SPEECH)

        # Join Tables.
        self.write_entries(entries)

        # Warehouse
        self.write_warehouse(entries)

        # self.session.commit()

        self.notify('done saving')


class Reader(object):

    def __init__(self, connection_string='test.db', *args, **kwargs):

        self.meta = init_model(connection_string)
        self.meta.create_all()

        self.session = Session()

    def read(self):

        items = []
        entries = self.session.query(Warehouse).all()

        for entry in entries:

            display = '{kanji} [{kana}] ({pos}) {glosses}'.format(
                kanji=','.join(entry.kanjis),
                kana=','.join(entry.kanas),
                pos=','.join(entry.parts_of_speech),
                glosses=','.join(entry.glosses),
            )
            items.appen(display)

        return items
