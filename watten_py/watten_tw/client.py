import pickle

from kivy.support import install_twisted_reactor

from watten_py.objects.network import Packet, GamePacket

install_twisted_reactor()

from twisted.internet import reactor, protocol


class TwistedClientProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        data = pickle.loads(data)
        if isinstance(data, Packet):
            self.factory.app.handle_data(data)
        elif isinstance(data, GamePacket):
            self.factory.app.handle_game_data(data)


class TwistedClientFactory(protocol.ClientFactory):
    protocol = TwistedClientProtocol

    def __init__(self, app):
        self.app = app

    def startedConnecting(self, connector):
        self.app.status = "1"

    def clientConnectionLost(self, connector, reason):
        self.app.status = "0"

    def clientConnectionFailed(self, connector, reason):
        self.app.status = "-1"
