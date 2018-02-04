import gzip
import io

from core.utils.observer import Subject


class ParserException(Exception):
    pass


class InvalidFileType(ParserException):
    pass


# Actually probably don't want to call the parse function directly, could be cases when special ones are
# called instead.
# TODO - add further compression types?
class Parser(Subject):

    def __init__(self, *args, **kwargs):
        ''' Reads an xml file or gzipped xml file.

            :params infile: The input file.
            :params message_out: An output stream for parsing messages,
                defaults to none.
        '''

        super(Parser, self).__init__(*args, **kwargs)

    def parse_from_file(self, path=None):
        ''' Parse a JMDict file from the given a filepath.

            :param path: Path to a file to read.
        '''

        xml_file = None
        if path.endswith('.gz'):
            xml_file = gzip.open(path, 'r')
        elif path.endswith('xml'):
            xml_file = open(path, 'r')
        else:
            raise InvalidFileType('Invalid file type')

        return self.parse(xml_file)

    def parse_from_string(self, data):
        ''' Parse a JMDict string.

            :params data: The string to read.
        '''

        # xml = io.BytesIO(data.encode('utf-8'))
        xml = io.BytesIO(bytearray(data, 'utf-8'))

        return self.parse(xml)

    def parse(self, xml):
        raise NotImplemented()
