from kivy.support import install_twisted_reactor
from twisted.internet.protocol import connectionDone
from twisted.python import failure

install_twisted_reactor()

from twisted.internet import reactor, protocol


class TwistedServerProtocol(protocol.Protocol):
    btn = None
    user = None

    def dataReceived(self, data):
        self.factory.app.handle_data(data, self.transport)

    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        self.factory.app.on_disconnection(self.transport)


class TwistedServerFactory(protocol.Factory):
    protocol = TwistedServerProtocol

    def __init__(self, app):
        self.app = app
