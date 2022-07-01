import datetime
import pickle
import uuid

from watten_py.objects.database import WattenDatabase
from watten_py.objects.network import GamePacket, Packet


class User:
    def __init__(self, user_id: uuid.UUID, username: str, email: str = None):
        self.user_id: uuid.UUID = user_id
        self.username = username
        self.email = email

    def __str__(self):
        return f"<Client {self.username}>"

    @classmethod
    def get_user(cls, username: str, password: str, database: WattenDatabase, dummy: bool = False):
        usr = database.get_user(user_name=username, password=password)
        if usr:
            return cls(*usr)
        else:
            if not database.get_user(user_name=username):
                return "Invalid Username"
            elif not database.get_user(password=password):
                return "Invalid Password"

    @classmethod
    def get_user_by_node(cls, node, database: WattenDatabase):
        usr = database.get_user(node=node)
        if usr:
            return cls(*usr)
        else:
            return None

    @classmethod
    def new_user(cls, user_id: uuid.UUID, username: str, email: str, password: str, database: WattenDatabase, dummy: bool = False):
        usr = database.new_user(user_id, username, email, password, dummy)
        if usr:
            return cls(*usr)
        else:
            return None


class ServerSideUser(User):
    def __init__(self, connection, btn, *args, **kwargs):
        self.connection = connection
        self.btn = btn
        self.ready: bool = False
        self.ready_time: datetime.datetime | None = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"<ServerSideClient {self.username}, ready={self.ready}>"

    @classmethod
    def from_User(cls, client: User, connection, btn):
        if client is None:
            return None
        else:
            return cls(
                connection,
                btn,
                **client.__dict__
            )

    def to_User(self):
        return User(self.user_id, self.username, self.email)

    def send(self, packet: Packet | GamePacket):
        self.connection.write(pickle.dumps)(packet)
