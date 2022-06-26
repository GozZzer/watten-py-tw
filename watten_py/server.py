import datetime
import pickle

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import partial
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
                transport.protocol.user = None
                transport.btn.text = f"{host.host}:{host.port}"
            case "LOGIN":
                user = Client.get_user(data.data["username"], data.data["password"])
                if isinstance(user, Client):
                    server_user = ServerSideClient.from_Client(user)
                    if server_user.username not in [conn.protocol.user.username for conn in self.connections if conn.protocol.user]:
                        transport.protocol.user = ServerSideClient.from_Client(user)
                        transport.btn.text = user.username
                    else:
                        user = "This account is already connected to the server"
                transport.write(pickle.dumps(Packet("USER_LOG", user=user)))
            case "REGISTER":
                user = Client.new_user(data.data["username"], data.data["email"], data.data["password"], data.data["uuid"])
                if isinstance(user, Client):
                    transport.protocol.user = ServerSideClient.from_Client(user)
                    transport.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_REG", user=user)))
            case "DUMMY":
                user = Client.new_user(data.data["name"], uuid=data.data["uuid"])
                if isinstance(user, Client):
                    transport.protocol.user = ServerSideClient.from_Client(user)
                    transport.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_DUM", user=user)))
            case "READY":
                transport.protocol.user.ready = not transport.protocol.user.ready
                if transport.protocol.user.ready:
                    print(f"{transport.protocol.user.username} is ready")
                    transport.protocol.user.ready_time = datetime.datetime.now()
                    self.ask_for_game_start(transport.protocol.user)

        # print(data)

    def ask_for_game_start(self, ready_player: ServerSideClient):
        ready_players = [pl for pl in self.connections if pl.protocol.user.ready]
        if len(ready_players) >= 4:
            ready_players.sort(key=lambda r_pl: r_pl.protocol.user.ready_time)
            game_players = ready_players[:4]
            # Check if the player who started the game is in the game if not this statement adds him
            if ready_player.username not in [pl.protocol.user.username for pl in ready_players]:
                try:
                    conn = [con for con in self.connections if con.protocol.user.username == ready_player.username][0]
                    ready_players[3] = conn
                except IndexError:
                    pass
            Clock.schedule_once(partial(self.start_game, ready_players))

    def start_game(self, players: list):
        pass

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
        print([trans for trans in self.connections if transport.btn == self.connections[0].btn])
        connection = [trans for trans in self.connections if transport.btn == self.connections[0].btn]
        if connection:
            self.connections.pop(self.connections.index(connection[0]))
        print("disconnect", transport)


if __name__ == '__main__':
    WattenServerApp().run()
