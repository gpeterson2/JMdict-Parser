# TODO - here because there were some optimizations for sqlite
# There might still need to be some, if this is the file format to use going forward.

from jmdict.data.sql.base import Writer, Reader


class SqliteWriter(Writer):

    def __init__(self, connection_string='test.db', drop_tables=False, *args, **kwargs):
        uri = 'sqlite:///{0}'.format(connection_string)
        super(SqliteWriter, self).__init__(connection_string=uri, drop_tables=drop_tables, *args, **kwargs)


class SqliteReader(Reader):

    def __init__(self, connection_string='test.db', *args, **kwargs):
        uri = 'sqlite:///{0}'.format(connection_string)
        super(SqliteReader, self).__init__(connection_string=uri, *args, **kwargs)
