import itertools

from watten_py.objects.client import Client
from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.player import Player
from watten_py.objects.game.cards import CardDek, CardBase
from watten_py.objects.network import GamePacket, Packet
from watten_py.tools.database import DatabaseAttribute


class Game:
    team1_points: list[int] = []
    team2_points: list[int] = []

    def __init__(self, game_id: int, player: list[list[Player]]):
        self.game_id = game_id
        self.team1_player: list[Player] = player[0]
        self.team2_player: list[Player] = player[1]
        pass


class ServerSideGame:
    card_dek: CardDek
    game_player_loop: list[Client] | None = None
    round_winner: int

    def __init__(self, game_id: int, player: list[list[Client]], team1_points: DatabaseAttribute, team2_points: DatabaseAttribute):
        self.game_id = game_id
        self.team1_player: list[Client] = player[0]
        self.team2_player: list[Client] = player[1]
        self.team1_points: DatabaseAttribute = team1_points
        self.team2_points: DatabaseAttribute = team2_points

    @classmethod
    def new_game(cls, game_id: int, player: list[list[Client]], connection):
        return cls(
            game_id,
            player,
            DatabaseAttribute(connection, "GameData", "team1_points", "game_id=%s", game_id),
            DatabaseAttribute(connection, "GameData", "team2_points", "game_id=%s", game_id)
        )

    def to_Game(self):
        player = [[cl.player for cl in self.team1_player], [cl.player for cl in self.team2_player]]
        return Game(self.game_id, player)

    def start(self):
        self.card_dek = CardDek.get_mixed_dek()
        self.update_game_player_loop()
        print(self.game_player_loop)
        for card_amount in [3, 2]:
            for client in self.game_player_loop:
                cards = self.card_dek.deal_top_card(card_amount)
                print(cards)
                client.player.cards.append(cards)
        for cl in self.game_player_loop:
            print(cl.player.cards)
        self.send_to_game(GamePacket("GAMESTART", game=self.to_Game()))

    def start_round(self):
        pass

    def update_game_player_loop(self):
        if not self.game_player_loop:
            self.game_player_loop = [self.team1_player[0], self.team2_player[0], self.team1_player[1], self.team2_player[1]]
        else:
            self.game_player_loop = self.game_player_loop[:self.round_winner] + self.game_player_loop[self.round_winner:]

    def send_to_game(self, packet: Packet | GamePacket):
        for cl in self.team1_player + self.team2_player:
            self.send_to(cl, packet)

    @staticmethod
    def send_to(client: Client, packet: Packet | GamePacket):
        if "game" in packet.data.keys():
            game: Game = packet.data["game"]
            for pl in game.team1_player + game.team2_player:
                if pl != client.player:
                    pl.cards = list(itertools.repeat(CardBase(-1), len(pl.cards)))
        else:
            client.send(packet)


class ServerSideSet:
    continue_set: bool = True

    def __init__(self, set_id: int, player: list[list[Client]], first_game: ServerSideGame, team1_set_points: DatabaseAttribute, team2_set_points: DatabaseAttribute):
        self.set_id = set_id
        self.team1_set_points: DatabaseAttribute = team1_set_points
        self.team2_set_points: DatabaseAttribute = team2_set_points
        self.team1: list[Client] = player[0]
        self.team2: list[Client] = player[1]
        self.games = [first_game]

    def __repr__(self):
        return f"<ServerSideSet #{self.set_id} games={len(self.games)}>"

    @classmethod
    def new_set(cls, player: list[list[Client]], database: WattenDatabase):
        set_id, game_id = database.new_set([list(map(lambda x: x.user.user_id, team)) for team in player])
        game = ServerSideGame.new_game(game_id, player, database.connection)
        return cls(
            set_id,
            player,
            game,
            DatabaseAttribute(database.connection, "SetData", "team1_set_points", "set_id=%s", set_id),
            DatabaseAttribute(database.connection, "SetData", "team2_set_points", "set_id=%s", set_id)
        )

    def start_set(self, exec_after):
        while self.continue_set:
            self.games[-1].start()

    def send_to_set(self, packet: Packet | GamePacket):
        for cl in self.team1 + self.team2:
            self.send_to(cl, packet)

    @staticmethod
    def send_to(client: Client, packet: Packet | GamePacket):
        client.send(packet)
