import itertools
import random
import time
from functools import partial

from kivy.clock import Clock

from watten_py.objects.client import Client
from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.player import Player
from watten_py.objects.game.cards import CardDek, CardBase
from watten_py.objects.network import GamePacket, Packet
from watten_py.tools.database import DatabaseAttribute


class Game:
    def __init__(self, game_id: int, player: list[list[Player]], team1_points: list[int], team2_points: list[int], played_cards: list[CardBase]):
        self.game_id = game_id
        self.team1_player: list[Player] = player[0]
        self.team2_player: list[Player] = player[1]
        self.team1_points: list[int] = team1_points
        self.team2_points: list[int] = team2_points
        self.played_cards: list[CardBase] = played_cards
        pass

    def to_sendable_game(self, player: Player):
        sendable_player = []
        all_player = [self.team1_player, self.team2_player]
        for team in all_player:
            lst = []
            for pl in team:
                if pl.player_id == player.player_id:
                    lst.append(player)
                else:
                    lst.append(player.to_not_viewable())
            sendable_player.append(lst)
        return Game(self.game_id, sendable_player, self.team1_points, self.team2_points, self.played_cards)


class ServerSideGame:
    card_dek: CardDek
    curr_round: list[CardBase] = []
    game_player_loop: list[Client] | None = None
    round_winner: int = None
    highest: CardBase = None
    game_winner: list[Client] = []

    def __init__(self, game_id: int, game_num: int, player: list[list[Client]], team1_points: DatabaseAttribute, team2_points: DatabaseAttribute):
        self.game_id = game_id
        self.game_num = game_num
        self.team1_player: list[Client] = player[0]
        self.team2_player: list[Client] = player[1]
        self.team1_points: DatabaseAttribute = team1_points
        self.team2_points: DatabaseAttribute = team2_points
        self.play_card_timeout: int = 10

    @classmethod
    def new_game(cls, game_id: int, player: list[list[Client]], game_num: int, connection):
        return cls(
            game_id,
            game_num,
            player,
            DatabaseAttribute(connection, "GameData", "team1_points", "game_id=%s", game_id),
            DatabaseAttribute(connection, "GameData", "team2_points", "game_id=%s", game_id)
        )

    def is_done(self):
        return True if self.game_winner else False

    def to_Game(self):
        player = [[cl.player for cl in self.team1_player], [cl.player for cl in self.team2_player]]
        return Game(self.game_id, player, self.team1_points.get(), self.team2_points.get(), self.curr_round)

    def next_round(self, exec_after=None):
        if sum(self.team1_points.get()) >= 11:
            self.send_to_game(GamePacket("GAMEDONE", self.game_id, winner="team1"))
            self.game_winner = self.team1_player
            for cl in self.game_player_loop:
                cl.add_acceptable_game("NEXTGAME")
        elif sum(self.team2_points.get()) >= 11:
            self.send_to_game(GamePacket("GAMEDONE", self.game_id, winner="team2"))
            self.game_winner = self.team2_player
            for cl in self.game_player_loop:
                cl.add_acceptable_game("NEXTGAME")
        else:
            self.card_dek = CardDek.get_mixed_dek()
            self.update_game_player_loop()
            for card_amount in [3, 2]:
                for client in self.game_player_loop:
                    cards = self.card_dek.deal_top_card(card_amount)
                    client.player.cards = client.player.cards + cards
                    cards = None
            self.highest = CardBase.new_card(self.game_player_loop[0].player.cards[0].num(), self.game_player_loop[3].player.cards[0].col())
            try:
                print(self.highest)
            except IndexError: #########################################################################################################sadfasdf
                pass
            self.send_to_game(GamePacket("ROUNDSTART", self.game_id, game=self.to_Game(), highest=self.highest))
            Clock.schedule_once(partial(self.next_player, self.game_player_loop[0]), 2)

    def next_player(self, client: Client, exec_after=None):
        possible = self.get_possible_cards(client)
        self.send_to(client, GamePacket("TURN", self.game_id, possible=possible))
        client.add_acceptable_game("TURN_C")

    def decide_round_winner(self, exec_after):
        self.round_winner = 0
        for card in self.curr_round[1:]:
            # Card is the highest card
            if card == self.highest and card.num() == self.highest.num():
                self.round_winner = self.curr_round.index(card)
                return
            # Card is the highest number and before round_winner is not the highest number
            if card.num() == self.highest.num() and self.curr_round[self.round_winner].num() != self.highest.num():
                self.round_winner = self.curr_round.index(card)
            # Card is not the highest number
            else:
                # Card is the same color as the first card and the first card was the highest color
                if card == self.curr_round[0] and card == self.highest:
                    if card > self.curr_round[self.round_winner]:
                        self.round_winner = self.curr_round.index(card)
                # card color is matching with the color of the first played card
                elif card == self.curr_round[0]:
                    if card > self.curr_round[self.round_winner]:
                        self.round_winner = self.curr_round.index(card)
                # Card Color is the highest color
                elif card == self.highest:
                    self.round_winner = self.curr_round.index(card)
                # Card is a random card
                else:
                    pass
        self.round_winner = self.round_winner % 4
        self.add_points()
        self.curr_round = []
        Clock.schedule_once(self.next_round)

    def add_points(self):
        round_winner = self.game_player_loop[self.round_winner]
        if round_winner in self.team1_player:
            self.team1_points.append(2)
        elif round_winner in self.team2_player:
            self.team2_points.append(2)

    def get_possible_cards(self, cl: Client) -> list[CardBase]:
        cards = cl.player.cards
        if cl in [self.game_player_loop[0], self.game_player_loop[3]]:
            if not self.curr_round:
                return cards
            if self.highest == self.curr_round[0]:
                cds = [c for c in cards if c == self.highest]
                return cds if cds is not None else cards
            else:
                return cards
        else:
            return cards

    def schenere(self):
        self.game_player_loop[0].player.cards = []
        self.game_player_loop[3].player.cards = []
        for card_amount in [3, 2]:
            for client in [self.game_player_loop[0], self.game_player_loop[3]]:
                cards = self.card_dek.deal_top_card(card_amount)
                client.player.cards = client.player.cards + cards
                cards = None

    def update_game_player_loop(self):
        if not self.game_player_loop:
            self.game_player_loop = [self.team1_player[0], self.team2_player[0], self.team1_player[1], self.team2_player[1]]
        else:
            if self.round_winner:
                self.game_player_loop = self.game_player_loop[:self.round_winner] + self.game_player_loop[self.round_winner:]
        self.game_player_loop = self.game_player_loop[:self.game_num-1] + self.game_player_loop[self.game_num-1:]

    def send_to_game(self, packet: Packet | GamePacket):
        for cl in self.team1_player + self.team2_player:
            self.send_to(cl, packet)

    @staticmethod
    def send_to(client: Client, packet: Packet | GamePacket):
        """if "game" in packet.data.keys():
            sendable = packet.data["game"].to_sendable_game(client.player)
            packet.data["game"]: Game = sendable
            kwargs = packet.data
            del kwargs["game"]
            client.send(GamePacket(packet.task_type, packet.game_id, game=sendable, **kwargs))
        else:
            client.send(packet)"""
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
        game = ServerSideGame.new_game(game_id, player, 1, database.connection)
        return cls(
            set_id,
            player,
            game,
            DatabaseAttribute(database.connection, "SetData", "team1_set_points", "set_id=%s", set_id),
            DatabaseAttribute(database.connection, "SetData", "team2_set_points", "set_id=%s", set_id)
        )

    def start_game(self, exec_after=None):
        Clock.schedule_once(self.games[-1].next_round)

    def handle_data(self, data: GamePacket, client: Client, db: WattenDatabase, exec_after=None):
        if data.task_type not in client.get_acceptable_game():
            return
        player = client.player
        match data.task_type:
            case "TURN_C":
                if client not in self.games[-1].game_player_loop:
                    return
                if data.data["card"] in player.cards:
                    player.current_acceptable.pop(player.current_acceptable.index("TURN_C"))
                    player.cards.pop(player.cards.index(data.data["card"]))
                    self.games[-1].curr_round.append(data.data["card"])
                    self.games[-1].send_to_game(GamePacket("UPD_G", self.games[-1].game_id, game=self.games[-1].to_Game()))
                    cur_index = self.games[-1].game_player_loop.index(client)
                    if cur_index == 3:
                        Clock.schedule_once(self.games[-1].decide_round_winner)
                    else:
                        Clock.schedule_once(partial(self.games[-1].next_player, self.games[-1].game_player_loop[cur_index + 1]), 2)
                else:
                    Clock.schedule_once(partial(self.games[-1].next_player, client), 2)
            case "NEXTGAME":
                if self.games[-1].is_done():
                    db.client_won_game(*[cl.user.user_id for cl in self.games[-1].game_winner])
                    if self.games[-1].game_winner == self.games[-1].team1_player:
                        self.team1_set_points.append(1)
                    elif self.games[-1].game_winner == self.games[-1].team2_player:
                        self.team1_set_points.append(1)
                    for cl in self.games[-1].game_player_loop:
                        cl.player.current_acceptable.pop(cl.player.current_acceptable.index("NEXTGAME"))
                    game_id = db.new_game(self.set_id)
                    game = ServerSideGame.new_game(game_id, [self.team1, self.team2], len(self.games), db.connection)
                    self.games.append(game)
                    self.start_game()

    def close_set(self):
        self.games[-1].send_to_game(GamePacket("GAMEDONE"))

    def send_to_set(self, packet: Packet | GamePacket):
        for cl in self.team1 + self.team2:
            self.send_to(cl, packet)

    @staticmethod
    def send_to(client: Client, packet: Packet | GamePacket):
        client.send(packet)
