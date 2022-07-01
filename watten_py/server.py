import datetime
import pickle
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

from watten_py.objects.game.game import ServerSideSet
from watten_py.objects.game.player import ServerSidePlayer
from watten_py.objects.user import User, ServerSideUser, UnknownUser
from watten_py.objects.network import Packet
from watten_py.objects.database import WattenDatabase
from watten_py.watten_tw import sr_reactor, TwistedServerFactory


class WattenServerApp(App):
    layout: StackLayout
    factory: TwistedServerFactory
    database: WattenDatabase
    connections: list[ServerSideUser | UnknownUser] = []

    def build(self):
        self.layout = StackLayout()
        self.database = WattenDatabase()
        self.factory = TwistedServerFactory(self)
        sr_reactor.listenTCP(5643, self.factory)
        return self.layout

    def handle_data(self, data, transport):
        usr = self.resolve_user(transport)
        match data.task_type:
            case "NODE_R":
                user = User.get_user_by_node(data.data["node"], self.database)
                if isinstance(user, User):
                    server_user = ServerSideUser.from_User(user, usr.connection, usr.btn)
                    if server_user.username not in [conn.username for conn in self.connections if isinstance(conn, ServerSideUser)]:
                        server_user.btn.text = server_user.username
                        self.connections[self.connections.index(usr)] = server_user
                    else:
                        user = None
                transport.write(pickle.dumps(Packet("USER", user=user)))
            case "LOGOUT":
                host = transport.getHost()
                self.connections[self.connections.index(usr)] = UnknownUser(usr.connection, usr.btn)
                usr.btn.text = f"{host.host}:{host.port}"
            case "LOGIN":
                user = User.get_user(username=data.data["username"], password=data.data["password"], database=self.database)
                if isinstance(user, User):
                    server_user = ServerSideUser.from_User(user, usr.connection, usr.btn)
                    if server_user.username not in [conn.username for conn in self.connections if isinstance(conn, ServerSideUser)]:
                        server_user.btn.text = server_user.username
                        self.connections[self.connections.index(usr)] = server_user
                    else:
                        user = "This account is already connected to the server"
                transport.write(pickle.dumps(Packet("USER_LOG", user=user)))
            case "REGISTER":
                user = User.new_user(data.data["uuid"], data.data["username"], data.data["email"], data.data["password"], self.database)
                if isinstance(user, User):
                    self.connections[self.connections.index(usr)] = ServerSideUser.from_User(user, usr.connection, usr.btn)
                    usr.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_REG", user=user)))
            case "DUMMY":
                user = User.new_user(data.data["uuid"], data.data["name"], "dummy", "password", self.database, True)
                if isinstance(user, User):
                    self.connections[self.connections.index(usr)] = ServerSideUser.from_User(user, usr.connection, usr.btn)
                    usr.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_DUM", user=user)))
            case "READY":
                if isinstance(usr, ServerSideUser):
                    usr.ready = not usr.ready
                    if usr.ready:
                        print(f"{usr.username} is ready")
                        usr.ready_time = datetime.datetime.now()
                        self.ask_for_game_start(usr)

        # print(data)

    def handle_game_data(self, data, transport):
        usr = self.resolve_user(transport)

    def ask_for_game_start(self, ready_player: ServerSideUser):
        print(type(pl) for pl in self.connections)
        user_connections = [pl for pl in self.connections if isinstance(pl, ServerSideUser)]
        ready_players = [pl for pl in user_connections if pl.ready]
        if len(ready_players) >= 4:
            ready_players.sort(key=lambda r_pl: r_pl.ready_time)
            game_players = ready_players[:4]
            # Check if the player who started the game is in the game if not this statement adds him
            if ready_player.username not in [pl.username for pl in game_players]:
                try:
                    conn = [con for con in self.connections if con.username == ready_player.username][0]
                    game_players[3] = conn
                except IndexError:
                    pass
            player = []
            for pl in game_players:
                player.append(ServerSidePlayer.from_ServerSideUser(pl, self.database, pl.connection))
                pl.ready = False
            player = [[player[0], player[2]], [player[1], player[3]]]
            Clock.schedule_once(partial(self.game, player))

    def game(self, players: list[list[ServerSidePlayer]], *args):
        game_set = ServerSideSet.new_set(players, self.database)
        Clock.schedule_once(partial(game_set.start_set), 0)

    def on_connection(self, transport):
        print("connect", transport)
        host = transport.getHost()
        btn = Button(text=f"{host.host}:{host.port}", width=100, size_hint=(None, 0.15))
        usr = UnknownUser(transport, btn)
        self.connections.append(usr)
        self.layout.add_widget(btn)
        self.connections.append(usr)
        transport.write(pickle.dumps(Packet("NODE")))

    def on_disconnection(self, transport):
        user = self.resolve_user(transport)
        self.layout.remove_widget(user.btn)
        connection = [trans for trans in self.connections if user.btn == self.connections[0].btn]
        if connection:
            self.connections.pop(self.connections.index(connection[0]))
        print("disconnect", user.connection)

    def resolve_user(self, connection):
        return [usr for usr in self.connections if usr.connection == connection][0]


if __name__ == '__main__':
    WattenServerApp().run()
