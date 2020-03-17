import abc
import sqlite3


class IDb(abc.ABC):

    @staticmethod
    def tb_name() -> str:
        pass

    def __str__(self):
        return str(tuple([str(self.__dict__[key]) for key in self.__dict__]))

    def _get_properties(self):
        return [key for key in self.__dict__]


class Db:
    __connect: sqlite3.Connection = None

    def __connect_db(self) -> sqlite3.Connection:
        if self.__connect is None:
            self.__connect = sqlite3.connect('database.db')  # або :memory: що б зберігати у RAM
        return self.__connect

    def create_tb(self, entity: IDb):
        # print('create_tb')
        fields = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
        # print('entity.__dict__', entity.__dict__)
        for field in entity.__dict__:
            value = entity.__dict__[field]
            if type(value) is float:
                fields.append(f'{field} REAL')
                continue
            if type(value) is int:
                fields.append(f'{field} INTEGER')
                continue
            if field.find('date_create') != -1:
                fields.append(f'{field} timestamp')
                continue
            if field.find('hash') != -1:
                fields.append(f'{field} TEXT NOT NULL UNIQUE')
                continue
            else:
                fields.append(f'{field} TEXT')

        # self.__connect_db().execute(f"DROP TABLE IF EXISTS {entity.tb_name()}")
        sql = f"CREATE TABLE IF NOT EXISTS {entity.tb_name()} ({', '.join(fields)})"
        # print(sql)
        self.__connect_db().execute(sql)

    def insert(self, entity: IDb):
        values = tuple([str(value) for value in entity.__dict__.values()])
        sql = f"INSERT INTO {entity.tb_name()}{tuple(entity.__dict__.keys())} VALUES {values}"
        print(f'sql = "{sql}"')
        self.__connect_db().cursor().execute(sql)
        self.__connect_db().commit()

    # def insert_or_replace(self, entity: IDb):
    #     values = [str(value) for value in entity.__dict__.values()]
    #     sql = f"INSERT OR REPLACE INTO {entity.tb_name()}(id, {', '.join(entity.__dict__.keys())})  VALUES
    #     ((SELECT id FROM {entity.tb_name()} WHERE hash = "
    #     entity.hash
    #     ") {', '.join(values)})"
    #     print(f'sql = "{sql}"')
    #     self.__connect_db().cursor().execute(sql)
    #     self.__connect_db().commit()

    def find_by(self, tbl: str, value: str, column: str = 'id') -> tuple:
        sql = f"SELECT * FROM {tbl} WHERE {column} = '{value}'"
        print('sql=', sql)
        cursor = self.__connect_db().cursor()
        cursor.execute(sql)
        return cursor.fetchone()
