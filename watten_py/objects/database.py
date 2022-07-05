import uuid

import psycopg2
import psycopg2.extras


class WattenDatabase:
    connection: psycopg2._psycopg.connection

    def __init__(self):
        self.connect_to_db()
        psycopg2.extras.register_uuid()

    def connect_to_db(self, host: str = "localhost", port: int = 5432):
        try:
            connection = psycopg2.connect(
                database="watten-py",
                user="postgres",
                password="1234",
                host=host,
                port=port
            )
            # print("Connected to database")
            self.connection = connection
        except psycopg2.OperationalError:
            pass

    def stop_connection(self):
        self.connection.close()

    def new_user(self, user_id: uuid.UUID, user_name: str, email: str, password: str, dummy: bool = False):
        QUERY_LOGIN = f'INSERT INTO public."LoginData" (user_id, user_name, email, password, dummy) VALUES (%s, %s, %s, crypt(%s, gen_salt(%s)), %s) RETURNING user_id, user_name, email'
        DATA_LOGIN = (user_id, user_name, email, password, "md5", dummy)
        QUERY_PLAYER = f'INSERT INTO public."PlayerData" (user_id) VALUES (%s)'
        DATA_PLAYER = (user_id, )
        if dummy:
            usr = self.get_user(user_name=user_name)
            if usr:
                return usr

        if (not self.get_user(user_name=user_name) and not self.get_user(email=email)) or dummy:
            with self.connection.cursor() as curs:
                curs.execute(QUERY_LOGIN, DATA_LOGIN)
                user_dta = curs.fetchone()
                curs.execute(QUERY_PLAYER, DATA_PLAYER)
                self.connection.commit()
                return user_dta
        else:
            return None

    def get_uuid_by_node(self, node: int):
        node = ':'.join(['{}{}'.format(a, b) for a, b in zip(*[iter('{:012x}'.format(node))] * 2)])
        QUERY = 'SELECT user_id FROM public."LoginData" WHERE %s = uuid_macaddr(user_id) AND uuid_timestamp(user_id) = (SELECT MIN(uuid_timestamp(user_id)) FROM public."LoginData")'
        DATA = [node]
        with self.connection.cursor() as curs:
            curs.execute(QUERY, DATA)
            dta = curs.fetchone()
            return dta[0] if dta else None

    def get_user(self, user_id: uuid.UUID = None, user_name: str = None, email: str = None, password: str = None, node: int = None):
        QUERY = 'SELECT user_id, user_name, email FROM public."LoginData" WHERE'
        DATA = []
        if not node and not user_id and not user_name and not email and not password:
            return None
        if node:
            user_id = self.get_uuid_by_node(node)
        if user_id:
            if QUERY.endswith('" WHERE'):
                QUERY += ' user_id = %s'
            else:
                QUERY += ' and user_id = %s'
            DATA.append(user_id)
        else:
            if not user_id and not user_name and not email and not password:
                return None
        if user_name:
            if QUERY.endswith('" WHERE'):
                QUERY += ' user_name = %s'
            else:
                QUERY += ' AND user_name = %s'
            DATA.append(user_name)
        if email:
            if QUERY.endswith('" WHERE'):
                QUERY += ' email = %s'
            else:
                QUERY += ' AND email = %s'
            DATA.append(email)
        if password:
            if QUERY.endswith('" WHERE'):
                QUERY += ' password = crypt(%s, password)'
            else:
                QUERY += ' AND password = crypt(%s, password)'
            DATA.append(password)
        if QUERY.endswith('" WHERE'):
            QUERY += ' NOT connected'
        else:
            QUERY += ' AND NOT connected'
        with self.connection.cursor() as curs:
            curs.execute(QUERY, DATA)
            dta = curs.fetchone()
            if dta:
                curs.execute('UPDATE public."LoginData" SET connected=True WHERE user_id=%s', [dta[0]])
                self.connection.commit()
                return dta
            else:
                return None

    def disconnect_user(self, user_id: uuid.UUID):
        with self.connection.cursor() as curs:
            curs.execute('UPDATE public."LoginData" SET connected=False WHERE user_id=%s', [user_id])
            self.connection.commit()

    def get_player(self, user_id: uuid.UUID):
        QUERY = 'SELECT * FROM public."PlayerData" WHERE user_id=%s'
        DATA = [user_id]
        with self.connection.cursor() as curs:
            curs.execute(QUERY, DATA)
            dta = curs.fetchone()
            if dta:
                curs.execute('UPDATE public."PlayerData" SET connected_since=now() WHERE user_id=%s RETURNING *', [dta[0]])
                dta = curs.fetchone()
                self.connection.commit()
                return dta
            else:
                return [None, None, None, None]

    def new_set(self, player: list[list[uuid.UUID]]):
        QUERY_SET = 'INSERT INTO public."SetData" (team1_player1, team1_player2, team2_player1, team2_player2) VALUES (%s, %s, %s ,%s) RETURNING set_id'
        DATA_SET = [player[0][0], player[0][1], player[1][0], player[1][1]]
        with self.connection.cursor() as curs:
            curs.execute(QUERY_SET, DATA_SET)
            set_id = curs.fetchone()[0]
            self.connection.commit()
        QUERY_GAME = 'INSERT INTO public."GameData" (set_id) VALUES (%s) RETURNING game_id'
        DATA_GAME = [set_id]
        with self.connection.cursor() as curs:
            curs.execute(QUERY_GAME, DATA_GAME)
            game_id = curs.fetchone()[0]
            self.connection.commit()
        UPDATE_SET = 'UPDATE public."SetData" SET game_ids = array_append(game_ids, %s) WHERE set_id=%s'
        UPDATE_DATA = [game_id, set_id]
        with self.connection.cursor() as curs:
            curs.execute(UPDATE_SET, UPDATE_DATA)
            self.connection.commit()
        return set_id, game_id

    def new_game(self, set_id: int):
        QUERY_GAME = 'INSERT INTO public."GameData" (set_id) VALUES (%s) RETURNING game_id'
        DATA_GAME = [set_id]
        with self.connection.cursor() as curs:
            curs.execute(QUERY_GAME, DATA_GAME)
            game_id = curs.fetchone()[0]
            self.connection.commit()
        QUERY_SET = 'UPDATE public."SetData" SET game_ids = array_append(game_ids, %s) WHERE set_id=%s'
        DATA_SET = [game_id, set_id]
        with self.connection.cursor() as curs:
            curs.execute(QUERY_SET, DATA_SET)
            self.connection.commit()
        return game_id

    def get_set(self, set_id: int):
        QUERY_GAMES = 'SELECT * FROM public."GameData" WHERE set_id=%s'
        QUERY_SET = 'SELECT * FROM public."SetData" WHERE set_id=%s'
        DATA = [set_id]
        with self.connection.cursor() as curs:
            curs.execute(QUERY_GAMES, DATA)
            games = curs.fetchall()
            curs.execute(QUERY_SET, DATA)
            sett = list(curs.fetchone())
        return [
            sett[0],
            [games[games.index([dt for dt in games if dt[0] == gm][0])] for gm in sett[1]],
            [sett[2], sett[3]],
            [sett[4], sett[5]],
            sett[6], sett[7]
        ]

    def get_game(self, game_id: int):
        QUERY = 'SELECT * FROM public."GameData" WHERE game_id=%s'
        DATA = [game_id]
        with self.connection.cursor() as curs:
            curs.execute(QUERY, DATA)
            dta = curs.fetchone()
            return dta if dta else None

    def client_won_game(self, *user_id: uuid.UUID):
        QUERY = 'UPDATE public."PlayerData" SET games_won="PlayerData".games_won+1 WHERE user_id=%s'
        with self.connection.cursor() as curs:
            for user in user_id:
                DATA = (user,)
                curs.execute(QUERY, DATA)
            self.connection.commit()

    def client_won_set(self, *user_id: uuid.UUID):
        QUERY = 'UPDATE public."PlayerData" SET sets_won=sets_won+1 WHERE user_id=%s'
        with self.connection.cursor() as curs:
            for user in user_id:
                DATA = (user,)
                curs.execute(QUERY, DATA)
            self.connection.commit()


#d = WattenDatabase()
"""for i in ["abc", "def", "ghi", "jkl"]:
    uid = uuid.uuid1()
    d.new_user(uid, i, f"{i}@gmail.com", i)
    print(uid)"""
#d.new_user(uuid.uuid1(), "GozZzer", "gozzzer432@gmail.com", "1234")
# print(d.get_user(user_id=uuid.UUID("5f9ee3f1-f182-47b8-95a1-0754ebb70650")))
"""print(d.new_set([
    [uuid.UUID("0ed588b5-f658-11ec-8dc8-a2892896fc68"), uuid.UUID("0ed897ad-f658-11ec-9ad5-a2892896fc68")],
    [uuid.UUID("0ed897ae-f658-11ec-b68f-a2892896fc68"), uuid.UUID("0ed897af-f658-11ec-b244-a2892896fc68")]
]))"""
# print(d.new_game(1))
# print(d.get_set(1))
#print(d.get_user(node=uuid.getnode()))
