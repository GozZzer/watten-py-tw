from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.stacklayout import StackLayout
from kivy.logger import Logger

from twisted.internet import reactor
from twisted.internet.tcp import Server

from watten_py.objects.game.game import ServerSideSet
from watten_py.objects.client import Client
from watten_py.objects.network import Packet, GamePacket, UserUpdatePacket
from watten_py.objects.database import WattenDatabase
from watten_py.watten_tw import sr_reactor, TwistedServerFactory


class WattenServerApp(App):
    """
    The Server App which includes all the needed modules and functions to run the Watten-Py Server
    Attributes:
        - layout: StackLayout
            Just a basic Layout to display all the current connections
        - factory: TwistedServerFactory
            The factory where all the connections are connected to
        - database: WattenDatabase
            The database to get/save all the important data
        - reactor: reactor
            The reactor to manage all the connections
        - connections: list[Client]
            A list oh all current connections
        - sets: list[ServerSideSet]
            A list of all current sets
    """
    layout: StackLayout
    factory: TwistedServerFactory
    database: WattenDatabase
    reactor: reactor
    connections: list[Client] = []
    sets: list[ServerSideSet] = []

    def build(self):
        """
        Build the App
        By building the app several steps are performed
          1. Connect to the Database
          2. Listen to incoming connections
                - Port: 5643
                - Protocol: TCP

        Return: StackLayout
            The layout the app should display
        """
        self.layout = StackLayout()
        self.database = WattenDatabase()
        Logger.info("Database: Server is connected to the Database")
        self.factory = TwistedServerFactory(self)
        self.reactor = sr_reactor
        self.reactor.listenTCP(5643, self.factory)
        Logger.info("Network: Reactor is listening to port 5643 (TCP)")
        return self.layout

    def stop(self, *args):
        """
        Stopp The App
        By stopping the app several steps are performed:
          1. Logout every client
          2. Disconnect from the database
          3. Stop The App

        Return: None
        """
        for cl in self.connections:
            cl.logout(self.database)
        self.database.stop_connection()
        super().stop(*args)

    def handle_data(self, data: Packet, connection: Server):
        """
        Handles data from incoming connections
        Only instances of the type -> >>>Packet<<< are handled

        Arguments:
            - data: Packet
                The Packet which includes:
                 - task_type: str (According to this type the data gets handled different)
                 - data: dict (Additional data the Server needs from the client)
            - connection:
                The Connection (TwistedServerProtocol) to send/receive data from a client

        Return: None
        """
        # Get the client according to the connection
        client = self.resolve_client(connection)
        # match the packet to the task_type
        match data.task_type:
            # The Player is ready to play a game -> The server checks if it is possible to start a game (self.ask_for_game_start())
            case "READY":
                if client.ready(self.database):
                    Clock.schedule_once(partial(self.ask_for_game_start, client), 0)

        # print(data)

    def handle_user_update(self, data: UserUpdatePacket, connection: Server):
        """
        Handles data from incoming connections
        Only instances of the type -> >>>UserUpdatePacket<<< are handled

        This function directly calls the on_user_update() function of the client which sent the update request

        Arguments:
            - data: UserUpdatePacket
                The Packet which includes:
                 - task_type: str (According to this type the data gets handled different)
                 - data: dict (Additional data the Server needs from the client)
            - connection:
                The Connection (TwistedServerProtocol) to send/receive data from a client

        Return: None
        """
        # Get the client according to the connection
        client = self.resolve_client(connection)
        client.on_user_update(data, self.database)

    def handle_game_data(self, data: GamePacket, connection: Server):
        """
        Handles data from incoming connections
        Only instances of the type -> >>>GamePacket<<< are handled

        This function directly calls the on_user_update() function of the client which sent the update request

        Arguments:
            - data: UserUpdatePacket
                The Packet which includes:
                 - task_type: str (According to this type the data gets handled different)
                 - data: dict (Additional data the Server needs from the client)
            - game_id: int
                The ID of the game the player currently plays
            - connection:
                The Connection (TwistedServerProtocol) to send/receive data from a client

        Return: None
        """
        # Get the client according to the connection
        client = self.resolve_client(connection)
        playing_set = self.resolve_set(data)
        playing_game = playing_set.games[-1]
        Clock.schedule_once(partial(playing_set.handle_data, data, client, self.database))

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

    def game(self, players: list[list[Client]],  exec_after):
        game_set = ServerSideSet.new_set(players, self.database)
        self.sets.append(game_set)
        Clock.schedule_once(partial(game_set.start_game), 0)

    def on_connection(self, connection: Server):
        addr = connection.getHost()
        Logger.info(f"Connection: Connected [{addr.type}] Client: {addr.host}:{addr.port}")
        clnt, btn = Client.on_connection(connection)
        self.layout.add_widget(btn)
        self.connections.append(clnt)
        clnt.send(Packet("NODE"))

    def on_disconnection(self, connection: Server):
        client = self.resolve_client(connection)
        s = self.resolve_set(client=client)
        s.close_set()
        client.logout(self.database)
        self.layout.remove_widget(client.btn)
        conn = [trans for trans in self.connections if client.btn == self.connections[0].btn]
        if conn:
            self.connections.pop(self.connections.index(conn[0]))
        addr = conn[0].address
        Logger.info(f"Connection: Disconnected [{addr.type}] Client: {addr.host}:{addr.port}")

    def resolve_client(self, connection: Server):
        return [cli for cli in self.connections if cli.connection == connection][0]

    def resolve_set(self, data: GamePacket = None, client: Client = None):
        if data:
            if data.game_id is not None:
                return [playing_set for playing_set in self.sets if data.game_id in [g.game_id for g in playing_set.games]][0]
        elif client:
            if client.player:
                return [sett for sett in self.sets if client in [sett.team1 + sett.team2]][0]




if __name__ == '__main__':
    WattenServerApp().run()
