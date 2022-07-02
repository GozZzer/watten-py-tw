import datetime
import uuid

from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.cards import CardBase


class Player:
    games_won: int
    set_won: int
    cards: list[CardBase] = []
    connected_since: datetime.datetime

    def __init__(self, user_id: uuid.UUID, database: WattenDatabase = None):
        self.resolve_data(user_id, database)

    def resolve_data(self, user_id: uuid.UUID, database: WattenDatabase):
        _, self.games_won, self.set_won, self.connected_since = database.get_player(user_id)
