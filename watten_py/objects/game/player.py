import datetime
import itertools
import uuid

from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.cards import CardBase


class Player:
    games_won: int
    set_won: int
    cards: list[CardBase] = []
    connected_since: datetime.datetime
    current_acceptable: list[str] = []

    def __init__(self, user_id: uuid.UUID, database: WattenDatabase = None):
        self.player_id: uuid.UUID = user_id
        if database:
            self.resolve_data(user_id, database)

    def resolve_data(self, user_id: uuid.UUID, database: WattenDatabase):
        _, self.games_won, self.set_won, self.connected_since = database.get_player(user_id)

    def to_not_viewable(self):
        pl = Player(self.player_id)
        pl.cards = list(itertools.repeat(CardBase(-1), len(self.cards)))
        pl.connected_since = self.connected_since
        pl.games_won = self.games_won
        pl.set_won = self.set_won
        return pl

