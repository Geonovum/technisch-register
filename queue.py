import os
import sqlite3


# extracted from
# https://github.com/scrapy/queuelib/blob/master/queuelib/queue.py
# as pipy version os queuelib does not have FifoSQLiteQueue
class FifoSQLiteQueue(object):

    _sql_create = (
        'CREATE TABLE IF NOT EXISTS queue '
        '(id INTEGER PRIMARY KEY AUTOINCREMENT, initiator text, prerelease bool)'
    )
    _sql_size = 'SELECT COUNT(*) FROM queue'
    _sql_push = 'INSERT INTO queue (initiator, prerelease) VALUES (?,?)'
    _sql_pop = 'SELECT id, initiator, prerelease FROM queue ORDER BY id LIMIT 1'
    _sql_del = 'DELETE FROM queue WHERE id = ?'

    def __init__(self, path):
        self._path = os.path.abspath(path)
        self._db = sqlite3.Connection(self._path, timeout=60)
        self._db.text_factory = bytes
        with self._db as conn:
            conn.execute(self._sql_create)

    def push(self, initiator, prerelease):
        # if not isinstance(item, bytes):
            # raise TypeError('Unsupported type: {}'.format(type(item).__name__))

        with self._db as conn:
            conn.execute(self._sql_push, (initiator, prerelease))

    def pop(self):
        with self._db as conn:
            for id_, initiator, prerelease in conn.execute(self._sql_pop):
                conn.execute(self._sql_del, (id_,))
                return initiator, prerelease

    def close(self):
        size = len(self)
        self._db.close()
        # do not remove database if queue is empty 
        # as that causes the .close() after first 
        # delete to fail
        if not size:
            try:
                os.remove(self._path)
            except OSError:
                print "Warning, can't delete database... continuing."

    def __len__(self):
        with self._db as conn:
            return next(conn.execute(self._sql_size))[0]

if __name__ == "__main__":
    # testing whether two connections can write to same
    # database

    fifo = FifoSQLiteQueue('queue.db')
    fifo2 = FifoSQLiteQueue('queue.db')

    fifo.push('a')
    fifo2.push('b')

    print fifo.pop()
    print fifo.pop()
    print fifo.pop()
    # print fifo.pop()

    fifo.push('c')

    print fifo2.pop()

    fifo.close()
    fifo2.close()