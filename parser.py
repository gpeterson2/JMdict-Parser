#! /usr/bin/env python

from lxml import etree

from model import Session
from model.r_ele import R_ele

class Parser(object):

    def parse(self, filename):
        #'test_files/JMdict'

        xml = open(filename, 'r')

        events = ('start', 'end')
        context = etree.iterparse(xml, events=events)

        ses = Session()
        #ses.begin()

        i = 0
        for action, elem in context:
            if elem.tag == 'reb':

                ses.begin()
                r = ses.query(R_ele).filter(R_ele.reb == elem.text).first();

                if not r:
                    r = R_ele()
                    r.reb = elem.text 
                    ses.add(r)
                ses.commit()

                #print('%s: %s %s' % (action, elem.tag, elem.text))
                print('%s: %s' % (i, elem.text))
                i += 1

        #ses.commit()

