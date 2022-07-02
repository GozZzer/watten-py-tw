import pickle

from kivy.uix.button import Button

from watten_py.objects.user import User
from watten_py.objects.game.player import Player, ServerSidePlayer
from watten_py.objects.network import Packet, GamePacket, UserUpdatePacket
from watten_py.objects.database import WattenDatabase


class Client:
    def __init__(self, connection, btn: Button):
        self.connection = connection
        self.btn = btn
        self.user: User | None = None
        self.player: ServerSidePlayer | None = None
        self._player: Player | None = None

    def __str__(self):
        return f"<Client connection: {self.connection}>"

    @classmethod
    def on_connection(cls, transport):
        host = transport.getHost()
        btn = Button(text=f"{host.host}:{host.port}", width=100, size_hint=(None, 0.15))
        cli = cls(transport, btn)
        return cli, btn

    def logout(self, db: WattenDatabase):
        if self.user:
            db.disconnect_user(self.user.user_id)

    def on_user_update(self, packet: UserUpdatePacket, db: WattenDatabase):
        print(f"uhdl: {packet}")
        match packet.task_type:
            case "NODE_R":
                self.user = User.get_user_by_node(packet.data["node"], db)
                self.send(Packet("USER", user=self.user))
            case "LOGIN":
                self.user = User.get_user(username=packet.data["username"], password=packet.data["password"], database=db)
                if isinstance(self.user, User):
                    self.btn.text = self.user.username
                self.send(Packet("USER_LOG", user=self.user))
            case "REGISTER":
                self.user = User.new_user(packet.data["uuid"], packet.data["username"], packet.data["email"], packet.data["password"], db)
                if isinstance(self.user, User):
                    self.btn.text = self.user.username
                self.send(Packet("USER_REG", user=self.user))
            case "DUMMY":
                self.user = User.new_user(packet.data["uuid"], packet.data["name"], "dummy", "password", db, True)
                if isinstance(self.user, User):
                    self.btn.text = self.user.username
                self.send(Packet("USER_DUM", user=self.user))
            case "LOGOUT":
                host = self.connection.getHost()
                self.btn.text = f"{host.host}:{host.port}"
                self.logout(db)
                self.user, self.user = None, None
            case _:
                raise NotImplementedError

    def ready(self, db: WattenDatabase):
        if self.user:
            self._player = Player(self.user.user_id, db)
            self.player = ServerSidePlayer(self.user.user_id, db)
            return True
        else:
            return False

    def set_done(self):
        self.player = None
        self._player = None

    def send(self, packet: Packet | GamePacket):
        if self.connection:
            self.connection.write(pickle.dumps(packet))
            print(f"sent: {packet}")
            return True
        else:
            return False
