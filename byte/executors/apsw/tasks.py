from byte.core.models import Task, ReadTask, SelectTask, WriteTask


class ApswTask(Task):
    def __init__(self, executor, sql, parameters):
        super(ApswTask, self).__init__(executor)

        self.sql = sql
        self.parameters = parameters

        self.cursor = None

    def open(self):
        self.cursor = self.executor.cursor()

    def execute(self):
        self.open()

        # Execute SQL
        print('EXECUTE: %r %r' % (self.sql, self.parameters))
        self.cursor.execute(self.sql, self.parameters)

        return self

    def close(self):
        self.cursor.close()


class ApswReadTask(ReadTask, ApswTask):
    pass


class ApswSelectTask(SelectTask, ApswReadTask):
    def items(self):
        for row in self.cursor:
            yield self.model.from_plain(
                self._build_item(row),
                translate=True
            )

    def _build_item(self, row):
        data = {}

        for i, (c_name, c_type) in enumerate(self.cursor.getdescription()):
            data[c_name] = row[i]

        return data


class ApswWriteTask(WriteTask, ApswTask):
    pass
