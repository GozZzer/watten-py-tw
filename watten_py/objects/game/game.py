import pickle

from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.player import Player, ServerSidePlayer
from watten_py.objects.game.cards import Card
from watten_py.objects.network import GamePacket, Packet
from watten_py.tools.database import DatabaseAttribute


class Game:
    team1_points: list[int] = []
    team2_points: list[int] = []

    def __init__(self, game_id: int, player: list[Player], own_cards: list[Card]):
        self.game_id = game_id
        self.player = player
        self.own_cards = own_cards
        pass


class ServerSideGame:
    card_dek: list[Card]
    player_dek: list[list[Card]]

    def __init__(self, game_id: int, team1_points: DatabaseAttribute, team2_points: DatabaseAttribute):
        self.game_id = game_id
        self.team1_points = team1_points
        self.team2_points = team2_points

    @classmethod
    def new_game(cls, game_id: int, connection):
        return cls(
            game_id,
            DatabaseAttribute(connection, "GameData", "team1_points", "game_id=%s", game_id),
            DatabaseAttribute(connection, "GameData", "team2_points", "game_id=%s", game_id)
        )


class ServerSideSet:
    continue_set: bool = True

    def __init__(self, set_id: int, player: list[list[ServerSidePlayer]], first_game: ServerSideGame, team1_set_points: DatabaseAttribute, team2_set_points: DatabaseAttribute):
        self.set_id = set_id
        self.team1_set_points: DatabaseAttribute = team1_set_points
        self.team2_set_points: DatabaseAttribute = team2_set_points
        self.team1: list[ServerSidePlayer] = player[0]
        self.team2: list[ServerSidePlayer] = player[1]
        self.games = [first_game]

    def __repr__(self):
        return f"<ServerSideSet #{self.set_id} games={len(self.games)}>"

    @classmethod
    def new_set(cls, player: list[list[ServerSidePlayer]], database: WattenDatabase):
        set_id, game_id = database.new_set([list(map(lambda x: x.user.user_id, team)) for team in player])
        game = ServerSideGame.new_game(game_id, database.connection)
        return cls(
            set_id,
            player,
            game,
            DatabaseAttribute(database.connection, "SetData", "team1_set_points", "set_id=%s", set_id),
            DatabaseAttribute(database.connection, "SetData", "team2_set_points", "set_id=%s", set_id)
        )

    def start_set(self, *args):
        while self.continue_set:
            self.send_to_set(Packet("GAMESTART", game=self.games[-1]))

    def send_to_set(self, packet: Packet | GamePacket):
        for pl in self.team1:
            self.send_to(pl.user.connection, packet)

        for pl in self.team2:
            self.send_to(pl.user.connection, packet)

    @staticmethod
    def send_to(connection, packet: Packet | GamePacket):
        connection.write(pickle.dumps(packet))
