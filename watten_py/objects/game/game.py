from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.player import Player, ServerSidePlayer
from watten_py.objects.game.cards import Card
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
    def __init__(self, set_id: int, player: list[list[ServerSidePlayer]], first_game: ServerSideGame, team1_set_points: DatabaseAttribute, team2_set_points: DatabaseAttribute):
        self.set_id = set_id
        self.team1_set_points = team1_set_points
        self.team2_set_points = team2_set_points
        self.team1 = player[0]
        self.team2 = player[1]
        self.games = [first_game]

    @classmethod
    def new_set(cls, player:list[list[ServerSidePlayer]], database: WattenDatabase):
        set_id, game_id = database.new_set([list(map(lambda x: x.user_id, team)) for team in player])
        game = ServerSideGame.new_game(game_id, database.connection)
        return cls(
            set_id,
            player,
            game,
            DatabaseAttribute(database.connection, "SetData", "team1_set_points", "set_id=%s", set_id),
            DatabaseAttribute(database.connection, "SetData", "team2_set_points", "set_id=%s", set_id)
        )
