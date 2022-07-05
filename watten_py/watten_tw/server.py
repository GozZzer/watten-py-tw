import pickle

from kivy.support import install_twisted_reactor
from kivy.logger import Logger
from twisted.internet.protocol import connectionDone
from twisted.python import failure

from watten_py.objects.network import Packet, GamePacket, UserUpdatePacket

install_twisted_reactor()

from twisted.internet import reactor, protocol


class TwistedServerProtocol(protocol.Protocol):

    def dataReceived(self, data):
        data = pickle.loads(data)
        Logger.info(f"Received: {data}")
        if isinstance(data, UserUpdatePacket):
            self.factory.app.handle_user_update(data, self.transport)
        elif isinstance(data, GamePacket):
            self.factory.app.handle_game_data(data, self.transport)
        else:
            self.factory.app.handle_data(data, self.transport)

    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        self.factory.app.on_disconnection(self.transport)


class TwistedServerFactory(protocol.ServerFactory):
    protocol = TwistedServerProtocol

    def __init__(self, app):
        self.app = app
