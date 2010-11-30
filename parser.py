#! /usr/bin/env python

from lxml import etree

from models import Session
from models.entry import Entry
from models.kana_element import KanaElement
from models.kanji_element import KanjiElement
from models.gloss import Gloss
from models.sense import Sense
from models.part_of_speach import PartOfSpeach

class Parser(object):

    def parse(self, filename):
        #'test_files/JMdict'

        xml = open(filename, 'r')

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events)

        ses = Session()
        #ses.begin()

        # Set up the parts of speach, as I don't think there's
        # a way to read them directly from the file...
        self.insert_parts_of_speech(ses)

        entry = Entry()

        print('start reading')

        # looks like there 142665 total r_ele
        # still taking forever...
        # OK, putting everything in a dict, and then inserting sped things up
        # I don't really want that to be the overall pattern, though
        for i, (action, elem) in enumerate(context):

            tag = elem.tag

            if tag == 'entry' and action == 'start':
                entry = Entry()
                ses.begin()

            if tag == 'ent_seq' and action == 'start':
                entry.ent_seq = elem.text

            if tag == 'reb' and action == 'start':

                kana = KanaElement()
                kana.element = elem.text
                entry.kana.append(kana)

            if tag == 'keb' and action == 'start':

                kanji = KanjiElement()
                kanji.element = elem.text
                entry.kanji.append(kanji)

            if tag == 'sense' and action == 'start':
                sense = Sense();

            if tag == 'pos' and action == 'start':
                print('pos: %s' % elem.text)

            if tag == 'gloss' and action == 'start':
                gloss = Gloss()
                gloss.gloss = elem.text;

                lang = 'eng'
                keys = elem.keys()
                # Should have 0 or 1
                if len(keys) > 0:
                    # Not calling directly because it's a full namespace
                    # this is easier
                    lang = elem.get(keys[0])

                gloss.lang = lang                    

                sense.gloss.append(gloss)

            if tag == 'sense' and action == 'end':
                entry.sense.append(sense)

            if tag == 'entry' and action == 'end':
                ses.add(entry)
                ses.commit()

                # to make testing easier
                if i > 1000:
                    break

        print('done reading')
        print('commiting')

        #ses.commit()

        print('done commiting')

    def insert_parts_of_speech(self, ses):
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

        ses.begin()

        for abbr, text in poss:
            pos = PartOfSpeach()
            pos.code = abbr
            pos.text = text

            ses.add(pos)

        ses.commit() 

