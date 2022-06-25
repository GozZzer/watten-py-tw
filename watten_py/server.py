import datetime
import pickle

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

from watten_py.objects import Packet, Client, ServerSideClient
from watten_py.watten_tw import sr_reactor, TwistedServerFactory


class WattenServerApp(App):
    layout = None
    factory = None
    connections = []

    def build(self):
        self.layout = StackLayout()
        self.factory = TwistedServerFactory(self)
        sr_reactor.listenTCP(5643, self.factory)
        return self.layout

    def handle_data(self, data, transport):
        data = pickle.loads(data)
        match data.task_type:
            case "NODE_R":
                user = Client.get_user_by_node(data.data["node"])
                if isinstance(user, Client):
                    server_user = ServerSideClient.from_Client(user)
                    if server_user.username not in [conn.protocol.user.username for conn in self.connections if conn.protocol.user]:
                        transport.protocol.user = server_user
                        transport.btn.text = user.username
                    else:
                        user = None
                transport.write(pickle.dumps(Packet("USER", user=user)))
            case "LOGOUT":
                host = transport.getHost()
                transport.btn.text = f"{host.host}:{host.port}"
            case "LOGIN":
                user = Client.get_user(data.data["username"], data.data["password"])
                if isinstance(user, Client):
                    server_user = ServerSideClient.from_Client(user)
                    if server_user.username not in [conn.protocol.user.username for conn in self.connections if conn.protocol.user]:
                        transport.user = ServerSideClient.from_Client(user)
                        transport.btn.text = user.username
                    else:
                        print("x")
                        user = "This account is already connected to the server"
                print(user)
                transport.write(pickle.dumps(Packet("USER_LOG", user=user)))
            case "REGISTER":
                user = Client.new_user(data.data["username"], data.data["email"], data.data["password"], data.data["uuid"])
                if isinstance(user, Client):
                    transport.user = ServerSideClient.from_Client(user)
                    transport.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_REG", user=user)))
            case "DUMMY":
                user = Client.new_user(data.data["name"], uuid=data.data["uuid"])
                if isinstance(user, Client):
                    transport.user = ServerSideClient.from_Client(user)
                    transport.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_DUM", user=user)))
            case "READY":
                print(transport.__dict__)
                transport.user.ready = not transport.user.ready
                if transport.user.ready:
                    transport.user.ready_time = datetime.datetime.now()
                    self.ask_for_game_start(transport.user)

        print(data)

    def ask_for_game_start(self, ready_user: ServerSideClient):
        ready_player = [pl for pl in self.connections if pl.user.ready]
        print(ready_player)

    def on_connection(self, transport):
        print("connect", transport)
        host = transport.getHost()
        btn = Button(text=f"{host.host}:{host.port}", width=100, size_hint=(None, 0.15))
        transport.btn = btn
        self.layout.add_widget(btn)
        self.connections.append(transport)
        transport.write(pickle.dumps(Packet("NODE")))

    def on_disconnection(self, transport):
        self.layout.remove_widget(transport.btn)
        print(transport.btn == self.connections[0].btn)
        self.connections.pop(self.connections.index([trans for trans in self.connections if transport.btn == self.connections[0].btn][0]))
        print("disconnect", transport)


if __name__ == '__main__':
    WattenServerApp().run()
