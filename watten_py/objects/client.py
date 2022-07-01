import pickle
import uuid

from kivy.uix.button import Button

from watten_py.objects.user import UnknownUser, User, ServerSideUser
from watten_py.objects.game.player import Player, ServerSidePlayer
from watten_py.objects.network import Packet, GamePacket


class Client:
    user: ServerSideUser
    _user: User
    player: ServerSidePlayer
    _player: Player

    def __init__(self, connection, btn: Button):
        self.connection = connection
        self.btn = btn
        self.uk_user = UnknownUser(connection, btn)

    @classmethod
    def on_connection(cls, connection):
        host = transport.getHost()
        btn = Button(text=f"{host.host}:{host.port}", width=100, size_hint=(None, 0.15))
        cli = cls(connection, btn)
        return cli, btn, cli.uk_user

    def send(self, packet: Packet | GamePacket):
        if self.connection:
            if (self.player and isinstance(packet, GamePacket)) or (self.user and isinstance(packet, Packet)):
                self.connection.write(pickle.dumps(packet))
            else:
                return False
