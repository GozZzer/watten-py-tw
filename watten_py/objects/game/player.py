from watten_py.objects.database import WattenDatabase
from watten_py.objects.user import User


class Player:
    games_won: int
    set_won: int

    def __init__(self, user: User, database: WattenDatabase = None):
        self.user = user
        self.resolve_data(database)

    def resolve_data(self, database: WattenDatabase):
        _, self.games_won, self.set_won = database.get_player(self.user.user_id)


class ServerSidePlayer(Player):
    dek: list
    game_id: int

    def __init__(self, user: User, database: WattenDatabase = None):
        super().__init__(user, database)

    @classmethod
    def from_player(cls, pl: Player):
        return cls(pl.user)

    def to_player(self, database: WattenDatabase):
        return Player(self.user, database)

    def set_game_id(self, game_id: int):
        self.game_id = game_id