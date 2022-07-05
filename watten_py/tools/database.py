class DatabaseAttribute:
    def __init__(self, connection, table, value, statement, *args):
        self.connection = connection
        self.table = table
        self.value = value
        self.statement = statement
        self.args = args
        self.select_query = f'SELECT {value} from public."{table}" WHERE ' + statement
        self.update_query = f'UPDATE public."{table}" SET {value}=%s WHERE ' + statement
        self.append_query = f'UPDATE public."{table}" SET {value}=array_append({value}, %s) WHERE ' + statement

    def set(self, value):
        with self.connection.cursor() as curs:
            curs.execute(self.update_query, [value] + list(self.args))
            self.connection.commit()

    def get(self):
        with self.connection.cursor() as curs:
            curs.execute(self.select_query, self.args)
            dta = curs.fetchone()
            return dta[0] if dta else None

    def append(self, value):
        with self.connection.cursor() as curs:
            curs.execute(self.append_query, [value, self.args])
            self.connection.commit()
