import datetime
import uuid

from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.cards import Card


class Player:
    games_won: int
    set_won: int
    cards: list[Card]
    connected_since: datetime.datetime

    def __init__(self, user_id: uuid.UUID, database: WattenDatabase = None):
        self.resolve_data(user_id, database)

    def resolve_data(self, user_id: uuid.UUID, database: WattenDatabase):
        _, self.games_won, self.set_won, self.connected_since = database.get_player(user_id)


class ServerSidePlayer(Player):
    dek: list[Card]
    game_id: int

    def __init__(self, user_id: uuid.UUID, database: WattenDatabase):
        super().__init__(user_id, database)

    def set_game_id(self, game_id: int):
        self.game_id = game_id
