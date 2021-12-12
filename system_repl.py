class Record:
    """Record in database."""
    def __init__(self, record_id, info):
        self.__id = record_id
        self.__info = info

    def get_id(self):
        """Return record ID."""
        return self.__id

    def get_info(self):
        """Return record info."""
        return self.__info


class Database:
    """Database prototype."""
    def __init__(self):
        self.__records = {}

    def records_num(self):
        """Number of records."""
        return len(self.__records)

    def add_record(self, r):
        """Add record to database."""
        if r.get_id() in self.__records:
            raise ValueError("Duplicated ID")

        self.__records[r.get_id()] = r

    def get_record(self, record_id):
        """Get record by ID."""
        try:
            return self.__records[record_id]
        except KeyError:
            return None

    def get_all(self):
        """Return all records."""
        return self.__records


class System:
    """System with replication."""
    def __init__(self, repls_num=1):
        if repls_num < 1:
            raise ValueError("repls_num must be positive")

        self.__main = Database()
        self.__repls = []
        self.__stats = {
            'main': 0,
            'repl': [],
        }
        for _ in range(repls_num):
            self.__repls.append(Database())
            self.__stats['repl'].append(0)

        self.__ind = 0

    def get_main(self):
        """Return main DB."""
        return self.__main

    def get_repl(self, ind=0):
        """Return replicated DB."""
        return self.__repls[ind]

    def sync(self):
        """Synchronize system."""
        for repl in self.__repls:
            _sync(self.__main, repl)

    def add_record(self, rec):
        """Add record to database."""
        return self.__main.add_record(rec)

    def get_record(self, record_id):
        """Get record by ID."""
        rec = self.__repls[self.__ind].get_record(record_id)
        self.__stats['repl'][self.__ind] += 1
        self.__update_ind()
        if rec:
            return rec
        return self.__main.get_record(record_id)

    def get_all(self):
        """Return all records."""
        res = self.__repls[self.__ind].get_all()
        self.__stats['repl'][self.__ind] += 1
        self.__update_ind()
        return res

    def stats(self):
        """Return statistics of readings."""
        return self.__stats

    def __update_ind(self):
        self.__ind = (self.__ind + 1) % len(self.__repls)


def _sync(src, dst):
    records = src.get_all()
    for rec_id, rec in records.items():
        if not dst.get_record(rec_id):
            dst.add_record(rec)