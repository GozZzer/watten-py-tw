import datetime
import pickle
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

from watten_py.objects.game.game import ServerSideSet
from watten_py.objects.game.player import ServerSidePlayer
from watten_py.objects.client import Client
from watten_py.objects.user import User
from watten_py.objects.network import Packet, UserUpdatePacket
from watten_py.objects.database import WattenDatabase
from watten_py.watten_tw import sr_reactor, TwistedServerFactory


class WattenServerApp(App):
    layout: StackLayout
    factory: TwistedServerFactory
    database: WattenDatabase
    connections: list[Client] = []

    def build(self):
        self.layout = StackLayout()
        self.database = WattenDatabase()
        self.factory = TwistedServerFactory(self)
        sr_reactor.listenTCP(5643, self.factory)
        return self.layout

    def stop(self, *args):
        for cl in self.connections:
            cl.logout(self.database)
        self.database.stop_connection()
        super().stop(*args)

    def handle_data(self, data, transport):
        client = self.resolve_client(transport)
        match data.task_type:
            case "READY":
                if client.ready(self.database):
                    Clock.schedule_once(partial(self.ask_for_game_start, client), 0)

        # print(data)

    def handle_user_update(self, data, transport):
        client = self.resolve_client(transport)
        client.on_user_update(data, self.database)

    def handle_game_data(self, data, transport):
        client = self.resolve_client(transport)

    def ask_for_game_start(self, ready_player: Client, exec_after):
        ready_clients = [cl for cl in self.connections if cl.player is not None]
        if len(ready_clients) >= 4:
            ready_clients.sort(key=lambda r_cl: r_cl.player.connected_since)
            game_players = ready_clients[:4]
            # Check if the player who started the game is in the game if not this statement adds him
            if ready_player not in ready_clients:
                try:
                    game_players[3] = ready_player
                except IndexError:
                    pass
            player = [[game_players[0], game_players[2]], [game_players[1], game_players[3]]]
            Clock.schedule_once(partial(self.game, player))

    def game(self, players: list[list[Client]], exec_after):
        game_set = ServerSideSet.new_set(players, self.database)
        Clock.schedule_once(partial(game_set.start_set), 0)

    def on_connection(self, transport):
        print("connect", transport)
        clnt, btn = Client.on_connection(transport)
        self.layout.add_widget(btn)
        self.connections.append(clnt)
        clnt.send(Packet("NODE"))

    def on_disconnection(self, transport):
        client = self.resolve_client(transport)
        client.logout(self.database)
        self.layout.remove_widget(client.btn)
        connection = [trans for trans in self.connections if client.btn == self.connections[0].btn]
        if connection:
            self.connections.pop(self.connections.index(connection[0]))
        print("disconnect", client.connection)

    def resolve_client(self, connection):
        return [cli for cli in self.connections if cli.connection == connection][0]


if __name__ == '__main__':
    WattenServerApp().run()
