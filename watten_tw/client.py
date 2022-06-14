import pickle

from kivy.support import install_twisted_reactor

install_twisted_reactor()

# A Simple Client that send messages to the Echo Server
from twisted.internet import reactor, protocol


class TwistedClientProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        data = pickle.loads(data)
        print(data)
        self.factory.app.handle_server_data(data)


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
