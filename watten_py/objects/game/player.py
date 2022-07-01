from watten_py.objects.database import WattenDatabase
from watten_py.objects.user import User, ServerSideUser
from watten_py.objects.game.cards import Card


class Player:
    games_won: int
    set_won: int
    cards: list[Card]

    def __init__(self, user: User, database: WattenDatabase = None):
        self._user: User = user
        self.resolve_data(database)

    def resolve_data(self, database: WattenDatabase):
        _, self.games_won, self.set_won = database.get_player(self._user.user_id)


class ServerSidePlayer(Player):
    dek: list[Card]
    game_id: int

    def __init__(self, user: ServerSideUser, database: WattenDatabase = None, connection=None):
        self.user: ServerSideUser = user
        self.connection = connection
        super().__init__(user.to_User(), database)

    @classmethod
    def from_player(cls, pl: Player, connection, btn):
        return cls(ServerSideUser.from_User(pl._user, connection, btn))

    def to_player(self, database: WattenDatabase):
        return Player(self.user, database)

    @classmethod
    def from_ServerSideUser(cls, user: ServerSideUser, database: WattenDatabase, connection):
        return cls(user, database, connection)

    def set_game_id(self, game_id: int):
        self.game_id = game_id
